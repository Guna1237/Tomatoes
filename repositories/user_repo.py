import streamlit as st
from database import get_client
import local_database
from typing import Optional


@st.cache_data(ttl=300)
def get_user_by_id(user_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("users").select("*").eq("id", user_id).execute()
        if result.data:
            return result.data[0]
        return local_database.one("users", lambda u: u.get("id") == user_id)
    except Exception as e:
        print(f"[user_repo] get_user_by_id error: {e}")
        return local_database.one("users", lambda u: u.get("id") == user_id)


@st.cache_data(ttl=300)
def get_user_by_email(email: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("users").select("*").eq("email", email).execute()
        if result.data:
            return result.data[0]
        return local_database.one("users", lambda u: u.get("email", "").lower() == email.lower())
    except Exception as e:
        print(f"[user_repo] get_user_by_email error: {e}")
        return local_database.one("users", lambda u: u.get("email", "").lower() == email.lower())


def create_user(user_id: str, email: str, name: str, role: str = "student") -> dict:
    data = {
        "id": user_id,
        "email": email,
        "name": name,
        "role": role,
        "tomato_balance": 50,
        "tomatos": 50,
        "bio": "",
    }
    try:
        client = get_client()
        result = client.table("users").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"[user_repo] create_user error: {e}")
        return local_database.insert("users", data)


def update_user(user_id: str, data: dict) -> dict:
    if "tomatos" in data:
        data = {**data, "tomato_balance": data["tomatos"]}
    try:
        client = get_client()
        result = client.table("users").update(data).eq("id", user_id).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else local_database.update("users", user_id, data)
    except Exception as e:
        print(f"[user_repo] update_user error: {e}")
        st.cache_data.clear()
        return local_database.update("users", user_id, data)


def update_tomato_balance(user_id: str, new_balance: int) -> bool:
    try:
        client = get_client()
        result = client.table("users").update({"tomato_balance": new_balance}).eq("id", user_id).execute()
        st.cache_data.clear()
        if result.data:
            return True
        return bool(local_database.update("users", user_id, {"tomato_balance": new_balance, "tomatos": new_balance}))
    except Exception as e:
        print(f"[user_repo] update_tomato_balance error: {e}")
        return bool(local_database.update("users", user_id, {"tomato_balance": new_balance, "tomatos": new_balance}))


def get_all_users() -> list:
    try:
        client = get_client()
        result = client.table("users").select("*").execute()
        return result.data or local_database.all_rows("users")
    except Exception as e:
        print(f"[user_repo] get_all_users error: {e}")
        return local_database.all_rows("users")
