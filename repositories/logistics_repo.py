import streamlit as st
from database import get_client
from typing import Optional


@st.cache_data(ttl=60)
def get_all_requests() -> list:
    try:
        client = get_client()
        result = client.table("logistics_requests").select("*").order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"[logistics_repo] get_all_requests error: {e}")
        return []


@st.cache_data(ttl=60)
def get_request_by_id(req_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table("logistics_requests").select("*").eq("id", req_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"[logistics_repo] get_request_by_id error: {e}")
        return None


def create_request(data: dict) -> dict:
    client = get_client()
    result = client.table("logistics_requests").insert(data).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}


def update_request(req_id: str, data: dict) -> dict:
    client = get_client()
    result = client.table("logistics_requests").update(data).eq("id", req_id).execute()
    st.cache_data.clear()
    return result.data[0] if result.data else {}
