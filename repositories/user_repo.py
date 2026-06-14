import streamlit as st
from database import get_client
from typing import Optional


@st.cache_data(ttl=300)
def get_user_by_id(user_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("users").select("*").eq("id", user_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[user_repo] get_user_by_id error: {e}")
        return None


@st.cache_data(ttl=300)
def get_user_by_email(email: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("users").select("*").eq("email", email).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[user_repo] get_user_by_email error: {e}")
        return None


def create_user(user_id: str, email: str, name: str, role: str = "student") -> dict:
    client = get_client()
    data = {
        "id": user_id,
        "email": email,
        "name": name,
        "role": role,
        "tomato_balance": 0,
        "bio": "",
    }
    result = client.table("users").insert(data).execute()
    return result.data[0] if result.data else {}


def update_user(user_id: str, data: dict) -> dict:
    client = get_client()
    result = client.table("users").update(data).eq("id", user_id).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}


def update_tomato_balance(user_id: str, new_balance: int) -> bool:
    try:
        client = get_client()
        client.table("users").update({"tomato_balance": new_balance}).eq("id", user_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[user_repo] update_tomato_balance error: {e}")
        return False


def get_all_users() -> list:
    try:
        client = get_client()
        result = client.table("users").select("*").execute()
        return result.data or []
    except Exception as e:
        print(f"[user_repo] get_all_users error: {e}")
        return []
