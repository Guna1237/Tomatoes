import streamlit as st
import uuid
import os
from pathlib import Path
from repositories import lost_found_repo
from repositories.notification_repo import add_notification
from database import get_client
from config import STORAGE_BUCKET
from typing import Optional

LOCAL_IMAGE_DIR = Path(__file__).resolve().parent.parent / "uploads" / "lost_found"


def _safe_image_name(image_name: str) -> str:
    return os.path.basename(image_name).replace("\\", "_").replace("/", "_")


class LostFoundService:
    @staticmethod
    def get_all(item_type: str = "", category: str = "") -> list:
        items = lost_found_repo.get_all_items()
        if item_type:
            items = [i for i in items if i.get("item_type", "") == item_type]
        if category:
            items = [i for i in items if i.get("category", "") == category]
        return items

    @staticmethod
    def report(
        title: str,
        description: str,
        category: str,
        item_type: str,
        location: str,
        image_bytes: Optional[bytes],
        image_name: Optional[str],
        user: dict,
    ) -> dict:
        title = title.strip() if title else ""
        location = location.strip() if location else ""

        if not title:
            raise ValueError("Item title cannot be empty.")
        if not location:
            raise ValueError("Location cannot be empty.")
        if not item_type:
            raise ValueError("Item type (Lost/Found) is required.")

        image_url = None
        if image_bytes and image_name:
            safe_image_name = _safe_image_name(image_name)
            unique_name = f"{uuid.uuid4()}_{safe_image_name}"
            try:
                storage_path = f"lost_found/{unique_name}"
                client = get_client()
                client.storage.from_(STORAGE_BUCKET).upload(storage_path, image_bytes)
                public_url_response = client.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
                image_url = (
                    public_url_response
                    if isinstance(public_url_response, str)
                    else public_url_response.get("publicURL", "")
                )
            except Exception as e:
                print(f"[lost_found_service] Image upload error (non-fatal): {e}")
                LOCAL_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
                local_path = LOCAL_IMAGE_DIR / unique_name
                local_path.write_bytes(image_bytes)
                image_url = str(local_path)

        data = {
            "title": title,
            "description": description,
            "category": category,
            "item_type": item_type,
            "location": location,
            "image_url": image_url,
            "reporter_id": user["id"],
            "reporter_name": user.get("name", ""),
            "status": "Open",
            "claimed_by": None,
        }
        new_item = lost_found_repo.create_item(data)
        st.cache_data.clear()
        return new_item

    @staticmethod
    def claim(item_id: str, user: dict) -> tuple:
        item = lost_found_repo.get_item_by_id(item_id)
        if not item:
            return False, "Item not found."
        if item.get("reporter_id") == user.get("id"):
            return False, "You cannot claim your own reported item."
        if item.get("status") != "Open":
            return False, "This item has already been claimed or resolved."

        lost_found_repo.update_item(item_id, {
            "status": "Claimed",
            "claimed_by": user["id"],
        })

        add_notification(
            user_id=item["reporter_id"],
            title="Item Claimed",
            content=f"Your reported item '{item.get('title', '')}' has been claimed by {user.get('name', 'someone')}. Please verify and resolve if correct.",
            notif_type="lost_found",
            related_id=item_id,
        )
        st.cache_data.clear()
        return True, ""

    @staticmethod
    def resolve(item_id: str, user: dict) -> bool:
        item = lost_found_repo.get_item_by_id(item_id)
        if not item:
            raise ValueError("Item not found.")
        if user.get("role") != "admin" and item.get("reporter_id") != user.get("id"):
            raise PermissionError("Only the reporter or an admin can resolve this item.")

        lost_found_repo.update_item(item_id, {"status": "Resolved"})
        st.cache_data.clear()
        return True
