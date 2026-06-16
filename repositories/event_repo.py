import streamlit as st
from database import get_client
import local_database
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
        if result.data:
            return result.data
        rows = local_database.all_rows("events", lambda e: e.get("is_active", True))
        if upcoming_only:
            today = date.today().isoformat()
            rows = [row for row in rows if str(row.get("date", "")) >= today]
        return sorted(rows, key=lambda e: e.get("date", ""))
    except Exception as e:
        print(f"[event_repo] get_events error: {e}")
        rows = local_database.all_rows("events", lambda e: e.get("is_active", True))
        if upcoming_only:
            today = date.today().isoformat()
            rows = [row for row in rows if str(row.get("date", "")) >= today]
        return sorted(rows, key=lambda e: e.get("date", ""))


@st.cache_data(ttl=300)
def get_event_by_id(event_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("events").select("*").eq("id", event_id).execute()
        if result.data:
            return result.data[0]
        return local_database.one("events", lambda e: e.get("id") == event_id)
    except Exception as e:
        print(f"[event_repo] get_event_by_id error: {e}")
        return local_database.one("events", lambda e: e.get("id") == event_id)


def create_event(data: dict) -> dict:
    try:
        client = get_client()
        result = client.table("events").insert(data).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"[event_repo] create_event error: {e}")
        return local_database.insert("events", data)


def update_event(event_id: str, data: dict) -> dict:
    try:
        client = get_client()
        result = client.table("events").update(data).eq("id", event_id).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else {}
    except Exception as e:
        print(f"[event_repo] update_event error: {e}")
        return local_database.update("events", event_id, data)


def delete_event(event_id: str) -> bool:
    try:
        client = get_client()
        client.table("events").update({"is_active": False}).eq("id", event_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] delete_event error: {e}")
        return bool(local_database.update("events", event_id, {"is_active": False}))


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
        return local_database.set_count("events", event_id, "registered_count", 1)


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
        return local_database.set_count("events", event_id, "registered_count", -1)


@st.cache_data(ttl=300)
def get_registrations_for_event(event_id: str) -> list:
    try:
        client = get_client()
        result = client.table("event_registrations").select("*").eq("event_id", event_id).execute()
        return result.data or local_database.all_rows("event_registrations", lambda r: r.get("event_id") == event_id)
    except Exception as e:
        print(f"[event_repo] get_registrations_for_event error: {e}")
        return local_database.all_rows("event_registrations", lambda r: r.get("event_id") == event_id)


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
        if events:
            return events
        regs = local_database.all_rows("event_registrations", lambda r: r.get("user_id") == user_id)
        return [
            event for event in (
                local_database.one("events", lambda e, event_id=reg.get("event_id"): e.get("id") == event_id)
                for reg in regs
            )
            if event
        ]
    except Exception as e:
        print(f"[event_repo] get_user_registrations error: {e}")
        regs = local_database.all_rows("event_registrations", lambda r: r.get("user_id") == user_id)
        return [
            event for event in (
                local_database.one("events", lambda e, event_id=reg.get("event_id"): e.get("id") == event_id)
                for reg in regs
            )
            if event
        ]


def register_user(event_id: str, user_id: str) -> bool:
    try:
        client = get_client()
        client.table("event_registrations").insert({"event_id": event_id, "user_id": user_id}).execute()
        increment_registered_count(event_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] register_user error: {e}")
        exists = local_database.one(
            "event_registrations",
            lambda r: r.get("event_id") == event_id and r.get("user_id") == user_id,
        )
        if exists:
            return True
        local_database.insert("event_registrations", {"event_id": event_id, "user_id": user_id})
        local_database.set_count("events", event_id, "registered_count", 1)
        return True


def unregister_user(event_id: str, user_id: str) -> bool:
    try:
        client = get_client()
        client.table("event_registrations").delete().eq("event_id", event_id).eq("user_id", user_id).execute()
        decrement_registered_count(event_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[event_repo] unregister_user error: {e}")
        removed = local_database.delete_where(
            "event_registrations",
            lambda r: r.get("event_id") == event_id and r.get("user_id") == user_id,
        )
        if removed:
            local_database.set_count("events", event_id, "registered_count", -1)
        return removed


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
        if result.data:
            return True
        return bool(local_database.one(
            "event_registrations",
            lambda r: r.get("event_id") == event_id and r.get("user_id") == user_id,
        ))
    except Exception as e:
        print(f"[event_repo] is_registered error: {e}")
        return bool(local_database.one(
            "event_registrations",
            lambda r: r.get("event_id") == event_id and r.get("user_id") == user_id,
        ))
