import streamlit as st
import datetime
import services
import ui_components


def render(user: dict) -> None:
    """Renders the CampusConnect Smart Dashboard."""

    # --- Greeting ---
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    first_name = user["name"].split(" ")[0]
    ui_components.page_header(
        title=f"{greeting}, {first_name}",
        subtitle="Here is what is happening on campus today.",
        icon="home"
    )

    user_id = user["id"]

    # Refresh user to get latest tomato balance
    refreshed = services.UserService.get_by_id(user_id)
    if refreshed:
        user = refreshed

    # --- Fetch data ---
    try:
        all_events = services.EventService.get_all()
    except Exception as e:
        st.error(f"Could not load events: {e}")
        all_events = []

    try:
        user_events = services.EventService.get_user_events(user_id)
    except Exception as e:
        st.error(f"Could not load your registrations: {e}")
        user_events = []

    try:
        all_logistics = services.ParcelService.get_all()
    except Exception as e:
        st.error(f"Could not load logistics: {e}")
        all_logistics = []

    try:
        announcements = services.AnnouncementService.get_all()
    except Exception as e:
        st.error(f"Could not load announcements: {e}")
        announcements = []

    # Derived counts
    registered_event_ids = {e["id"] for e in user_events}
    today = datetime.date.today()

    upcoming_unregistered = [
        e for e in all_events
        if e["id"] not in registered_event_ids
        and datetime.date.fromisoformat(e["date"]) >= today
    ]

    active_requests = [
        r for r in all_logistics
        if r["requester_id"] == user_id and r["status"] != "Delivered"
    ]

    tomato_balance = user.get("tomatos", 0)

    # --- KPI Row (4 cards) ---
    st.markdown("""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.75rem;">
""", unsafe_allow_html=True)

    kpi_html = f"""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.75rem;">

  <div class="metric-box">
    <div class="metric-icon-wrapper" style="color: #A855F7; background-color: rgba(168,85,247,0.12);">
      <i data-lucide="calendar-search"></i>
    </div>
    <div class="metric-info">
      <span class="metric-value">{len(upcoming_unregistered)}</span>
      <span class="metric-label">Upcoming Events</span>
    </div>
  </div>

  <div class="metric-box">
    <div class="metric-icon-wrapper" style="color: #22C55E; background-color: rgba(34,197,94,0.12);">
      <i data-lucide="calendar-check-2"></i>
    </div>
    <div class="metric-info">
      <span class="metric-value">{len(user_events)}</span>
      <span class="metric-label">My Registrations</span>
    </div>
  </div>

  <div class="metric-box">
    <div class="metric-icon-wrapper" style="color: #F59E0B; background-color: rgba(245,158,11,0.12);">
      <i data-lucide="coins"></i>
    </div>
    <div class="metric-info">
      <span class="metric-value">{tomato_balance}</span>
      <span class="metric-label">Tomato Balance</span>
    </div>
  </div>

  <div class="metric-box">
    <div class="metric-icon-wrapper" style="color: #3B82F6; background-color: rgba(59,130,246,0.12);">
      <i data-lucide="package"></i>
    </div>
    <div class="metric-info">
      <span class="metric-value">{len(active_requests)}</span>
      <span class="metric-label">Active Requests</span>
    </div>
  </div>

</div>
"""
    st.markdown(kpi_html, unsafe_allow_html=True)
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)

    # =====================================================================
    # Section: Upcoming Events (next 3 user hasn't registered for)
    # =====================================================================
    sec_col1, sec_col2 = st.columns([8, 2])
    with sec_col1:
        st.markdown(
            '<h3 style="margin: 0.25rem 0 0.75rem 0; color:#FFFFFF; font-size:1.2rem; '
            'display:flex; align-items:center; gap:8px;">'
            '<i data-lucide="sparkles" style="color:#A855F7; width:20px;"></i> Upcoming Events</h3>',
            unsafe_allow_html=True
        )
    with sec_col2:
        if st.button("View all", key="dash_view_all_events", use_container_width=True):
            st.query_params["page"] = "Events"
            st.rerun()

    next_events = sorted(
        upcoming_unregistered,
        key=lambda x: x["date"]
    )[:3]

    if next_events:
        evt_cols = st.columns(len(next_events))
        for idx, event in enumerate(next_events):
            with evt_cols[idx]:
                date_obj = datetime.date.fromisoformat(event["date"])
                formatted_date = date_obj.strftime("%b %d, %Y")
                fill_pct = min(100, int((event["registered_count"] / max(event["capacity"], 1)) * 100))
                spots_left = max(0, event["capacity"] - event["registered_count"])
                is_full = spots_left <= 0

                bar_color = "#DD0426" if fill_pct > 80 else "#22C55E" if fill_pct < 50 else "#F59E0B"

                st.markdown(f"""
<div class="premium-card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column;">
  <div style="position:relative; height:110px; width:100%;">
    <img src="{event['banner_url']}" style="width:100%; height:100%; object-fit:cover;" />
    <div style="position:absolute; top:8px; right:8px; background:rgba(0,0,0,0.65);
                padding:3px 8px; border-radius:6px; font-size:0.7rem; color:#fff; font-weight:600;">
      {spots_left} left
    </div>
  </div>
  <div style="padding:1rem; flex-grow:1; display:flex; flex-direction:column; gap:6px;">
    <h5 style="margin:0; color:#FFFFFF; font-size:0.95rem; font-weight:700;
               white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{event['title']}</h5>
    <div style="font-size:0.78rem; color:#94A3B8; display:flex; align-items:center; gap:5px;">
      <i data-lucide="calendar" style="width:12px;"></i> {formatted_date}
    </div>
    <div style="font-size:0.78rem; color:#94A3B8; display:flex; align-items:center; gap:5px;
                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
      <i data-lucide="map-pin" style="width:12px;"></i> {event['venue']}
    </div>
    <div style="margin-top:6px;">
      <div style="display:flex; justify-content:space-between; font-size:0.7rem;
                  color:#94A3B8; margin-bottom:3px;">
        <span>{event['registered_count']} / {event['capacity']}</span>
        <span>{fill_pct}%</span>
      </div>
      <div style="background:#2D3748; height:4px; border-radius:2px;">
        <div style="background:{bar_color}; width:{fill_pct}%; height:100%; border-radius:2px;"></div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

                if is_full:
                    st.button("Event Full", key=f"dash_full_{event['id']}", disabled=True,
                              use_container_width=True)
                else:
                    if st.button("Register", key=f"dash_reg_{event['id']}", type="primary",
                                 use_container_width=True):
                        try:
                            services.EventService.register(event["id"], user_id)
                            st.success(f"Registered for {event['title']}!")
                            ui_components.safe_rerun()
                        except Exception as err:
                            st.error(f"Registration failed: {err}")
    else:
        ui_components.render_empty_state(
            title="All caught up",
            description="You are registered for all available upcoming events, or no events are scheduled.",
            icon="calendar-check"
        )

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
    st.divider()

    # =====================================================================
    # Two-column layout: My Registered Events | Recent Announcements
    # =====================================================================
    col_left, col_right = st.columns([6, 6])

    # --- My Registered Events ---
    with col_left:
        hdr_l1, hdr_l2 = st.columns([7, 3])
        with hdr_l1:
            st.markdown(
                '<h3 style="margin:0 0 0.75rem 0; color:#FFFFFF; font-size:1.1rem; '
                'display:flex; align-items:center; gap:8px;">'
                '<i data-lucide="calendar-check-2" style="color:#22C55E; width:18px;"></i> '
                'My Registered Events</h3>',
                unsafe_allow_html=True
            )
        with hdr_l2:
            if st.button("View all", key="dash_view_my_events", use_container_width=True):
                st.query_params["page"] = "Events"
                st.rerun()

        if user_events:
            upcoming_mine = sorted(user_events, key=lambda x: x["date"])[:3]
            for event in upcoming_mine:
                date_obj = datetime.date.fromisoformat(event["date"])
                formatted_date = date_obj.strftime("%b %d, %Y")
                st.markdown(f"""
<div class="premium-card" style="padding:0.9rem; margin-bottom:0.5rem;">
  <div style="display:flex; gap:10px; align-items:start;">
    <img src="{event['banner_url']}"
         style="width:56px; height:44px; object-fit:cover; border-radius:6px; flex-shrink:0;" />
    <div style="overflow:hidden; flex-grow:1;">
      <h5 style="margin:0 0 3px 0; color:#FFFFFF; font-size:0.9rem; font-weight:700;
                 white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{event['title']}</h5>
      <div style="font-size:0.75rem; color:#94A3B8; display:flex; gap:10px; flex-wrap:wrap;">
        <span><i data-lucide="clock" style="width:11px;"></i> {formatted_date} @ {event['time']}</span>
        <span><i data-lucide="map-pin" style="width:11px;"></i> {event['venue']}</span>
      </div>
    </div>
    <span style="background:rgba(34,197,94,0.12); color:#22C55E; border:1px solid rgba(34,197,94,0.25);
                 border-radius:9999px; font-size:0.65rem; font-weight:600; padding:2px 8px; flex-shrink:0;
                 white-space:nowrap;">Registered</span>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No registered events",
                description="Explore the Events Hub and sign up for something exciting.",
                icon="calendar"
            )

    # --- Recent Announcements ---
    with col_right:
        hdr_r1, hdr_r2 = st.columns([7, 3])
        with hdr_r1:
            st.markdown(
                '<h3 style="margin:0 0 0.75rem 0; color:#FFFFFF; font-size:1.1rem; '
                'display:flex; align-items:center; gap:8px;">'
                '<i data-lucide="megaphone" style="color:#EAB308; width:18px;"></i> '
                'Recent Announcements</h3>',
                unsafe_allow_html=True
            )
        with hdr_r2:
            if st.button("View all", key="dash_view_announcements", use_container_width=True):
                st.query_params["page"] = "Announcements"
                st.rerun()

        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_anns = sorted(
            announcements,
            key=lambda a: (priority_order.get(a.get("priority", "Low"), 2), a["created_at"])
        )[:3]

        if sorted_anns:
            for ann in sorted_anns:
                p = ann.get("priority", "Low")
                if p == "High":
                    badge_bg = "rgba(221,4,38,0.12)"
                    badge_color = "#DD0426"
                    badge_border = "rgba(221,4,38,0.25)"
                elif p == "Medium":
                    badge_bg = "rgba(245,158,11,0.12)"
                    badge_color = "#F59E0B"
                    badge_border = "rgba(245,158,11,0.25)"
                else:
                    badge_bg = "rgba(148,163,184,0.12)"
                    badge_color = "#94A3B8"
                    badge_border = "rgba(148,163,184,0.25)"

                content_preview = ann["content"][:120] + ("..." if len(ann["content"]) > 120 else "")
                st.markdown(f"""
<div class="premium-card" style="padding:0.9rem; margin-bottom:0.5rem;">
  <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:5px;">
    <span style="font-size:0.7rem; font-weight:600; background:{badge_bg}; color:{badge_color};
                 border:1px solid {badge_border}; border-radius:9999px; padding:2px 8px;">
      {p}
    </span>
    <span class="category-tag" style="font-size:0.65rem;">{ann.get('category','General')}</span>
  </div>
  <h5 style="margin:0 0 4px 0; color:#FFFFFF; font-size:0.9rem; font-weight:700;">{ann['title']}</h5>
  <p style="margin:0; color:#94A3B8; font-size:0.8rem; line-height:1.4;">{content_preview}</p>
  <div style="margin-top:8px; font-size:0.72rem; color:#4B5563; display:flex; gap:10px;">
    <span>By {ann.get('author_name', ann.get('author', ''))}</span>
    <span>{str(ann.get('created_at',''))[:10]}</span>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No announcements",
                description="Official notices will appear here.",
                icon="megaphone"
            )

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
    st.divider()

    # =====================================================================
    # Section: Recent Parcel Requests
    # =====================================================================
    pr_hdr1, pr_hdr2 = st.columns([8, 2])
    with pr_hdr1:
        st.markdown(
            '<h3 style="margin:0 0 0.75rem 0; color:#FFFFFF; font-size:1.1rem; '
            'display:flex; align-items:center; gap:8px;">'
            '<i data-lucide="package" style="color:#3B82F6; width:18px;"></i> '
            'Recent Parcel Requests</h3>',
            unsafe_allow_html=True
        )
    with pr_hdr2:
        if st.button("View all", key="dash_view_logistics", use_container_width=True):
            st.query_params["page"] = "Logistics"
            st.rerun()

    user_requests = [r for r in all_logistics if r["requester_id"] == user_id][:4]

    if user_requests:
        status_colors = {
            "Created":   ("#3B82F6", "rgba(59,130,246,0.12)", "rgba(59,130,246,0.25)"),
            "Accepted":  ("#A855F7", "rgba(168,85,247,0.12)", "rgba(168,85,247,0.25)"),
            "Picked Up": ("#F59E0B", "rgba(245,158,11,0.12)", "rgba(245,158,11,0.25)"),
            "Delivered": ("#22C55E", "rgba(34,197,94,0.12)",  "rgba(34,197,94,0.25)"),
            "Cancelled": ("#EF4444", "rgba(239,68,68,0.12)",  "rgba(239,68,68,0.25)"),
        }

        req_cols = st.columns(min(len(user_requests), 2))
        for idx, req in enumerate(user_requests):
            col = req_cols[idx % 2]
            status = req.get("status", "Created")
            sc = status_colors.get(status, ("#94A3B8", "rgba(148,163,184,0.12)", "rgba(148,163,184,0.25)"))
            with col:
                st.markdown(f"""
<div class="premium-card" style="padding:0.9rem; margin-bottom:0.5rem;">
  <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:6px;">
    <h5 style="margin:0; color:#FFFFFF; font-size:0.9rem; font-weight:700;
               white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;">
      {req['title']}
    </h5>
    <span style="background:{sc[1]}; color:{sc[0]}; border:1px solid {sc[2]};
                 border-radius:9999px; font-size:0.65rem; font-weight:600;
                 padding:2px 8px; flex-shrink:0; white-space:nowrap;">{status}</span>
  </div>
  <div style="font-size:0.78rem; color:#94A3B8; display:flex; flex-direction:column; gap:3px;">
    <span><i data-lucide="arrow-right" style="width:11px;"></i>
      {req.get('pickup_location','—')} &rarr; {req.get('delivery_location','—')}</span>
    <span style="font-size:0.7rem; color:#4B5563;">{req.get('created_at','')[:10]}</span>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        ui_components.render_empty_state(
            title="No parcel requests",
            description="Your logistics requests will appear here once submitted.",
            icon="package"
        )

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
