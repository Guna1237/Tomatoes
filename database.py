"""
CampusConnect – Supabase client singleton.
"""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_client() -> Client:
    """Return a cached Supabase client, initialised from Streamlit secrets."""
    import os
    url: str = st.secrets.get("SUPABASE_URL", "") or os.environ.get("SUPABASE_URL", "")
    key: str = st.secrets.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_KEY in .streamlit/secrets.toml or as environment variables."
        )
    return create_client(url, key)
