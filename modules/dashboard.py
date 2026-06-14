import streamlit as st
import datetime
import services
import ui_components

def render(user: dict):
    """
    Renders the Smart Dashboard.
    """
    # 1. Page Header with Personalized Greeting
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
        
    first_name = user["name"].split(" ")[0]
    ui_components.page_header(
        title=f"{greeting}, {first_name}",
        subtitle="Here is what is happening on campus today.",
        icon="home"
    )
    
    # Get user statistics
    user_id = user["id"]
    email = user["email"]
    
    # Reload user info to keep tomatos up to date
    refreshed_user = services.UserService.get_by_id(user_id)
    if refreshed_user:
        user = refreshed_user
        
    user_events = services.EventService.get_user_events(user_id)
    saved_announcements = services.AnnouncementService.get_user_saved(user_id)
    all_logistics = services.ParcelService.get_all()
    
    # Calculate user's active logistics requests (requested by user or accepted by user, and not delivered)
    active_logistics = [
        req for req in all_logistics 
        if (req["requester_id"] == user_id or req["helper_id"] == user_id) 
        and req["status"] != "Delivered"
    ]
    
    # 2. Render KPI metrics
    ui_components.render_kpis(
        tomatos_val=user["tomatos"],
        deliveries_val=len(active_logistics),
        events_val=len(user_events),
        saved_val=len(saved_announcements)
    )
    
    # Layout Grid: 70% main content, 30% sidebar feed
    col_main, col_feed = st.columns([7, 3])
    
    with col_main:
        # 3. Active Logistics Timeline
        if active_logistics:
            latest_active = active_logistics[0]
            # Determine role (Requester vs Helper)
            role_text = "Requested by you" if latest_active["requester_id"] == user_id else f"Accepted by you (Requester: {latest_active['requester_name']})"
            
            st.markdown(f"""
<div class="fade-in" style="margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
<span style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">
Active parcel: <strong>{latest_active['title']}</strong> ({role_text})
</span>
<span class="category-tag" style="background-color: rgba(59, 130, 246, 0.15); color: #60A5FA; border-color: rgba(59, 130, 246, 0.3);">
Route: {latest_active['pickup_location']} → {latest_active['delivery_location']}
</span>
</div>
""", unsafe_allow_html=True)
            
            ui_components.render_timeline(latest_active["status"])
            
            # Add action button in logistics timeline to update state if user is the helper
            if latest_active["helper_id"] == user_id:
                status = latest_active["status"]
                btn_col1, btn_col2 = st.columns([3, 7])
                with btn_col1:
                    if status == "Matched":
                        if st.button("Mark as Picked Up", key="dash_pickup_btn", type="primary"):
                            services.ParcelService.update_status(latest_active["id"], "Picked Up")
                            st.success("Status updated to Picked Up!")
                            ui_components.safe_rerun()
                    elif status == "Picked Up":
                        if st.button("Mark as Delivered", key="dash_deliver_btn", type="primary"):
                            services.ParcelService.update_status(latest_active["id"], "Delivered")
                            st.success("Delivery completed! Tomatos transferred.")
                            ui_components.safe_rerun()
                            
        # 4. Upcoming Registered Events Section
        st.markdown('<h3 style="margin-top: 1.5rem; margin-bottom: 0.75rem; color: #FFFFFF; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;"><i data-lucide="calendar-check" style="color:#A855F7; width:20px;"></i> My Registered Events</h3>', unsafe_allow_html=True)
        if user_events:
            # Sort by date
            user_events_sorted = sorted(user_events, key=lambda x: x["date"])[:2]
            for event in user_events_sorted:
                # Format date
                date_obj = datetime.date.fromisoformat(event["date"])
                formatted_date = date_obj.strftime("%A, %b %d, %Y")
                
                st.markdown(f"""
<div class="premium-card">
<div style="display: flex; gap: 1rem;">
<img src="{event['banner_url']}" class="event-banner" style="width: 120px; height: 80px; margin-bottom: 0;" />
<div style="flex-grow: 1;">
<h4 style="margin: 0 0 4px 0; color: #FFFFFF; font-size: 1.05rem;">{event['title']}</h4>
<p style="margin: 0; color: #94A3B8; font-size: 0.85rem; max-height: 40px; overflow: hidden; text-overflow: ellipsis;">{event['description'][:100]}...</p>
<div class="info-row" style="margin-top: 6px;">
<span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="clock" style="width: 12px; height:12px;"></i> {formatted_date} @ {event['time']}</span>
<span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="map-pin" style="width: 12px; height:12px;"></i> {event['venue']}</span>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No registered events",
                description="You have not registered for any upcoming events yet. Check out the Events Hub to find interesting activities!",
                icon="calendar"
            )
            
        # 5. Recent Announcements
        st.markdown('<h3 style="margin-top: 1.5rem; margin-bottom: 0.75rem; color: #FFFFFF; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;"><i data-lucide="megaphone" style="color:#EAB308; width:20px;"></i> Important Announcements</h3>', unsafe_allow_html=True)
        announcements = services.AnnouncementService.get_all()
        if announcements:
            recent_anns = announcements[:2]
            for ann in recent_anns:
                priority_class = f"priority-{ann['priority'].lower()}"
                
                st.markdown(f"""
<div class="premium-card">
<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
<h4 style="margin: 0; color: #FFFFFF; font-size: 1.05rem;">{ann['title']}</h4>
<span class="priority-badge {priority_class}">{ann['priority']} Priority</span>
</div>
<p style="margin: 0; color: #94A3B8; font-size: 0.88rem; line-height: 1.4;">{ann['content'][:150]}...</p>
<div class="info-row" style="margin-top: 8px; justify-content: space-between;">
<span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="user" style="width: 12px; height: 12px;"></i> By {ann['author']}</span>
<span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="calendar" style="width: 12px; height: 12px;"></i> {ann['created_at'][:10]}</span>
</div>
</div>
""", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No announcements",
                description="No recent announcements found. Admin notices will show up here.",
                icon="megaphone"
            )
            
    with col_feed:
        # 6. Resource Activity Feed
        st.markdown('<h3 style="margin-top: 0; margin-bottom: 0.75rem; color: #FFFFFF; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;"><i data-lucide="file-text" style="color:#3B82F6; width:18px;"></i> New Resources</h3>', unsafe_allow_html=True)
        resources = services.ResourceService.get_all()
        if resources:
            for res in resources[:3]:
                # Map category to icon
                cat_icons = {
                    "Notes": "book-open",
                    "PYQs": "help-circle",
                    "PPTs": "presentation",
                    "PDFs": "file",
                    "Study guides": "compass"
                }
                icon = cat_icons.get(res["category"], "file")
                
                st.markdown(f"""
<div class="premium-card" style="padding: 0.75rem; margin-bottom: 0.5rem; border-color: rgba(255,255,255,0.03);">
<div style="display: flex; gap: 8px; align-items: start;">
<div style="background-color: rgba(59, 130, 246, 0.1); border-radius: 6px; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; color: #3B82F6; flex-shrink: 0;">
<i data-lucide="{icon}" style="width: 14px; height: 14px;"></i>
</div>
<div style="overflow: hidden;">
<h5 style="margin: 0; color: #FFFFFF; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{res['title']}</h5>
<span class="category-tag" style="padding: 0px 4px; font-size: 0.65rem; border-radius: 2px;">{res['course_code']}</span>
<span style="font-size: 0.7rem; color: #94A3B8; margin-left: 4px;">by {res['uploader_name'].split(' ')[0]}</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#94A3B8; font-size:0.85rem; padding: 10px 0;">No resources shared yet.</div>', unsafe_allow_html=True)
            
        # 7. Notifications Sub-panel (Latest 4 notifications)
        st.markdown('<h3 style="margin-top: 1.5rem; margin-bottom: 0.75rem; color: #FFFFFF; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;"><i data-lucide="bell" style="color:#EAB308; width:18px;"></i> Recent Alerts</h3>', unsafe_allow_html=True)
        notifications = services.NotificationService.get_all(user_id)
        if notifications:
            unread_count = len([n for n in notifications if not n["read"]])
            if unread_count > 0:
                st.markdown(f'<span class="category-tag" style="background-color: rgba(239, 68, 68, 0.15); color: #F87171; border-color: rgba(239, 68, 68, 0.3); margin-bottom: 8px; display: inline-block;">{unread_count} Unread</span>', unsafe_allow_html=True)
            
            for notif in notifications[:4]:
                dot_style = "display: inline-block; width: 6px; height: 6px; background-color: #3B82F6; border-radius: 50%; margin-right: 6px;" if not notif["read"] else "display:none;"
                bg_color = "rgba(59, 130, 246, 0.03)" if not notif["read"] else "transparent"
                border_color = "rgba(59, 130, 246, 0.15)" if not notif["read"] else "rgba(255,255,255,0.03)"
                
                st.markdown(f"""
<div class="premium-card" style="padding: 0.75rem; margin-bottom: 0.5rem; background-color: {bg_color}; border-color: {border_color};">
<div style="font-size: 0.85rem; font-weight: 600; color: #FFFFFF; display: flex; align-items: center;">
<span style="{dot_style}"></span>
{notif['title']}
</div>
<div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">{notif['content']}</div>
<div style="font-size: 0.65rem; color: #4B5563; margin-top: 4px;">{notif['created_at'][11:16]} ({notif['created_at'][:10]})</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#94A3B8; font-size:0.85rem; padding: 10px 0;">No active alerts.</div>', unsafe_allow_html=True)

    # Force load icons again
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
