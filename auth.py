"""
CampusConnect – Supabase Auth helpers.

Session state keys used throughout the app:
    st.session_state["user"]          – dict  | None   (public.users row)
    st.session_state["access_token"]  – str   | None
    st.session_state["current_page"]  – str   | None
"""

from __future__ import annotations

import streamlit as st
import hashlib
from typing import Optional

from database import get_client
from config import ROLES
from repositories import user_repo


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _store_session(user_profile: dict, access_token: str) -> None:
    """Persist the authenticated session into Streamlit session state."""
    st.session_state["user"] = user_profile
    st.session_state["access_token"] = access_token


def _clear_session() -> None:
    """Remove all session-state keys related to authentication."""
    for key in ("user", "access_token", "current_page"):
        st.session_state.pop(key, None)


def _hash_password(password: str) -> str:
    return "sha256$" + hashlib.sha256(password.encode("utf-8")).hexdigest()


def _verify_local_password(user: dict, password: str) -> bool:
    stored_hash = user.get("password_hash") or ""
    if stored_hash.startswith("sha256$"):
        return stored_hash == _hash_password(password)
    return bool(user.get("password") and user.get("password") == password)


def _local_login(email: str, password: str) -> tuple[Optional[dict], Optional[str]]:
    profile = user_repo.get_user_by_email(email.strip().lower())
    if profile and _verify_local_password(profile, password):
        _store_session(profile, "local")
        return profile, None
    return None, "Invalid credentials. Please try again."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def login(email: str, password: str) -> tuple[Optional[dict], Optional[str]]:
    """
    Authenticate with Supabase and load the matching public.users profile.

    Returns
    -------
    (user_dict, None)        on success
    (None, error_message)    on failure
    """
    safe_email = email.strip().lower()
    client = get_client()
    try:
        response = client.auth.sign_in_with_password(
            {"email": safe_email, "password": password}
        )
    except Exception:
        return _local_login(safe_email, password)

    if response.user is None or response.session is None:
        return _local_login(safe_email, password)

    access_token: str = response.session.access_token
    user_id: str = response.user.id

    profile = get_user_profile(user_id)
    if profile is None:
        # Profile row may not exist yet (edge case); create a minimal one.
        try:
            insert_data = {
                "id": user_id,
                "email": safe_email,
                "name": response.user.user_metadata.get("name", email.split("@")[0]),
                "role": ROLES["student"],
            }
            result = client.table("users").insert(insert_data).execute()
            profile = result.data[0] if result.data else insert_data
        except Exception as exc:
            return None, f"Could not load user profile: {exc}"

    _store_session(profile, access_token)
    return profile, None


def signup(
    email: str,
    password: str,
    name: str,
    role: str = "student",
) -> tuple[Optional[dict], Optional[str]]:
    """
    Register a new user with Supabase Auth and insert a public.users row.

    The ``role`` parameter is always coerced to ``"student"`` unless the
    calling context has already verified admin privileges – regular sign-up
    never grants elevated roles.

    Returns
    -------
    (user_dict, None)        on success
    (None, error_message)    on failure
    """
    client = get_client()
    safe_role: str = ROLES["student"]  # sign-up never grants admin/club_admin

    try:
        response = client.auth.sign_up(
            {
                "email": email.strip().lower(),
                "password": password,
                "options": {"data": {"name": name.strip()}},
            }
        )
    except Exception as exc:
        return None, str(exc)

    if response.user is None:
        return None, "Sign-up failed. The e-mail address may already be registered."

    user_id: str = response.user.id

    # The DB trigger (handle_new_auth_user) auto-creates the public.users row.
    # Try to read it back; if not ready yet, build a minimal in-memory profile.
    profile: dict = get_user_profile(user_id) or {
        "id": user_id,
        "email": email.strip().lower(),
        "name": name.strip(),
        "role": safe_role,
        "tomato_balance": 50,
        "tomatos": 50,
        "avatar_url": None,
        "bio": None,
        "created_at": None,
    }

    # Store session only when Supabase returns a live session (email
    # confirmation may be required depending on project settings).
    if response.session is not None:
        _store_session(profile, response.session.access_token)

    return profile, None


def logout() -> None:
    """Sign out from Supabase and wipe local session state."""
    try:
        get_client().auth.sign_out()
    except Exception:
        pass  # Always clear local state even if the network call fails.
    finally:
        _clear_session()


def get_current_session() -> Optional[dict]:
    """
    Return the currently authenticated user dict, or ``None`` if the session
    has expired or is absent.

    Attempts a token refresh via Supabase when the local state looks stale.
    """
    user: Optional[dict] = st.session_state.get("user")
    if user is None:
        return None

    # Local/demo mode: bypass Supabase token validation for local profiles.
    if st.session_state.get("access_token") in {"demo", "local"}:
        return user

    # Validate the live session with Supabase.
    try:
        session = get_client().auth.get_session()
        if session is None:
            _clear_session()
            return None
        # Refresh the stored access token in case it was silently rotated.
        st.session_state["access_token"] = session.access_token
        return user
    except Exception:
        _clear_session()
        return None


def reset_password(email: str) -> bool:
    """
    Trigger a password-reset e-mail via Supabase.

    Returns ``True`` on success, ``False`` on failure.
    """
    try:
        get_client().auth.reset_password_email(email.strip().lower())
        return True
    except Exception:
        return False


def refresh_session() -> Optional[dict]:
    """
    Force a token refresh with Supabase and update session state.

    Returns the current user dict on success, ``None`` on failure.
    """
    try:
        response = get_client().auth.refresh_session()
        if response.session is None:
            _clear_session()
            return None
        st.session_state["access_token"] = response.session.access_token
        return st.session_state.get("user")
    except Exception:
        _clear_session()
        return None


def get_user_profile(user_id: str) -> Optional[dict]:
    """
    Fetch a single row from ``public.users`` by primary key.

    Returns the row dict on success, ``None`` if not found or on error.
    """
    try:
        result = (
            get_client()
            .table("users")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        return result.data if result.data else None
    except Exception:
        return None
