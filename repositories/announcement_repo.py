import streamlit as st
from database import get_client
from typing import Optional


@st.cache_data(ttl=300)
def get_announcements() -> list:
    try:
        client = get_client()
        result = (
            client.table("announcements")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[announcement_repo] get_announcements error: {e}")
        return []


def create_announcement(data: dict) -> dict:
    client = get_client()
    result = client.table("announcements").insert(data).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}


def update_announcement(ann_id: str, data: dict) -> dict:
    client = get_client()
    result = client.table("announcements").update(data).eq("id", ann_id).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}


def delete_announcement(ann_id: str) -> bool:
    try:
        client = get_client()
        client.table("announcements").update({"is_active": False}).eq("id", ann_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[announcement_repo] delete_announcement error: {e}")
        return False


@st.cache_data(ttl=300)
def get_saved_announcements(user_id: str) -> list:
    try:
        client = get_client()
        result = (
            client.table("saved_announcements")
            .select("announcement_id, announcements(*)")
            .eq("user_id", user_id)
            .execute()
        )
        announcements = []
        for row in result.data or []:
            if row.get("announcements"):
                announcements.append(row["announcements"])
        return announcements
    except Exception as e:
        print(f"[announcement_repo] get_saved_announcements error: {e}")
        return []


def save_announcement(user_id: str, ann_id: str) -> bool:
    try:
        client = get_client()
        client.table("saved_announcements").insert({"user_id": user_id, "announcement_id": ann_id}).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[announcement_repo] save_announcement error: {e}")
        return False


def unsave_announcement(user_id: str, ann_id: str) -> bool:
    try:
        client = get_client()
        client.table("saved_announcements").delete().eq("user_id", user_id).eq("announcement_id", ann_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[announcement_repo] unsave_announcement error: {e}")
        return False


def is_saved(user_id: str, ann_id: str) -> bool:
    try:
        client = get_client()
        result = (
            client.table("saved_announcements")
            .select("announcement_id")
            .eq("user_id", user_id)
            .eq("announcement_id", ann_id)
            .execute()
        )
        return len(result.data or []) > 0
    except Exception as e:
        print(f"[announcement_repo] is_saved error: {e}")
        return False
