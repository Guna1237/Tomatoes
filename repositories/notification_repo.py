import streamlit as st
from database import get_client
from typing import Optional


@st.cache_data(ttl=30)
def get_notifications(user_id: str) -> list:
    try:
        client = get_client()
        result = (
            client.table("notifications")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[notification_repo] get_notifications error: {e}")
        return []


@st.cache_data(ttl=30)
def get_unread_count(user_id: str) -> int:
    try:
        client = get_client()
        result = (
            client.table("notifications")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("read", False)
            .execute()
        )
        return result.count or 0
    except Exception as e:
        print(f"[notification_repo] get_unread_count error: {e}")
        return 0


def add_notification(
    user_id: str,
    title: str,
    content: str,
    notif_type: str = "general",
    related_id: Optional[str] = None,
) -> dict:
    try:
        client = get_client()
        data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "notification_type": notif_type,
            "read": False,
        }
        if related_id:
            data["related_id"] = related_id
        result = client.table("notifications").insert(data).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"[notification_repo] add_notification error: {e}")
        return {}


def mark_read(notif_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").update({"read": True}).eq("id", notif_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] mark_read error: {e}")
        return False


def mark_all_read(user_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").update({"read": True}).eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] mark_all_read error: {e}")
        return False


def delete_notification(notif_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").delete().eq("id", notif_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] delete_notification error: {e}")
        return False


def clear_all(user_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").delete().eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] clear_all error: {e}")
        return False
