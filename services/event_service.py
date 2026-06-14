import streamlit as st
from repositories import event_repo
from repositories.notification_repo import add_notification
from config import ROLES
from typing import Optional
from datetime import date


class EventService:
    @staticmethod
    def get_all(search: str = "", category: str = "", upcoming_only: bool = False) -> list:
        events = event_repo.get_events(upcoming_only=upcoming_only)
        if search:
            s = search.lower()
            events = [
                e for e in events
                if s in e.get("title", "").lower()
                or s in e.get("description", "").lower()
                or s in e.get("venue", "").lower()
            ]
        if category:
            events = [e for e in events if e.get("category", "") == category]
        return events

    @staticmethod
    def get_by_id(event_id: str) -> Optional[dict]:
        return event_repo.get_event_by_id(event_id)

    @staticmethod
    def create(data: dict, user: dict) -> dict:
        role = user.get("role", "")
        if role not in ("club_admin", "admin"):
            raise PermissionError("Only club admins or admins can create events.")

        title = data.get("title", "").strip()
        venue = data.get("venue", "").strip()
        event_date = data.get("date")
        event_time = data.get("time")
        capacity = data.get("capacity", 0)

        if not title:
            raise ValueError("Event title cannot be empty.")
        if not venue:
            raise ValueError("Event venue cannot be empty.")
        if not event_date:
            raise ValueError("Event date is required.")
        if not event_time:
            raise ValueError("Event time is required.")
        if int(capacity) <= 0:
            raise ValueError("Capacity must be greater than 0.")

        event_date_obj = event_date if isinstance(event_date, date) else date.fromisoformat(str(event_date))
        if event_date_obj < date.today():
            raise ValueError("Event date must be in the future.")

        payload = {
            **data,
            "title": title,
            "venue": venue,
            "organizer_id": user["id"],
            "organizer_name": user.get("name", ""),
            "registered_count": 0,
            "is_active": True,
        }
        new_event = event_repo.create_event(payload)
        st.cache_data.clear()
        return new_event

    @staticmethod
    def update(event_id: str, data: dict, user: dict) -> dict:
        event = event_repo.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found.")
        if user.get("role") != "admin" and event.get("organizer_id") != user.get("id"):
            raise PermissionError("Only the organizer or an admin can edit this event.")
        updated = event_repo.update_event(event_id, data)
        st.cache_data.clear()
        return updated

    @staticmethod
    def delete(event_id: str, user: dict) -> bool:
        event = event_repo.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found.")
        if user.get("role") != "admin" and event.get("organizer_id") != user.get("id"):
            raise PermissionError("Only the organizer or an admin can delete this event.")
        result = event_repo.delete_event(event_id)
        st.cache_data.clear()
        return result

    @staticmethod
    def register(event_id: str, user_id: str) -> tuple:
        if event_repo.is_registered(event_id, user_id):
            return False, "You are already registered for this event."

        event = event_repo.get_event_by_id(event_id)
        if not event:
            return False, "Event not found."
        if not event.get("is_active", True):
            return False, "This event is no longer active."

        capacity = event.get("capacity", 0)
        registered = event.get("registered_count", 0)
        if registered >= capacity:
            return False, "This event is at full capacity."

        success = event_repo.register_user(event_id, user_id)
        if not success:
            return False, "Registration failed. Please try again."

        add_notification(
            user_id=user_id,
            title="Event Registration Confirmed",
            content=f"You have successfully registered for '{event.get('title', 'the event')}'.",
            notif_type="event",
            related_id=event_id,
        )
        st.cache_data.clear()
        return True, "Successfully registered for the event!"

    @staticmethod
    def unregister(event_id: str, user_id: str) -> tuple:
        if not event_repo.is_registered(event_id, user_id):
            return False, "You are not registered for this event."

        event = event_repo.get_event_by_id(event_id)
        success = event_repo.unregister_user(event_id, user_id)
        if not success:
            return False, "Failed to unregister. Please try again."

        add_notification(
            user_id=user_id,
            title="Event Registration Cancelled",
            content=f"You have unregistered from '{event.get('title', 'the event') if event else 'the event'}'.",
            notif_type="event",
            related_id=event_id,
        )
        st.cache_data.clear()
        return True, "Successfully unregistered from the event."

    @staticmethod
    def is_registered(event_id: str, user_id: str) -> bool:
        return event_repo.is_registered(event_id, user_id)

    @staticmethod
    def get_registered_events(user_id: str) -> list:
        return event_repo.get_user_registrations(user_id)
