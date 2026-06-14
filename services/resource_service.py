import streamlit as st
import uuid
import os
from repositories import resource_repo
from database import get_client
from config import STORAGE_BUCKET, MAX_FILE_SIZE_MB, ALLOWED_FILE_TYPES
from typing import Optional


class ResourceService:
    @staticmethod
    def get_all(search: str = "", category: str = "", course: str = "") -> list:
        resources = resource_repo.get_resources()
        if search:
            s = search.lower()
            resources = [
                r for r in resources
                if s in r.get("title", "").lower()
                or s in r.get("course_code", "").lower()
                or s in r.get("course_name", "").lower()
            ]
        if category:
            resources = [r for r in resources if r.get("category", "") == category]
        if course:
            c = course.lower()
            resources = [
                r for r in resources
                if c in r.get("course_code", "").lower()
                or c in r.get("course_name", "").lower()
            ]
        return resources

    @staticmethod
    def upload(
        title: str,
        course_code: str,
        course_name: str,
        category: str,
        file_bytes: bytes,
        file_name: str,
        uploader: dict,
    ) -> dict:
        ext = os.path.splitext(file_name)[1].lower().lstrip(".")
        if ext not in ALLOWED_FILE_TYPES:
            raise ValueError(f"File type '.{ext}' is not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}")

        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(f"File size {size_mb:.1f} MB exceeds the limit of {MAX_FILE_SIZE_MB} MB.")

        if not title or not title.strip():
            raise ValueError("Resource title cannot be empty.")

        unique_name = f"{uuid.uuid4()}_{file_name}"
        storage_path = f"resources/{uploader['id']}/{unique_name}"

        client = get_client()
        client.storage.from_(STORAGE_BUCKET).upload(storage_path, file_bytes)
        public_url_response = client.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
        file_url = public_url_response if isinstance(public_url_response, str) else public_url_response.get("publicURL", "")

        data = {
            "title": title.strip(),
            "course_code": course_code.strip(),
            "course_name": course_name.strip(),
            "category": category,
            "file_url": file_url,
            "file_name": file_name,
            "file_type": ext,
            "file_size_mb": round(size_mb, 2),
            "uploader_id": uploader["id"],
            "uploader_name": uploader.get("name", ""),
            "download_count": 0,
            "bookmark_count": 0,
            "is_active": True,
        }
        new_resource = resource_repo.create_resource(data)
        st.cache_data.clear()
        return new_resource

    @staticmethod
    def get_download_url(resource_id: str, user_id: str) -> str:
        resource = resource_repo.get_resource_by_id(resource_id)
        if not resource:
            raise ValueError("Resource not found.")
        resource_repo.increment_downloads(resource_id)
        st.cache_data.clear()
        return resource.get("file_url", "")

    @staticmethod
    def bookmark(user_id: str, resource_id: str) -> bool:
        return resource_repo.bookmark(user_id, resource_id)

    @staticmethod
    def unbookmark(user_id: str, resource_id: str) -> bool:
        return resource_repo.unbookmark(user_id, resource_id)

    @staticmethod
    def is_bookmarked(user_id: str, resource_id: str) -> bool:
        return resource_repo.is_bookmarked(user_id, resource_id)

    @staticmethod
    def get_bookmarked(user_id: str) -> list:
        return resource_repo.get_bookmarked_resources(user_id)

    @staticmethod
    def delete(resource_id: str, user: dict) -> bool:
        resource = resource_repo.get_resource_by_id(resource_id)
        if not resource:
            raise ValueError("Resource not found.")
        if user.get("role") != "admin" and resource.get("uploader_id") != user.get("id"):
            raise PermissionError("Only the uploader or an admin can delete this resource.")

        file_url = resource.get("file_url", "")
        if file_url:
            try:
                client = get_client()
                uploader_id = resource.get("uploader_id", "")
                file_name = resource.get("file_name", "")
                storage_path = None
                if f"resources/{uploader_id}/" in file_url:
                    path_start = file_url.find(f"resources/{uploader_id}/")
                    storage_path = file_url[path_start:]
                    storage_path = storage_path.split("?")[0]
                if storage_path:
                    client.storage.from_(STORAGE_BUCKET).remove([storage_path])
            except Exception as e:
                print(f"[resource_service] Storage delete error (non-fatal): {e}")

        result = resource_repo.delete_resource(resource_id)
        st.cache_data.clear()
        return result
