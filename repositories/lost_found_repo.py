import streamlit as st
from database import get_client
import local_database
from typing import Optional


TABLE = "lost_found"


@st.cache_data(ttl=120)
def get_all_items() -> list:
    try:
        client = get_client()
        result = client.table(TABLE).select("*").order("created_at", desc=True).execute()
        if result.data:
            return result.data
        rows = local_database.all_rows(TABLE)
        return sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True)
    except Exception as e:
        print(f"[lost_found_repo] get_all_items error: {e}")
        rows = local_database.all_rows(TABLE)
        return sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True)


def get_item_by_id(item_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table(TABLE).select("*").eq("id", item_id).execute()
        if result.data:
            return result.data[0]
        return local_database.one(TABLE, lambda i: i.get("id") == item_id)
    except Exception as e:
        print(f"[lost_found_repo] get_item_by_id error: {e}")
        return local_database.one(TABLE, lambda i: i.get("id") == item_id)


def create_item(data: dict) -> dict:
    try:
        client = get_client()
        result = client.table(TABLE).insert(data).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else local_database.insert(TABLE, data)
    except Exception as e:
        print(f"[lost_found_repo] create_item error: {e}")
        st.cache_data.clear()
        return local_database.insert(TABLE, data)


def update_item(item_id: str, data: dict) -> dict:
    try:
        client = get_client()
        result = client.table(TABLE).update(data).eq("id", item_id).execute()
        st.cache_data.clear()
        return result.data[0] if result.data else local_database.update(TABLE, item_id, data)
    except Exception as e:
        print(f"[lost_found_repo] update_item error: {e}")
        st.cache_data.clear()
        return local_database.update(TABLE, item_id, data)
