import streamlit as st
import services
import ui_components

def render(user: dict):
    """
    Renders the Profile & Notification Hub.
    """
    user_id = user["id"]
    
    # Reload user info to keep tomatos up to date
    refreshed_user = services.UserService.get_by_id(user_id)
    if refreshed_user:
        user = refreshed_user
        
    ui_components.page_header(
        title="Profile & Notifications",
        subtitle="Manage your profile settings, switch test roles, and check your notification logs.",
        icon="user"
    )
    
    tab_profile, tab_notifications = st.tabs([
        "Profile & Stats",
        "Notification Center"
    ])
    
    # Get statistics
    all_events = services.EventService.get_user_events(user_id)
    all_resources = services.ResourceService.get_all()
    my_resources = [r for r in all_resources if r["uploader_id"] == user_id]
    
    all_logistics = services.ParcelService.get_all()
    completed_jobs = [r for r in all_logistics if r["helper_id"] == user_id and r["status"] == "Delivered"]
    requested_jobs = [r for r in all_logistics if r["requester_id"] == user_id]
    
    # --- Tab 1: Profile & Stats ---
    with tab_profile:
        col_avatar, col_info = st.columns([2, 8])
        
        with col_avatar:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 15px;">
                <img src="{user['avatar_url']}" style="width: 120px; height: 120px; border-radius: 50%; border: 3px solid #3B82F6; background-color: #161B22; padding: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);" />
            </div>
            """, unsafe_allow_html=True)
            
        with col_info:
            st.markdown(f"""
            <h3 style="margin: 0; color: #FFFFFF; font-size: 1.5rem;">{user['name']}</h3>
            <p style="margin: 4px 0 10px 0; color: #94A3B8; font-size: 0.95rem;">{user['email']}</p>
            <div style="display: flex; gap: 8px;">
                <span class="priority-badge" style="background-color: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); font-weight: 600; text-transform: uppercase;">Role: {user['role']}</span>
                <span class="priority-badge" style="background-color: rgba(34, 197, 94, 0.15); color: #22C55E; border: 1px solid rgba(34, 197, 94, 0.3); font-weight: 600;">{user['tomatos']} Tomatos</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Stats counters row (Notion-style boxes)
        st.markdown("<h4 style='color: #FFFFFF; margin-top: 2rem; margin-bottom: 1rem;'>Activity Metrics</h4>", unsafe_allow_html=True)
        stats_cols = st.columns(4)
        
        stats_cols[0].markdown(f"""
        <div class="premium-card" style="text-align: center; padding: 1rem;">
            <span style="font-size: 1.8rem; font-weight: 700; color: #3B82F6; display:block;">{len(all_events)}</span>
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Events Registered</span>
        </div>
        """, unsafe_allow_html=True)
        
        stats_cols[1].markdown(f"""
        <div class="premium-card" style="text-align: center; padding: 1rem;">
            <span style="font-size: 1.8rem; font-weight: 700; color: #A855F7; display:block;">{len(my_resources)}</span>
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Resources Shared</span>
        </div>
        """, unsafe_allow_html=True)
        
        stats_cols[2].markdown(f"""
        <div class="premium-card" style="text-align: center; padding: 1rem;">
            <span style="font-size: 1.8rem; font-weight: 700; color: #22C55E; display:block;">{len(completed_jobs)}</span>
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Deliveries Made</span>
        </div>
        """, unsafe_allow_html=True)
        
        stats_cols[3].markdown(f"""
        <div class="premium-card" style="text-align: center; padding: 1rem;">
            <span style="font-size: 1.8rem; font-weight: 700; color: #F59E0B; display:block;">{len(requested_jobs)}</span>
            <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 500;">Requests Posted</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Role Switcher section for demo presentation
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #FFFFFF; margin-top: 0; margin-bottom: 0.5rem;'><i data-lucide='settings' style='width: 16px; color:#3B82F6; display:inline-block;'></i> Demo Role Switcher</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color:#94A3B8;'>Demonstrate how the application navigation changes dynamically based on student roles. Choose a role to immediately update authorization settings:</p>", unsafe_allow_html=True)
        
        roles = ["student", "club_admin", "admin"]
        selected_role_idx = roles.index(user["role"]) if user["role"] in roles else 0
        new_role = st.selectbox("Current Authorization Role (Test Switcher)", roles, index=selected_role_idx)
        
        if new_role != user["role"]:
            # Update user role in database
            if database.USE_SUPABASE:
                try:
                    database.supabase_client.table("users").update({"role": new_role}).eq("id", user_id).execute()
                except Exception as e:
                    st.error(f"Supabase update error: {e}")
            else:
                for u in database.mock_db.data["users"]:
                    if u["id"] == user_id:
                        u["role"] = new_role
                        break
                database.mock_db.save()
                
            st.success(f"Role changed to {new_role}! Reloading...")
            ui_components.safe_rerun()
            
    # --- Tab 2: Notification Center ---
    with tab_notifications:
        notifications = services.NotificationService.get_all(user_id)
        
        col_ctrl1, col_ctrl2 = st.columns([7, 3])
        with col_ctrl1:
            st.markdown(f"<h4 style='color:#FFFFFF; margin: 0;'>Notification Logs ({len(notifications)})</h4>", unsafe_allow_html=True)
        with col_ctrl2:
            if notifications:
                if st.button("Clear All Notifications", key="clear_all_notif", type="secondary", use_container_width=True):
                    services.NotificationService.clear_all(user_id)
                    st.success("All notifications cleared.")
                    ui_components.safe_rerun()
                    
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        if notifications:
            for notif in notifications:
                # Layout formatting based on read/unread
                is_unread = not notif["read"]
                dot_style = "display: inline-block; width: 8px; height: 8px; background-color: #3B82F6; border-radius: 50%; margin-right: 8px;" if is_unread else "display:none;"
                bg_color = "rgba(59, 130, 246, 0.04)" if is_unread else "transparent"
                border_color = "rgba(59, 130, 246, 0.18)" if is_unread else "rgba(255,255,255,0.03)"
                
                st.markdown(f"""
                <div class="premium-card" style="padding: 1rem; margin-bottom: 0.75rem; background-color: {bg_color}; border-color: {border_color};">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="font-weight: 600; color: #FFFFFF; font-size: 0.95rem; display: flex; align-items: center;">
                                <span style="{dot_style}"></span>
                                {notif['title']}
                            </div>
                            <div style="font-size: 0.85rem; color: #E2E8F0; margin-top: 4px; line-height: 1.4;">{notif['content']}</div>
                            <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 6px;"><i data-lucide="clock" style="width:10px; display:inline-block;"></i> Received: {notif['created_at'][:10]} at {notif['created_at'][11:16]}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Single read mark button if unread
                if is_unread:
                    r_col, _ = st.columns([2, 8])
                    with r_col:
                        if st.button("Mark as Read", key=f"read_notif_{notif['id']}", use_container_width=True):
                            services.NotificationService.mark_read(notif["id"])
                            ui_components.safe_rerun()
        else:
            ui_components.render_empty_state(
                title="Your inbox is clear",
                description="Activity updates and announcements notifications will show up here.",
                icon="bell-off"
            )

    # Reload icons
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
