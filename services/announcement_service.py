import streamlit as st
from repositories import announcement_repo
from repositories.notification_repo import add_notification
from typing import Optional


class AnnouncementService:
    @staticmethod
    def get_all(search: str = "", category: str = "", priority: str = "") -> list:
        announcements = announcement_repo.get_announcements()
        if search:
            s = search.lower()
            announcements = [
                a for a in announcements
                if s in a.get("title", "").lower()
                or s in a.get("content", "").lower()
            ]
        if category:
            announcements = [a for a in announcements if a.get("category", "") == category]
        if priority:
            announcements = [a for a in announcements if a.get("priority", "") == priority]
        return announcements

    @staticmethod
    def get_by_id(ann_id: str) -> Optional[dict]:
        try:
            from database import get_client
            client = get_client()
            result = client.table("announcements").select("*").eq("id", ann_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"[announcement_service] get_by_id error: {e}")
            return None

    @staticmethod
    def create(data: dict, user: dict) -> dict:
        role = user.get("role", "")
        if role not in ("club_admin", "admin"):
            raise PermissionError("Only club admins or admins can create announcements.")

        title = data.get("title", "").strip()
        content = data.get("content", "").strip()
        if not title:
            raise ValueError("Announcement title cannot be empty.")
        if not content:
            raise ValueError("Announcement content cannot be empty.")

        payload = {
            **data,
            "title": title,
            "content": content,
            "author_id": user["id"],
            "author_name": user.get("name", ""),
            "is_active": True,
        }
        new_ann = announcement_repo.create_announcement(payload)
        st.cache_data.clear()
        return new_ann

    @staticmethod
    def update(ann_id: str, data: dict, user: dict) -> dict:
        ann = AnnouncementService.get_by_id(ann_id)
        if not ann:
            raise ValueError("Announcement not found.")
        if user.get("role") != "admin" and ann.get("author_id") != user.get("id"):
            raise PermissionError("Only the author or an admin can edit this announcement.")

        title = data.get("title", "").strip()
        content = data.get("content", "").strip()
        if not title:
            raise ValueError("Announcement title cannot be empty.")
        if not content:
            raise ValueError("Announcement content cannot be empty.")

        updated = announcement_repo.update_announcement(ann_id, {**data, "title": title, "content": content})
        st.cache_data.clear()
        return updated

    @staticmethod
    def delete(ann_id: str, user: dict) -> bool:
        ann = AnnouncementService.get_by_id(ann_id)
        if not ann:
            raise ValueError("Announcement not found.")
        if user.get("role") != "admin" and ann.get("author_id") != user.get("id"):
            raise PermissionError("Only the author or an admin can delete this announcement.")
        result = announcement_repo.delete_announcement(ann_id)
        st.cache_data.clear()
        return result

    @staticmethod
    def save(user_id: str, ann_id: str) -> bool:
        return announcement_repo.save_announcement(user_id, ann_id)

    @staticmethod
    def unsave(user_id: str, ann_id: str) -> bool:
        return announcement_repo.unsave_announcement(user_id, ann_id)

    @staticmethod
    def is_saved(user_id: str, ann_id: str) -> bool:
        return announcement_repo.is_saved(user_id, ann_id)

    @staticmethod
    def get_saved(user_id: str) -> list:
        return announcement_repo.get_saved_announcements(user_id)
