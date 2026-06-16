import streamlit as st
from database import get_client
import local_database
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
        if result.data:
            return result.data
        rows = local_database.all_rows("announcements", lambda a: a.get("is_active", True))
        return sorted(rows, key=lambda a: a.get("created_at", ""), reverse=True)
    except Exception as e:
        print(f"[announcement_repo] get_announcements error: {e}")
        rows = local_database.all_rows("announcements", lambda a: a.get("is_active", True))
        return sorted(rows, key=lambda a: a.get("created_at", ""), reverse=True)


def create_announcement(data: dict) -> dict:
    try:
        client = get_client()
        result = client.table("announcements").insert(data).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else local_database.insert("announcements", data)
    except Exception as e:
        print(f"[announcement_repo] create_announcement error: {e}")
        st.cache_data.clear()
        return local_database.insert("announcements", data)


def update_announcement(ann_id: str, data: dict) -> dict:
    try:
        client = get_client()
        result = client.table("announcements").update(data).eq("id", ann_id).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else local_database.update("announcements", ann_id, data)
    except Exception as e:
        print(f"[announcement_repo] update_announcement error: {e}")
        st.cache_data.clear()
        return local_database.update("announcements", ann_id, data)


def delete_announcement(ann_id: str) -> bool:
    try:
        client = get_client()
        client.table("announcements").update({"is_active": False}).eq("id", ann_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[announcement_repo] delete_announcement error: {e}")
        return bool(local_database.update("announcements", ann_id, {"is_active": False}))


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
        if announcements:
            return announcements
        saved = local_database.all_rows("saved_announcements", lambda r: r.get("user_id") == user_id)
        return [
            ann for ann in (
                local_database.one("announcements", lambda a, ann_id=row.get("announcement_id"): a.get("id") == ann_id)
                for row in saved
            )
            if ann and ann.get("is_active", True)
        ]
    except Exception as e:
        print(f"[announcement_repo] get_saved_announcements error: {e}")
        saved = local_database.all_rows("saved_announcements", lambda r: r.get("user_id") == user_id)
        return [
            ann for ann in (
                local_database.one("announcements", lambda a, ann_id=row.get("announcement_id"): a.get("id") == ann_id)
                for row in saved
            )
            if ann and ann.get("is_active", True)
        ]


def save_announcement(user_id: str, ann_id: str) -> bool:
    try:
        client = get_client()
        client.table("saved_announcements").insert({"user_id": user_id, "announcement_id": ann_id}).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[announcement_repo] save_announcement error: {e}")
        exists = local_database.one(
            "saved_announcements",
            lambda r: r.get("user_id") == user_id and r.get("announcement_id") == ann_id,
        )
        if not exists:
            local_database.insert("saved_announcements", {"user_id": user_id, "announcement_id": ann_id})
        return True


def unsave_announcement(user_id: str, ann_id: str) -> bool:
    try:
        client = get_client()
        client.table("saved_announcements").delete().eq("user_id", user_id).eq("announcement_id", ann_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[announcement_repo] unsave_announcement error: {e}")
        return local_database.delete_where(
            "saved_announcements",
            lambda r: r.get("user_id") == user_id and r.get("announcement_id") == ann_id,
        )


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
        if result.data:
            return True
        return bool(local_database.one(
            "saved_announcements",
            lambda r: r.get("user_id") == user_id and r.get("announcement_id") == ann_id,
        ))
    except Exception as e:
        print(f"[announcement_repo] is_saved error: {e}")
        return bool(local_database.one(
            "saved_announcements",
            lambda r: r.get("user_id") == user_id and r.get("announcement_id") == ann_id,
        ))
