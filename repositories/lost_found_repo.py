import streamlit as st
from database import get_client
from typing import Optional


@st.cache_data(ttl=120)
def get_all_items() -> list:
    try:
        client = get_client()
        result = client.table("lost_found_items").select("*").order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"[lost_found_repo] get_all_items error: {e}")
        return []


def get_item_by_id(item_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("lost_found_items").select("*").eq("id", item_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[lost_found_repo] get_item_by_id error: {e}")
        return None


def create_item(data: dict) -> dict:
    client = get_client()
    result = client.table("lost_found_items").insert(data).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}


def update_item(item_id: str, data: dict) -> dict:
    client = get_client()
    result = client.table("lost_found_items").update(data).eq("id", item_id).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}
