import streamlit as st

# MUST be the very first Streamlit call
st.set_page_config(
    page_title="CampusConnect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import os
import services
import ui_components
from modules import dashboard, events, announcements, resources, logistics, lost_found, profile
from auth import get_current_session, login, signup, logout

# Ensure modules package exists
os.makedirs(r"c:\Users\notgu\OneDrive\Documents\campus\modules", exist_ok=True)
_init_path = r"c:\Users\notgu\OneDrive\Documents\campus\modules\__init__.py"
if not os.path.exists(_init_path):
    open(_init_path, "a").close()

# ── Inject global styles ──────────────────────────────────────────────────────
ui_components.inject_custom_styles()

# ── Page routing map ──────────────────────────────────────────────────────────
PAGE_MAP = {
    "Dashboard": dashboard.render,
    "Events": events.render,
    "Announcements": announcements.render,
    "Resources": resources.render,
    "Logistics": logistics.render,
    "Lost & Found": lost_found.render,
    "Profile": profile.render,
}

# ── Auth gate ─────────────────────────────────────────────────────────────────
user = get_current_session()

if not user:
    # ── Auth / login page ─────────────────────────────────────────────────────
    _, col_auth, _ = st.columns([3, 4, 3])
    with col_auth:
        st.markdown(
            """
<div style="text-align:center;margin-top:3rem;margin-bottom:2rem;" class="fade-in">
  <h1 style="color:#DD0426;margin:0;font-size:2.4rem;font-weight:800;
      display:flex;align-items:center;justify-content:center;gap:10px;">
    <i data-lucide="graduation-cap" style="width:40px;height:40px;color:#DD0426;"></i>
    CampusConnect
  </h1>
  <p style="color:#9197AE;margin-top:8px;font-size:1rem;">
    The all-in-one campus activity portal.
  </p>
</div>""",
            unsafe_allow_html=True,
        )

        auth_mode = st.radio("", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")

        with st.form("auth_form"):
            email_input = st.text_input("University Email", placeholder="student@university.edu")
            password_input = st.text_input("Password", type="password", placeholder="••••••••")
            if auth_mode == "Create Account":
                name_input = st.text_input("Full Name", placeholder="Jane Doe")
            submitted = st.form_submit_button(
                "Sign In" if auth_mode == "Sign In" else "Create Account",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not email_input or not password_input:
                st.error("Email and password are required.")
            elif auth_mode == "Sign In":
                auth_user, err = login(email_input, password_input)
                if err:
                    st.error(err)
                elif auth_user:
                    st.success(f"Welcome back, {auth_user.get('name', '')}!")
                    st.rerun()
            else:
                if not name_input.strip():
                    st.error("Full name is required for new accounts.")
                else:
                    auth_user, err = signup(email_input, password_input, name_input.strip())
                    if err:
                        st.error(err)
                    elif auth_user:
                        st.success(f"Account created! Welcome, {auth_user.get('name', '')}.")
                        st.rerun()

        # Demo quick-login profiles
        st.markdown(
            """
<div class="premium-card" style="margin-top:1.5rem;border-color:rgba(168,85,247,0.25);">
  <h4 style="margin:0 0 0.5rem 0;color:#A855F7;font-size:0.9rem;text-align:center;
      display:flex;align-items:center;justify-content:center;gap:6px;">
    <i data-lucide="shield-check" style="width:15px;"></i> Demo Profiles
  </h4>
</div>""",
            unsafe_allow_html=True,
        )
        d1, d2, d3 = st.columns(3)
        with d1:
            if st.button("Student", key="demo_student", use_container_width=True):
                demo_user = services.UserService.get_by_email("jane@university.edu")
                if demo_user:
                    st.session_state["user"] = demo_user
                    st.session_state["access_token"] = "demo"
                    st.rerun()
                else:
                    st.warning("Demo user not found.")
        with d2:
            if st.button("Club Admin", key="demo_club", use_container_width=True):
                demo_user = services.UserService.get_by_email("acs@university.edu")
                if demo_user:
                    st.session_state["user"] = demo_user
                    st.session_state["access_token"] = "demo"
                    st.rerun()
                else:
                    st.warning("Demo user not found.")
        with d3:
            if st.button("Admin", key="demo_admin", use_container_width=True):
                demo_user = services.UserService.get_by_email("registrar@university.edu")
                if demo_user:
                    st.session_state["user"] = demo_user
                    st.session_state["access_token"] = "demo"
                    st.rerun()
                else:
                    st.warning("Demo user not found.")

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
    st.stop()

# ── Authenticated app ─────────────────────────────────────────────────────────

# Refresh user data each render cycle
try:
    refreshed = services.UserService.get_by_id(user["id"])
    if refreshed:
        user = refreshed
        st.session_state["user"] = user
except Exception:
    pass

# Current page from query params
try:
    current_page = st.query_params.get("page", "Dashboard")
except AttributeError:
    # Older Streamlit fallback
    qp = st.experimental_get_query_params()
    current_page = qp.get("page", ["Dashboard"])[0]

# Keep session_state in sync
st.session_state["current_page"] = current_page

# ── Render sidebar ────────────────────────────────────────────────────────────
ui_components.render_custom_sidebar(user, current_page)

# ── Handle sign-out ───────────────────────────────────────────────────────────
if current_page == "SignOut":
    logout()
    try:
        st.query_params.clear()
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass
    st.rerun()

# ── Render active page ────────────────────────────────────────────────────────
render_fn = PAGE_MAP.get(current_page, dashboard.render)
try:
    render_fn(user)
except Exception as e:
    st.error(f"Error loading '{current_page}': {e}")
    st.exception(e)

# ── Activate Lucide icons ─────────────────────────────────────────────────────
st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
