import streamlit as st
from database import get_client
from typing import Optional
from datetime import date


@st.cache_data(ttl=300)
def get_events(upcoming_only: bool = False) -> list:
    try:
        client = get_client()
        query = client.table("events").select("*").eq("is_active", True).order("date", desc=False)
        if upcoming_only:
            today = date.today().isoformat()
            query = query.gte("date", today)
        result = query.execute()
        return result.data or []
    except Exception as e:
        print(f"[event_repo] get_events error: {e}")
        return []


@st.cache_data(ttl=300)
def get_event_by_id(event_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("events").select("*").eq("id", event_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[event_repo] get_event_by_id error: {e}")
        return None


def create_event(data: dict) -> dict:
    client = get_client()
    result = client.table("events").insert(data).execute()
    return result.data[0] if result.data else {}


def update_event(event_id: str, data: dict) -> dict:
    client = get_client()
    result = client.table("events").update(data).eq("id", event_id).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}


def delete_event(event_id: str) -> bool:
    try:
        client = get_client()
        client.table("events").update({"is_active": False}).eq("id", event_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] delete_event error: {e}")
        return False


def increment_registered_count(event_id: str) -> bool:
    try:
        client = get_client()
        event = get_event_by_id(event_id)
        if not event:
            return False
        current = event.get("registered_count", 0)
        client.table("events").update({"registered_count": current + 1}).eq("id", event_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] increment_registered_count error: {e}")
        return False


def decrement_registered_count(event_id: str) -> bool:
    try:
        client = get_client()
        event = get_event_by_id(event_id)
        if not event:
            return False
        current = event.get("registered_count", 0)
        new_count = max(0, current - 1)
        client.table("events").update({"registered_count": new_count}).eq("id", event_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] decrement_registered_count error: {e}")
        return False


@st.cache_data(ttl=300)
def get_registrations_for_event(event_id: str) -> list:
    try:
        client = get_client()
        result = client.table("event_registrations").select("*").eq("event_id", event_id).execute()
        return result.data or []
    except Exception as e:
        print(f"[event_repo] get_registrations_for_event error: {e}")
        return []


@st.cache_data(ttl=300)
def get_user_registrations(user_id: str) -> list:
    try:
        client = get_client()
        result = (
            client.table("event_registrations")
            .select("event_id, events(*)")
            .eq("user_id", user_id)
            .execute()
        )
        events = []
        for row in result.data or []:
            if row.get("events"):
                events.append(row["events"])
        return events
    except Exception as e:
        print(f"[event_repo] get_user_registrations error: {e}")
        return []


def register_user(event_id: str, user_id: str) -> bool:
    try:
        client = get_client()
        client.table("event_registrations").insert({"event_id": event_id, "user_id": user_id}).execute()
        increment_registered_count(event_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] register_user error: {e}")
        return False


def unregister_user(event_id: str, user_id: str) -> bool:
    try:
        client = get_client()
        client.table("event_registrations").delete().eq("event_id", event_id).eq("user_id", user_id).execute()
        decrement_registered_count(event_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] unregister_user error: {e}")
        return False


def is_registered(event_id: str, user_id: str) -> bool:
    try:
        client = get_client()
        result = (
            client.table("event_registrations")
            .select("event_id")
            .eq("event_id", event_id)
            .eq("user_id", user_id)
            .execute()
        )
        return len(result.data or []) > 0
    except Exception as e:
        print(f"[event_repo] is_registered error: {e}")
        return False
