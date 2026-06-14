import streamlit as st
import os

# Set page config (MUST BE FIRST Streamlit call)
st.set_page_config(
    page_title="CampusConnect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

import database
import ui_components
from modules import dashboard, events, announcements, resources, logistics, lost_found, profile

# Create modules __init__.py if it doesn't exist to ensure proper imports
os.makedirs(r"c:\Users\notgu\OneDrive\Documents\campus\modules", exist_ok=True)
with open(r"c:\Users\notgu\OneDrive\Documents\campus\modules\__init__.py", "a") as f:
    pass

# Inject global CSS and JS scripts
ui_components.inject_custom_styles()

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --- LOGIN & REGISTRATION PAGE ---
if not st.session_state.logged_in:
    # Centered single-column layout for login
    _, col_login, _ = st.columns([3, 4, 3])
    
    with col_login:
        # Title Banner
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem; margin-bottom: 2rem;" class="fade-in">
            <h1 style="color: #3B82F6; margin: 0; font-size: 2.5rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 8px;">
                <i data-lucide="graduation-cap" style="width: 40px; height: 40px; color: #3B82F6;"></i>
                CampusConnect
            </h1>
            <p style="color: #94A3B8; margin-top: 8px; font-size: 1.05rem;">The unified SaaS portal for campus activities, resources, and logistics.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Form Container
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; color:#FFFFFF; font-size:1.2rem; text-align:center;'>Student Sign In</h3>", unsafe_allow_html=True)
        
        email_input = st.text_input("University Email", placeholder="e.g. student@university.edu")
        name_input = st.text_input("Full Name (For New Users)", placeholder="e.g. Jane Doe")
        
        # Check domain restrictions or simple validation
        login_btn = st.button("Enter Platform", type="primary", use_container_width=True)
        
        if login_btn:
            if not email_input:
                st.error("Please enter your university email.")
            elif "@" not in email_input:
                st.error("Please enter a valid email address.")
            else:
                # Retrieve or register user
                user = database.get_user_by_email(email_input)
                if not user:
                    if not name_input:
                        st.warning("New user detected. Please enter your Full Name to create your account.")
                    else:
                        user = database.register_user(email_input, name_input, "student")
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
        
        # Demo account quick selector
        st.markdown("""
        <div class="premium-card" style="margin-top: 1.5rem; border-color: rgba(168, 85, 247, 0.25);">
            <h4 style="margin-top:0; color:#A855F7; font-size:1rem; text-align:center; display:flex; align-items:center; justify-content:center; gap:6px;">
                <i data-lucide="shield-check" style="width: 16px;"></i> Demo Evaluation Profiles
            </h4>
            <p style="font-size:0.8rem; color:#94A3B8; text-align:center; margin-bottom:12px;">Quickly login with pre-configured student, organizer, or admin roles for testing:</p>
        </div>
        """, unsafe_allow_html=True)
        
        demo_col1, demo_col2, demo_col3 = st.columns(3)
        
        with demo_col1:
            if st.button("Jane (Student)", key="demo_student_btn", use_container_width=True):
                user = database.get_user_by_email("jane@university.edu")
                st.session_state.logged_in = True
                st.session_state.current_user = user
                ui_components.safe_rerun()
                
        with demo_col2:
            if st.button("ACS Club (Club)", key="demo_club_btn", use_container_width=True):
                user = database.get_user_by_email("acs@university.edu")
                st.session_state.logged_in = True
                st.session_state.current_user = user
                ui_components.safe_rerun()
                
        with demo_col3:
            if st.button("Dr. Arthur (Admin)", key="demo_admin_btn", use_container_width=True):
                user = database.get_user_by_email("registrar@university.edu")
                st.session_state.logged_in = True
                st.session_state.current_user = user
                ui_components.safe_rerun()
                
        # Load Lucide icons in login page
        st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)

# --- APPLICATION LAYOUT (LOGGED IN) ---
else:
    user = st.session_state.current_user
    
    # Reload user info to keep credits up to date
    refreshed_user = database.get_user_by_id(user["id"])
    if refreshed_user:
        user = refreshed_user
        st.session_state.current_user = user

    # Sidebar Header
    st.sidebar.markdown("""
    <div style="padding-bottom: 15px; border-bottom: 1px solid #2D3748; margin-bottom: 15px;">
        <h2 style="color: #3B82F6; margin: 0; font-size: 1.35rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
            <i data-lucide="graduation-cap" style="width: 22px; height: 22px; color: #3B82F6;"></i>
            CampusConnect
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation list (Custom styled Streamlit buttons)
    # Using type="primary" for the active button, and "secondary" for inactive ones.
    # The injected CSS styles primary as active colored, secondary as hoverable transparent.
    nav_items = [
        {"name": "Dashboard", "icon": "home"},
        {"name": "Events", "icon": "calendar"},
        {"name": "Announcements", "icon": "megaphone"},
        {"name": "Resources", "icon": "folder-open"},
        {"name": "Logistics", "icon": "truck"},
        {"name": "Lost & Found", "icon": "package"},
        {"name": "Profile", "icon": "user"}
    ]
    
    st.sidebar.markdown("<span style='font-size:0.75rem; color:#4B5563; text-transform:uppercase; font-weight:700; letter-spacing:1px;'>Navigation</span>", unsafe_allow_html=True)
    
    for item in nav_items:
        is_active = st.session_state.current_page == item["name"]
        btn_type = "primary" if is_active else "secondary"
        
        # Display buttons with Lucide icon markers next to labels (CSS will style it)
        # Note: Lucide parser scans text inside buttons as well, or we can use custom icons class
        if st.sidebar.button(f"{item['name']}", key=f"sidebar_nav_{item['name']}", type=btn_type, use_container_width=True):
            st.session_state.current_page = item["name"]
            ui_components.safe_rerun()
            
    # Sidebar Footer Profile card
    st.sidebar.markdown(f"""
    <div style="margin-top: 3rem; padding-top: 15px; border-top: 1px solid #2D3748; display: flex; gap: 10px; align-items: center;">
        <img src="{user['avatar_url']}" style="width: 38px; height: 38px; border-radius: 50%; background-color:#161B22; border: 1px solid #2D3748;" />
        <div style="overflow: hidden; flex-grow: 1;">
            <div style="font-weight: 600; color: #FFFFFF; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user['name']}</div>
            <div style="font-size: 0.75rem; color: #22C55E; font-weight: 500;">{user['credits']} Credits</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sign out button
    if st.sidebar.button("Sign Out", key="sidebar_signout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.current_page = "Dashboard"
        st.success("Signed out successfully.")
        ui_components.safe_rerun()
        
    # --- RENDER MAIN PAGE CONTENT ---
    page = st.session_state.current_page
    
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
    except Exception as e:
        st.error(f"An error occurred loading the page '{page}': {e}")
        st.exception(e)
        
    # Reload icons to capture any newly rendered HTML elements
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
