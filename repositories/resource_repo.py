import streamlit as st
from database import get_client
from typing import Optional


@st.cache_data(ttl=300)
def get_resources() -> list:
    try:
        client = get_client()
        result = (
            client.table("resources")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[resource_repo] get_resources error: {e}")
        return []


def create_resource(data: dict) -> dict:
    client = get_client()
    result = client.table("resources").insert(data).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}


def delete_resource(resource_id: str) -> bool:
    try:
        client = get_client()
        client.table("resources").update({"is_active": False}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] delete_resource error: {e}")
        return False


def get_resource_by_id(resource_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("resources").select("*").eq("id", resource_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[resource_repo] get_resource_by_id error: {e}")
        return None


def increment_downloads(resource_id: str) -> bool:
    try:
        client = get_client()
        resource = get_resource_by_id(resource_id)
        if not resource:
            return False
        current = resource.get("download_count", 0)
        client.table("resources").update({"download_count": current + 1}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] increment_downloads error: {e}")
        return False


def increment_bookmarks(resource_id: str) -> bool:
    try:
        client = get_client()
        resource = get_resource_by_id(resource_id)
        if not resource:
            return False
        current = resource.get("bookmark_count", 0)
        client.table("resources").update({"bookmark_count": current + 1}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] increment_bookmarks error: {e}")
        return False


def decrement_bookmarks(resource_id: str) -> bool:
    try:
        client = get_client()
        resource = get_resource_by_id(resource_id)
        if not resource:
            return False
        current = resource.get("bookmark_count", 0)
        new_count = max(0, current - 1)
        client.table("resources").update({"bookmark_count": new_count}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] decrement_bookmarks error: {e}")
        return False


@st.cache_data(ttl=300)
def get_bookmarked_resources(user_id: str) -> list:
    try:
        client = get_client()
        result = (
            client.table("bookmarked_resources")
            .select("resource_id, resources(*)")
            .eq("user_id", user_id)
            .execute()
        )
        resources = []
        for row in result.data or []:
            if row.get("resources"):
                resources.append(row["resources"])
        return resources
    except Exception as e:
        print(f"[resource_repo] get_bookmarked_resources error: {e}")
        return []


def bookmark(user_id: str, resource_id: str) -> bool:
    try:
        client = get_client()
        client.table("bookmarked_resources").insert({"user_id": user_id, "resource_id": resource_id}).execute()
        increment_bookmarks(resource_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] bookmark error: {e}")
        return False


def unbookmark(user_id: str, resource_id: str) -> bool:
    try:
        client = get_client()
        client.table("bookmarked_resources").delete().eq("user_id", user_id).eq("resource_id", resource_id).execute()
        decrement_bookmarks(resource_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] unbookmark error: {e}")
        return False


def is_bookmarked(user_id: str, resource_id: str) -> bool:
    try:
        client = get_client()
        result = (
            client.table("bookmarked_resources")
            .select("resource_id")
            .eq("user_id", user_id)
            .eq("resource_id", resource_id)
            .execute()
        )
        return len(result.data or []) > 0
    except Exception as e:
        print(f"[resource_repo] is_bookmarked error: {e}")
        return False
