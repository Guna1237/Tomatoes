"""
services/__init__.py

Compatibility shim: exposes all service classes at the `services.*` namespace
so that modules using `import services; services.EventService.method()` work
correctly with the new per-module service implementations.
"""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st

# ── Raw service imports ───────────────────────────────────────────────────────
from services.user_service import UserService as _UserService
from services.event_service import EventService as _EventService
from services.announcement_service import AnnouncementService as _AnnService
from services.resource_service import ResourceService as _ResService
from services.logistics_service import LogisticsService as _LogService
from services.lost_found_service import LostFoundService as _LFService
from services.notification_service import NotificationService as _NotifService
from services.tomato_service import TomatoService  # no API changes needed


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tomatos_alias(user: Optional[dict]) -> Optional[dict]:
    """Add legacy 'tomatos' key as alias for 'tomato_balance'."""
    if user and "tomato_balance" in user:
        user = dict(user)
        user.setdefault("tomatos", user["tomato_balance"])
    return user


# ── UserService ───────────────────────────────────────────────────────────────

class UserService:
    @staticmethod
    def get_by_id(user_id: str) -> Optional[dict]:
        return _tomatos_alias(_UserService.get_by_id(user_id))

    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        return _tomatos_alias(_UserService.get_by_email(email))

    @staticmethod
    def update_profile(user_id: str, name: str, bio: str, current_user: dict) -> dict:
        return _UserService.update_profile(user_id, name, bio, current_user)


# ── EventService ──────────────────────────────────────────────────────────────

class EventService:
    @staticmethod
    def get_all(search: str = "", category: str = "", upcoming_only: bool = False) -> list:
        return _EventService.get_all(search=search, category=category, upcoming_only=upcoming_only)

    @staticmethod
    def get_user_events(user_id: str) -> list:
        """Legacy alias for get_registered_events."""
        return _EventService.get_registered_events(user_id)

    @staticmethod
    def is_registered(event_id: str, user_id: str) -> bool:
        return _EventService.is_registered(event_id, user_id)

    @staticmethod
    def register(event_id: str, user_id: str):
        return _EventService.register(event_id, user_id)

    @staticmethod
    def unregister(event_id: str, user_id: str):
        return _EventService.unregister(event_id, user_id)

    @staticmethod
    def create(
        title: str, description: str, banner_url: str,
        date, time, venue: str,
        organizer_id: str, organizer_name: str,
        capacity: int, category: str = "General",
    ) -> dict:
        user = {"id": organizer_id, "name": organizer_name, "role": "club_admin"}
        return _EventService.create(
            {
                "title": title, "description": description, "banner_url": banner_url,
                "date": str(date), "time": str(time), "venue": venue,
                "capacity": capacity, "category": category,
                "organizer_id": organizer_id, "organizer_name": organizer_name,
            },
            user,
        )


# ── AnnouncementService ───────────────────────────────────────────────────────

class AnnouncementService:
    @staticmethod
    def get_all(search: str = "", category: str = "", priority: str = "") -> list:
        return _AnnService.get_all(search=search, category=category, priority=priority)

    @staticmethod
    def get_user_saved(user_id: str) -> list:
        """Legacy alias for get_saved."""
        return _AnnService.get_saved(user_id)

    @staticmethod
    def is_saved(user_id: str, ann_id: str) -> bool:
        return _AnnService.is_saved(user_id, ann_id)

    @staticmethod
    def save(user_id: str, ann_id: str) -> bool:
        return _AnnService.save(user_id, ann_id)

    @staticmethod
    def unsave(user_id: str, ann_id: str) -> bool:
        return _AnnService.unsave(user_id, ann_id)

    @staticmethod
    def create(
        title: str, content: str, category: str,
        priority: str, author: str, author_id: Optional[str] = None,
    ) -> dict:
        user = {"id": author_id, "name": author, "role": "club_admin"}
        return _AnnService.create(
            {
                "title": title, "content": content,
                "category": category, "priority": priority,
                "author_name": author, "author_id": author_id,
            },
            user,
        )


# ── ResourceService ───────────────────────────────────────────────────────────

class ResourceService:
    @staticmethod
    def get_all(search: str = "", category: str = "", course: str = "") -> list:
        return _ResService.get_all(search=search, category=category, course=course)

    @staticmethod
    def is_bookmarked(user_id: str, resource_id: str) -> bool:
        return _ResService.is_bookmarked(user_id, resource_id)

    @staticmethod
    def bookmark(user_id: str, resource_id: str) -> bool:
        return _ResService.bookmark(user_id, resource_id)

    @staticmethod
    def unbookmark(user_id: str, resource_id: str) -> bool:
        return _ResService.unbookmark(user_id, resource_id)

    @staticmethod
    def get_user_bookmarked(user_id: str) -> list:
        """Legacy alias for get_bookmarked."""
        return _ResService.get_bookmarked(user_id)

    @staticmethod
    def upload(
        title: str, course_code: str, course_name: str, category: str,
        file_url: str, uploader_id: str, uploader_name: str,
    ) -> dict:
        """Upload from a local file path (modules save locally first)."""
        uploader = {"id": uploader_id, "name": uploader_name}
        if os.path.exists(file_url):
            with open(file_url, "rb") as fh:
                file_bytes = fh.read()
            file_name = os.path.basename(file_url)
            return _ResService.upload(
                title, course_code, course_name, category,
                file_bytes, file_name, uploader,
            )
        # Fallback: store URL directly without uploading to Supabase Storage
        from repositories.resource_repo import create_resource
        return create_resource(
            {
                "title": title, "course_code": course_code.upper(),
                "course_name": course_name, "category": category,
                "file_url": file_url, "file_name": os.path.basename(file_url),
                "uploader_id": uploader_id, "uploader_name": uploader_name,
            }
        )


# ── ParcelService (legacy alias for LogisticsService) ─────────────────────────

class ParcelService:
    @staticmethod
    def get_all() -> list:
        from repositories import logistics_repo
        return logistics_repo.get_all_requests()

    @staticmethod
    def create_request(
        requester_id: str,
        title: str,
        description: str,
        pickup_location: str,
        delivery_location: str,
        tomatoes_offered: int = 5,
    ) -> Optional[dict]:
        user = _UserService.get_by_id(requester_id) or {"id": requester_id, "name": ""}
        req, _err = _LogService.create_request(
            title=title, description=description,
            pickup=pickup_location, delivery=delivery_location,
            tomatoes=tomatoes_offered, user=user,
        )
        return req  # None on failure; module checks truthiness

    @staticmethod
    def accept_request(request_id: str, helper_id: str) -> bool:
        helper = _UserService.get_by_id(helper_id) or {"id": helper_id, "name": ""}
        ok, _ = _LogService.accept_request(request_id, helper)
        return ok

    @staticmethod
    def update_status(request_id: str, new_status: str) -> bool:
        """Update status and handle side-effects (tomatoes, notifications)."""
        from repositories import logistics_repo
        from repositories.notification_repo import add_notification

        req = logistics_repo.get_request_by_id(request_id)
        if not req:
            return False

        logistics_repo.update_request(request_id, {"status": new_status})
        reward = req.get("tomato_reward") or req.get("tomatoes_offered", 0)

        if new_status == "Delivered":
            helper_id = req.get("helper_id")
            if helper_id and reward > 0:
                TomatoService.credit(
                    user_id=helper_id, amount=reward,
                    description=f"Delivery reward: {req.get('title', '')}",
                    txn_type="delivery_reward", related_id=request_id,
                )
            if req.get("requester_id"):
                add_notification(
                    user_id=req["requester_id"],
                    title="Delivery Completed",
                    content=f"Your request '{req.get('title','')}' has been delivered!",
                    notif_type="parcel", related_id=request_id,
                )
        elif new_status == "Cancelled":
            requester_id = req.get("requester_id")
            if requester_id and reward > 0:
                TomatoService.credit(
                    user_id=requester_id, amount=reward,
                    description=f"Refund: cancelled request '{req.get('title', '')}'",
                    txn_type="bonus",
                )

        st.cache_data.clear()
        return True


# ── LostFoundService ──────────────────────────────────────────────────────────

class LostFoundService:
    @staticmethod
    def get_all(item_type: str = "", category: str = "") -> list:
        return _LFService.get_all(item_type=item_type, category=category)

    @staticmethod
    def report(
        title: str, description: str, category: str, item_type: str,
        location: str, image_url: str, reporter_id: str, reporter_name: str,
    ) -> dict:
        user = {"id": reporter_id, "name": reporter_name}
        image_bytes: Optional[bytes] = None
        image_name: Optional[str] = None
        if image_url and os.path.exists(image_url):
            with open(image_url, "rb") as fh:
                image_bytes = fh.read()
            image_name = os.path.basename(image_url)
        return _LFService.report(
            title=title, description=description, category=category,
            item_type=item_type, location=location,
            image_bytes=image_bytes, image_name=image_name,
            user=user,
        )

    @staticmethod
    def update_status(item_id: str, status: str, user_id: Optional[str] = None) -> bool:
        """Directly update status, bypassing per-user validation."""
        from repositories import lost_found_repo
        result = lost_found_repo.update_item(item_id, {"status": status})
        st.cache_data.clear()
        return bool(result)


# ── NotificationService ───────────────────────────────────────────────────────

class NotificationService:
    @staticmethod
    def get_all(user_id: str) -> list:
        return _NotifService.get_all(user_id)

    @staticmethod
    def get_unread_count(user_id: str) -> int:
        return _NotifService.get_unread_count(user_id)

    @staticmethod
    def add(
        user_id: str, title: str, content: str,
        notif_type: str = "general", related_id: Optional[str] = None,
    ) -> None:
        _NotifService.add(user_id, title, content, notif_type, related_id)

    @staticmethod
    def mark_read(notif_id: str) -> bool:
        return _NotifService.mark_read(notif_id)

    @staticmethod
    def clear_all(user_id: str) -> bool:
        return _NotifService.clear_all(user_id)
