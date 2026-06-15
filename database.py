"""
CampusConnect – Supabase client singleton.
"""

import streamlit as st
from supabase import create_client, Client

# Public anon key — safe to hardcode; no elevated privileges.
_FALLBACK_URL = "https://dkegesnvbkretzeeyflw.supabase.co"
_FALLBACK_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRrZWdlc252YmtyZXR6ZWV5Zmx3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE0NTcxMDgsImV4cCI6MjA5NzAzMzEwOH0"
    ".42PxS5MvqBjK-3vBIEeYFlm_fTQzdQ--KWUAEkFGcWk"
)


@st.cache_resource
def get_client() -> Client:
    import os
    url = st.secrets.get("SUPABASE_URL", "") or os.environ.get("SUPABASE_URL", "") or _FALLBACK_URL
    key = st.secrets.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_KEY", "") or _FALLBACK_KEY
    return create_client(url, key)
