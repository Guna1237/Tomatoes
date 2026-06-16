import streamlit as st
from database import get_client
import local_database
from typing import Optional


TABLE = "parcel_requests"


def _to_db(data: dict) -> dict:
    data = dict(data)
    if "tomato_reward" in data:
        data["tomatoes_offered"] = data.pop("tomato_reward")
    if "tomatos_offered" in data:
        data["tomatoes_offered"] = data.pop("tomatos_offered")
    return data


def _from_db(row: dict) -> dict:
    row = dict(row)
    if "tomatoes_offered" in row:
        row.setdefault("tomato_reward", row["tomatoes_offered"])
        row.setdefault("tomatos_offered", row["tomatoes_offered"])
    return row


@st.cache_data(ttl=60)
def get_all_requests() -> list:
    try:
        client = get_client()
        result = client.table(TABLE).select("*").order("created_at", desc=True).execute()
        if result.data:
            return [_from_db(row) for row in result.data]
        rows = local_database.all_rows(TABLE)
        return sorted([_from_db(row) for row in rows], key=lambda r: r.get("created_at", ""), reverse=True)
    except Exception as e:
        print(f"[logistics_repo] get_all_requests error: {e}")
        rows = local_database.all_rows(TABLE)
        return sorted([_from_db(row) for row in rows], key=lambda r: r.get("created_at", ""), reverse=True)


@st.cache_data(ttl=60)
def get_request_by_id(req_id: str) -> Optional[dict]:
    try:
        client = get_client()
        result = client.table(TABLE).select("*").eq("id", req_id).execute()
        if result.data:
            return _from_db(result.data[0])
        row = local_database.one(TABLE, lambda r: r.get("id") == req_id)
        return _from_db(row) if row else None
    except Exception as e:
        print(f"[logistics_repo] get_request_by_id error: {e}")
        row = local_database.one(TABLE, lambda r: r.get("id") == req_id)
        return _from_db(row) if row else None


def create_request(data: dict) -> dict:
    payload = _to_db(data)
    try:
        client = get_client()
        result = client.table(TABLE).insert(payload).execute()
        st.cache_data.clear()
        return _from_db(result.data[0]) if result.data else _from_db(local_database.insert(TABLE, payload))
    except Exception as e:
        print(f"[logistics_repo] create_request error: {e}")
        st.cache_data.clear()
        return _from_db(local_database.insert(TABLE, payload))


def update_request(req_id: str, data: dict) -> dict:
    payload = _to_db(data)
    try:
        client = get_client()
        result = client.table(TABLE).update(payload).eq("id", req_id).execute()
        st.cache_data.clear()
        return _from_db(result.data[0]) if result.data else _from_db(local_database.update(TABLE, req_id, payload))
    except Exception as e:
        print(f"[logistics_repo] update_request error: {e}")
        st.cache_data.clear()
        return _from_db(local_database.update(TABLE, req_id, payload))
