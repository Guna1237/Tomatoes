import streamlit as st
from repositories import notification_repo
from typing import Optional


class NotificationService:
    @staticmethod
    def get_all(user_id: str) -> list:
        return notification_repo.get_notifications(user_id)

    @staticmethod
    def get_unread_count(user_id: str) -> int:
        return notification_repo.get_unread_count(user_id)

    @staticmethod
    def mark_read(notif_id: str) -> bool:
        result = notification_repo.mark_read(notif_id)
        st.cache_data.clear()
        return result

    @staticmethod
    def mark_all_read(user_id: str) -> bool:
        result = notification_repo.mark_all_read(user_id)
        st.cache_data.clear()
        return result

    @staticmethod
    def clear_all(user_id: str) -> bool:
        result = notification_repo.clear_all(user_id)
        st.cache_data.clear()
        return result

    @staticmethod
    def delete(notif_id: str) -> bool:
        result = notification_repo.delete_notification(notif_id)
        st.cache_data.clear()
        return result

    @staticmethod
    def add(
        user_id: str,
        title: str,
        content: str,
        notif_type: str = "general",
        related_id: Optional[str] = None,
    ) -> None:
        notification_repo.add_notification(
            user_id=user_id,
            title=title,
            content=content,
            notif_type=notif_type,
            related_id=related_id,
        )
        st.cache_data.clear()
