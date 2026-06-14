import streamlit as st
import os

# Set page config (MUST BE FIRST Streamlit call)
st.set_page_config(
    page_title="CampusConnect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import services
import ui_components
from modules import dashboard, events, announcements, resources, logistics, lost_found, profile

os.makedirs(r"c:\Users\notgu\OneDrive\Documents\campus\modules", exist_ok=True)
with open(r"c:\Users\notgu\OneDrive\Documents\campus\modules\__init__.py", "a") as f:
    pass

# Inject global CSS and JS scripts
ui_components.inject_custom_styles()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Read page from query params
query_params = st.experimental_get_query_params()
current_page = query_params.get("page", ["Dashboard"])[0]
st.session_state.current_page = current_page

# --- LOGIN & REGISTRATION PAGE ---
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([3, 4, 3])
    with col_login:
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem; margin-bottom: 2rem;" class="fade-in">
            <h1 style="color: var(--accent); margin: 0; font-size: 2.5rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 8px;">
                <i data-lucide="graduation-cap" style="width: 40px; height: 40px; color: var(--accent);"></i>
                CampusConnect
            </h1>
            <p style="color: var(--text-secondary); margin-top: 8px; font-size: 1.05rem;">The premium SaaS portal for campus activities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; font-size:1.2rem; text-align:center;'>Student Sign In</h3>", unsafe_allow_html=True)
        
        email_input = st.text_input("University Email", placeholder="e.g. student@university.edu")
        name_input = st.text_input("Full Name (For New Users)", placeholder="e.g. Jane Doe")
        login_btn = st.button("Enter Platform", type="primary", use_container_width=True)
        
        if login_btn:
            if not email_input:
                st.error("Please enter your university email.")
            else:
                user = services.UserService.get_by_email(email_input)
                if not user:
                    if not name_input:
                        st.warning("New user detected. Please enter your Full Name to create your account.")
                    else:
                        user = services.UserService.register(email_input, name_input, "student")
                        st.success(f"Welcome to CampusConnect! Account created for {name_input}.")
                        st.session_state.logged_in = True
                        st.session_state.current_user = user
                        ui_components.safe_rerun()
                else:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.success(f"Welcome back, {user['name']}!")
                    ui_components.safe_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="premium-card" style="margin-top: 1.5rem; border-color: rgba(168, 85, 247, 0.25);">
            <h4 style="margin-top:0; color:#A855F7; font-size:1rem; text-align:center; display:flex; align-items:center; justify-content:center; gap:6px;">
                <i data-lucide="shield-check" style="width: 16px;"></i> Demo Evaluation Profiles
            </h4>
        </div>
        """, unsafe_allow_html=True)
        demo_col1, demo_col2, demo_col3 = st.columns(3)
        with demo_col1:
            if st.button("Jane (Student)", key="demo_student_btn", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.current_user = services.UserService.get_by_email("jane@university.edu")
                ui_components.safe_rerun()
        with demo_col2:
            if st.button("ACS Club (Club)", key="demo_club_btn", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.current_user = services.UserService.get_by_email("acs@university.edu")
                ui_components.safe_rerun()
        with demo_col3:
            if st.button("Dr. Arthur (Admin)", key="demo_admin_btn", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.current_user = services.UserService.get_by_email("registrar@university.edu")
                ui_components.safe_rerun()
        st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)

# --- APPLICATION LAYOUT (LOGGED IN) ---
else:
    user = st.session_state.current_user
    refreshed_user = services.UserService.get_by_id(user["id"])
    if refreshed_user:
        user = refreshed_user
        st.session_state.current_user = user

    # Render custom HTML Sidebar and wrapper
    ui_components.render_custom_sidebar(user, current_page)

    # Wrap main content in a container that responds to sidebar width
    st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)
    
    # Global Search Bar
    search_col1, search_col2 = st.columns([8, 2])
    
    if 'global_search' not in st.session_state:
        st.session_state.global_search = ''
        
    with search_col1:
        global_search = st.text_input('Global Search', placeholder='Search anything... (Ctrl + K to focus)', label_visibility='collapsed', key='global_search')
        st.info(f'Search results for "{global_search}" would appear here.')

    page = current_page
    try:
        if page == "Dashboard":
            dashboard.render(user)
        elif page == "Events":
            events.render(user)
        elif page == "Announcements":
            announcements.render(user)
        elif page == "Resources":
            resources.render(user)
        elif page == "Logistics":
            logistics.render(user)
        elif page == "Lost & Found":
            lost_found.render(user)
        elif page == "Profile":
            profile.render(user)
        elif page == "SignOut":
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.experimental_set_query_params()
            ui_components.safe_rerun()
    except Exception as e:
        st.error(f"An error occurred loading the page '{page}': {e}")
        st.exception(e)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
