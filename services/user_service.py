import streamlit as st
from repositories import user_repo
from typing import Optional


class UserService:
    @staticmethod
    def get_by_id(user_id: str) -> Optional[dict]:
        return user_repo.get_user_by_id(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        return user_repo.get_user_by_email(email)

    @staticmethod
    def create(user_id: str, email: str, name: str, role: str = "student") -> dict:
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")
        if not email or not email.strip():
            raise ValueError("Email cannot be empty.")
        return user_repo.create_user(user_id, email, name.strip(), role)

    @staticmethod
    def update_profile(user_id: str, name: str, bio: str, current_user: dict) -> dict:
        if current_user.get("id") != user_id and current_user.get("role") != "admin":
            raise PermissionError("You can only edit your own profile.")
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")
        updated = user_repo.update_user(user_id, {"name": name.strip(), "bio": bio})
        st.cache_data.clear()
        return updated

    @staticmethod
    def get_all(current_user: dict) -> list:
        if current_user.get("role") != "admin":
            raise PermissionError("Admin access required.")
        return user_repo.get_all_users()

    @staticmethod
    def update_role(user_id: str, new_role: str, current_user: dict) -> dict:
        if current_user.get("role") != "admin":
            raise PermissionError("Admin access required.")
        updated = user_repo.update_user(user_id, {"role": new_role})
        st.cache_data.clear()
        return updated
