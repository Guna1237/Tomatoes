import streamlit as st
from database import get_client
import local_database
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
        rows = local_database.all_rows("notifications", lambda n: n.get("user_id") == user_id)
        return sorted(rows, key=lambda n: n.get("created_at", ""), reverse=True)[:50]


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
        return len(local_database.all_rows(
            "notifications",
            lambda n: n.get("user_id") == user_id and not n.get("read", False),
        ))


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
        return result.data[0] if result.data else local_database.insert("notifications", data)
    except Exception as e:
        print(f"[notification_repo] add_notification error: {e}")
        return local_database.insert("notifications", data)


def mark_read(notif_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").update({"read": True}).eq("id", notif_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] mark_read error: {e}")
        return bool(local_database.update("notifications", notif_id, {"read": True}))


def mark_all_read(user_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").update({"read": True}).eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] mark_all_read error: {e}")
        updated = False
        for notif in local_database.all_rows("notifications", lambda n: n.get("user_id") == user_id):
            updated = bool(local_database.update("notifications", notif["id"], {"read": True})) or updated
        return updated


def delete_notification(notif_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").delete().eq("id", notif_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] delete_notification error: {e}")
        return local_database.delete_where("notifications", lambda n: n.get("id") == notif_id)


def clear_all(user_id: str) -> bool:
    try:
        client = get_client()
        client.table("notifications").delete().eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[notification_repo] clear_all error: {e}")
        return local_database.delete_where("notifications", lambda n: n.get("user_id") == user_id)
