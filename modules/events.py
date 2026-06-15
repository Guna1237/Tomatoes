import streamlit as st
import datetime
import calendar
import services
import ui_components

def render(user: dict):
    """
    Renders the Events Hub.
    """
    ui_components.page_header(
        title="Events Hub",
        subtitle="Discover student activities, register for workshops, and manage your club events.",
        icon="calendar"
    )
    
    user_id = user["id"]
    role = user["role"]
    
    # Check tabs
    tab_explore, tab_calendar, tab_my_events, tab_host = st.tabs([
        "Explore Events", 
        "Event Calendar", 
        "My Schedule", 
        "Host an Event"
    ])
    
    events = services.EventService.get_all()
    
    # --- Tab 1: Explore Events ---
    with tab_explore:
        col_search, col_cat, col_toggle = st.columns([5, 3, 2])
        with col_search:
            search_query = st.text_input("Search events...", placeholder="Search by title, description, or venue", key="evt_search")
        with col_cat:
            all_organizers = sorted(set(e["organizer_name"] for e in events))
            category_filter = st.selectbox("Filter by organizer", ["All Organizers"] + all_organizers, key="evt_organizer")
        with col_toggle:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            upcoming_only = st.checkbox("Upcoming only", value=True, key="evt_upcoming_only")

        # Filter events
        today_date = datetime.date.today()
        filtered_events = events
        if upcoming_only:
            filtered_events = [
                e for e in filtered_events
                if datetime.date.fromisoformat(e["date"]) >= today_date
            ]
        if search_query:
            filtered_events = [
                e for e in filtered_events
                if search_query.lower() in e["title"].lower()
                or search_query.lower() in e["description"].lower()
                or search_query.lower() in e["venue"].lower()
            ]
        if category_filter != "All Organizers":
            filtered_events = [e for e in filtered_events if e["organizer_name"] == category_filter]
            
        if filtered_events:
            # Render events in a 2-column layout
            evt_cols = st.columns(2)
            for idx, event in enumerate(filtered_events):
                col = evt_cols[idx % 2]
                with col:
                    date_obj = datetime.date.fromisoformat(event["date"])
                    formatted_date = date_obj.strftime("%A, %b %d, %Y")
                    
                    is_registered = services.EventService.is_registered(event["id"], user_id)
                    spots_left = max(0, event["capacity"] - event["registered_count"])
                    fill_pct = min(100, int((event["registered_count"] / event["capacity"]) * 100))
                    
                    # Custom Eventbrite-style Card
                    col.markdown(f"""
<div class="premium-card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column;">
<div style="position: relative; height: 140px; width: 100%;">
<img src="{event['banner_url']}" style="width: 100%; height: 100%; object-fit: cover;" />
<div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.6); padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; color: #fff; font-weight: 600;">
{spots_left} Seats Left
</div>
</div>
<div style="padding: 1.25rem; flex-grow: 1; display: flex; flex-direction: column;">
<h4 style="margin: 0 0 6px 0; color: var(--text); font-size: 1.1rem; font-weight: 700;">{event['title']}</h4>
<p style="margin: 0; color: var(--red); font-size: 0.85rem; font-weight: 600; margin-bottom: 12px;">{formatted_date} @ {event['time']}</p>
<div style="margin-bottom: 16px; font-size: 0.85rem; color: var(--muted); display: flex; flex-direction: column; gap: 6px;">
<div style="display: flex; align-items: flex-start; gap: 8px;">
<i data-lucide="map-pin" style="width: 14px; margin-top: 2px;"></i>
<div>
<div style="font-weight: 500; color: var(--text);">{event['venue']}</div>
<div style="color: var(--red); font-size: 0.75rem; cursor: pointer;">Show map</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<i data-lucide="building" style="width: 14px;"></i>
<span>By {event['organizer_name']}</span>
</div>
</div>
<div style="margin-top: auto; padding-top: 12px; border-top: 1px solid var(--border);">
<div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--muted); margin-bottom: 4px;">
<span>{event['registered_count']} / {event['capacity']} Registration</span>
</div>
<div style="background-color: var(--border); height: 4px; border-radius: 2px;">
<div style="background-color: var(--red); width: {fill_pct}%; height: 100%; border-radius: 2px;"></div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                    
                    # Streamlit registration buttons
                    if is_registered:
                        if col.button(f"Unregister from {event['title']}", key=f"unreg_btn_{event['id']}", use_container_width=True):
                            services.EventService.unregister(event["id"], user_id)
                            st.success("Unregistered successfully!")
                            ui_components.safe_rerun()
                    else:
                        if spots_left <= 0:
                            col.button("Event Full", key=f"full_btn_{event['id']}", disabled=True, use_container_width=True)
                        else:
                            if col.button(f"Register for {event['title']}", key=f"reg_btn_{event['id']}", type="primary", use_container_width=True):
                                services.EventService.register(event["id"], user_id)
                                st.success("Registered successfully!")
                                ui_components.safe_rerun()
        else:
            ui_components.render_empty_state(
                title="No events found",
                description="Try modifying your search queries or organizers list.",
                icon="calendar"
            )
            
    # --- Tab 2: Event Calendar ---
    with tab_calendar:
        # Initialize session state for calendar month/year
        if "cal_year" not in st.session_state:
            st.session_state.cal_year = datetime.datetime.now().year
            st.session_state.cal_month = datetime.datetime.now().month
            st.session_state.selected_day = datetime.datetime.now().day
            
        y = st.session_state.cal_year
        m = st.session_state.cal_month
        
        # Month Navigation header
        nav_col1, nav_col2, nav_col3 = st.columns([2, 6, 2])
        with nav_col1:
            if st.button("← Previous", key="cal_prev"):
                st.session_state.cal_month -= 1
                if st.session_state.cal_month == 0:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1
                ui_components.safe_rerun()
        with nav_col2:
            st.markdown(f"<h3 style='text-align: center; margin: 0; color: var(--text);'>{calendar.month_name[m]} {y}</h3>", unsafe_allow_html=True)
        with nav_col3:
            if st.button("Next →", key="cal_next"):
                st.session_state.cal_month += 1
                if st.session_state.cal_month == 13:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1
                ui_components.safe_rerun()
                
        # Generate calendar days list
        cal = calendar.Calendar(firstweekday=6) # Sunday start
        month_days = cal.monthdayscalendar(y, m)
        weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        
        # Render weekday titles
        wk_cols = st.columns(7)
        for i, wk in enumerate(weekdays):
            wk_cols[i].markdown(f"<div style='text-align: center; color: var(--muted); font-weight: 600; font-size: 0.85rem; padding-bottom: 8px;'>{wk}</div>", unsafe_allow_html=True)
            
        # Compile events by day for current month/year
        events_by_day = {}
        for event in events:
            try:
                ey, em, ed = map(int, event["date"].split("-"))
                if ey == y and em == m:
                    events_by_day.setdefault(ed, []).append(event)
            except Exception:
                pass
                
        # Render calendar grid
        for week in month_days:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    # Empty space
                    cols[i].markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)
                else:
                    # Check if day has events
                    day_events = events_by_day.get(day, [])
                    dot = f" ({len(day_events)})" if day_events else ""
                    
                    # Highlight selected day
                    is_sel = st.session_state.selected_day == day
                    btn_type = "primary" if is_sel else "secondary"
                    
                    # Set border color based on whether day has events
                    if day_events and not is_sel:
                        btn_label = f"{day} •"
                    else:
                        btn_label = f"{day}{dot}"
                        
                    if cols[i].button(btn_label, key=f"cal_day_{day}", type=btn_type, use_container_width=True):
                        st.session_state.selected_day = day
                        ui_components.safe_rerun()
                        
        # Display events for selected day
        sel_day = st.session_state.selected_day
        st.markdown(f"<h4 style='margin-top: 1.5rem; color: var(--text);'>Events on {calendar.month_name[m]} {sel_day}, {y}:</h4>", unsafe_allow_html=True)
        selected_events = events_by_day.get(sel_day, [])
        if selected_events:
            for event in selected_events:
                is_registered = services.EventService.is_registered(event["id"], user_id)
                status_chip = '<span class="priority-badge priority-high" style="margin-left: 10px;">Registered</span>' if is_registered else ''
                st.markdown(f"""
<div class="premium-card" style="padding: 1rem;">
<div style="display: flex; justify-content: space-between; align-items: start;">
<div>
<h5 style="margin: 0; font-size: 1rem; color: var(--text);">{event['title']}{status_chip}</h5>
<span style="font-size: 0.8rem; color: var(--muted);">Organizer: {event['organizer_name']} | Time: {event['time']} | Venue: {event['venue']}</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color: var(--muted); font-size: 0.9rem;'>No events scheduled for this day.</div>", unsafe_allow_html=True)

    # --- Tab 3: My Schedule ---
    with tab_my_events:
        my_registered_events = services.EventService.get_user_events(user_id)
        if my_registered_events:
            for event in my_registered_events:
                date_obj = datetime.date.fromisoformat(event["date"])
                formatted_date = date_obj.strftime("%A, %b %d, %Y")
                
                st.markdown(f"""
<div class="premium-card">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<h4 style="margin: 0; color: var(--text); font-size: 1.1rem; font-weight: 700;">{event['title']}</h4>
<p style="margin: 4px 0 0 0; color: var(--muted); font-size: 0.85rem;">
<i data-lucide="calendar" style="width: 12px; height: 12px; display: inline-block;"></i> {formatted_date} @ {event['time']} &nbsp;|&nbsp;
<i data-lucide="map-pin" style="width: 12px; height: 12px; display: inline-block;"></i> {event['venue']}
</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                
                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns([3, 3, 4])
                with col_btn1:
                    if st.button("Cancel Registration", key=f"cancel_reg_{event['id']}", use_container_width=True):
                        services.EventService.unregister(event["id"], user_id)
                        st.success("Cancelled registration.")
                        ui_components.safe_rerun()
                with col_btn2:
                    with st.expander("🎟️ Show Attendance QR"):
                        st.info("Present this QR Code to the organizers to check in.", icon="📱")
                        st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + event['id'] + "_" + user_id)
        else:
            ui_components.render_empty_state(
                title="No registered events",
                description="You are not registered for any upcoming events.",
                icon="calendar"
            )
            
    # --- Tab 4: Host an Event ---
    with tab_host:
        if role in ["admin", "club_admin"]:
            st.markdown("<h3 style='margin-top: 0; color: #FFFFFF; font-size: 1.2rem;'>Create New Event</h3>", unsafe_allow_html=True)
            
            with st.form("create_event_form", clear_on_submit=True):
                evt_title = st.text_input("Event Title *", placeholder="e.g. HackCampus 2026")
                evt_description = st.text_area("Event Description *", placeholder="Provide detail about schedule, prizes, food, etc.")
                
                col_d, col_t = st.columns(2)
                with col_d:
                    evt_date = st.date_input("Date *", min_value=datetime.date.today())
                with col_t:
                    # Provide text selection for time
                    evt_time = st.text_input("Time *", placeholder="e.g. 14:00 or 10:30 AM")
                    
                evt_venue = st.text_input("Venue *", placeholder="e.g. Seminar Hall C or Online")
                evt_banner = st.text_input("Banner Image URL (Optional)", placeholder="e.g. https://images.unsplash.com/photo-...")
                evt_capacity = st.number_input("Maximum Capacity", min_value=10, max_value=1000, value=100)
                
                submit_button = st.form_submit_button("Submit Event Request", type="primary")
                
                if submit_button:
                    if not evt_title or not evt_description or not evt_time or not evt_venue:
                        st.error("Please fill in all mandatory fields (*).")
                    else:
                        services.EventService.create(
                            title=evt_title,
                            description=evt_description,
                            date=evt_date.isoformat(),
                            time=evt_time,
                            venue=evt_venue,
                            banner_url=evt_banner,
                            organizer_id=user_id,
                            organizer_name=user["name"],
                            capacity=evt_capacity
                        )
                        st.success(f"Successfully posted event '{evt_title}'!")
                        ui_components.safe_rerun()
        else:
            # Student view for hosting request
            st.markdown("""
<div class="premium-card" style="text-align: center; padding: 2rem;">
<div style="color: #A855F7; margin-bottom: 1rem;"><i data-lucide="shield-alert" style="width: 48px; height: 48px;"></i></div>
<h4 style="margin: 0 0 6px 0; color: #FFFFFF;">Club Access Required</h4>
<p style="margin: 0; color: var(--muted); font-size: 0.9rem;">
Only verified student clubs or university admin offices can host events.
If you represent an official student organization, you can change your profile role to <strong>Club Admin</strong> in the Profile tab to test this functionality.
</p>
</div>
""", unsafe_allow_html=True)

    # Force render icons
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
