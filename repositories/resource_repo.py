import streamlit as st
from database import get_client
import local_database
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
        if result.data:
            return result.data
        rows = local_database.all_rows("resources", lambda r: r.get("is_active", True))
        return sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True)
    except Exception as e:
        print(f"[resource_repo] get_resources error: {e}")
        rows = local_database.all_rows("resources", lambda r: r.get("is_active", True))
        return sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True)


def create_resource(data: dict) -> dict:
    try:
        client = get_client()
        result = client.table("resources").insert(data).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else local_database.insert("resources", data)
    except Exception as e:
        print(f"[resource_repo] create_resource error: {e}")
        st.cache_data.clear()
        return local_database.insert("resources", data)


def delete_resource(resource_id: str) -> bool:
    try:
        client = get_client()
        client.table("resources").update({"is_active": False}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] delete_resource error: {e}")
        return bool(local_database.update("resources", resource_id, {"is_active": False}))


def get_resource_by_id(resource_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("resources").select("*").eq("id", resource_id).execute()
        if result.data:
            return result.data[0]
        return local_database.one("resources", lambda r: r.get("id") == resource_id)
    except Exception as e:
        print(f"[resource_repo] get_resource_by_id error: {e}")
        return local_database.one("resources", lambda r: r.get("id") == resource_id)


def increment_downloads(resource_id: str) -> bool:
    try:
        client = get_client()
        resource = get_resource_by_id(resource_id)
        if not resource:
            return False
        current = resource.get("downloads_count", 0)
        client.table("resources").update({"downloads_count": current + 1}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] increment_downloads error: {e}")
        return local_database.set_count("resources", resource_id, "downloads_count", 1)


def increment_bookmarks(resource_id: str) -> bool:
    try:
        client = get_client()
        resource = get_resource_by_id(resource_id)
        if not resource:
            return False
        current = resource.get("bookmarks_count", 0)
        client.table("resources").update({"bookmarks_count": current + 1}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] increment_bookmarks error: {e}")
        return local_database.set_count("resources", resource_id, "bookmarks_count", 1)


def decrement_bookmarks(resource_id: str) -> bool:
    try:
        client = get_client()
        resource = get_resource_by_id(resource_id)
        if not resource:
            return False
        current = resource.get("bookmarks_count", 0)
        new_count = max(0, current - 1)
        client.table("resources").update({"bookmarks_count": new_count}).eq("id", resource_id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] decrement_bookmarks error: {e}")
        return local_database.set_count("resources", resource_id, "bookmarks_count", -1)


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
        if resources:
            return resources
        bookmarks = local_database.all_rows("bookmarked_resources", lambda r: r.get("user_id") == user_id)
        return [
            res for res in (
                local_database.one("resources", lambda r, res_id=row.get("resource_id"): r.get("id") == res_id)
                for row in bookmarks
            )
            if res and res.get("is_active", True)
        ]
    except Exception as e:
        print(f"[resource_repo] get_bookmarked_resources error: {e}")
        bookmarks = local_database.all_rows("bookmarked_resources", lambda r: r.get("user_id") == user_id)
        return [
            res for res in (
                local_database.one("resources", lambda r, res_id=row.get("resource_id"): r.get("id") == res_id)
                for row in bookmarks
            )
            if res and res.get("is_active", True)
        ]


def bookmark(user_id: str, resource_id: str) -> bool:
    try:
        client = get_client()
        client.table("bookmarked_resources").insert({"user_id": user_id, "resource_id": resource_id}).execute()
        increment_bookmarks(resource_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] bookmark error: {e}")
        exists = local_database.one(
            "bookmarked_resources",
            lambda r: r.get("user_id") == user_id and r.get("resource_id") == resource_id,
        )
        if not exists:
            local_database.insert("bookmarked_resources", {"user_id": user_id, "resource_id": resource_id})
            local_database.set_count("resources", resource_id, "bookmarks_count", 1)
        return True


def unbookmark(user_id: str, resource_id: str) -> bool:
    try:
        client = get_client()
        client.table("bookmarked_resources").delete().eq("user_id", user_id).eq("resource_id", resource_id).execute()
        decrement_bookmarks(resource_id)
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"[resource_repo] unbookmark error: {e}")
        removed = local_database.delete_where(
            "bookmarked_resources",
            lambda r: r.get("user_id") == user_id and r.get("resource_id") == resource_id,
        )
        if removed:
            local_database.set_count("resources", resource_id, "bookmarks_count", -1)
        return removed


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
        if result.data:
            return True
        return bool(local_database.one(
            "bookmarked_resources",
            lambda r: r.get("user_id") == user_id and r.get("resource_id") == resource_id,
        ))
    except Exception as e:
        print(f"[resource_repo] is_bookmarked error: {e}")
        return bool(local_database.one(
            "bookmarked_resources",
            lambda r: r.get("user_id") == user_id and r.get("resource_id") == resource_id,
        ))
