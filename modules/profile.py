import streamlit as st
import services
import ui_components


def _time_ago(ts: str) -> str:
    """Return a human-readable relative time string from an ISO timestamp."""
    try:
        import datetime
        dt = datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{diff.days}d ago"
    except Exception:
        return str(ts)[:10] if ts else ""


def _txn_row(t: dict) -> None:
    amount = t.get("amount", 0)
    is_pos = amount > 0
    sign = "+" if is_pos else ""
    color = "#22C55E" if is_pos else "#EF4444"
    bg = "rgba(34,197,94,0.04)" if is_pos else "rgba(239,68,68,0.04)"
    border = "rgba(34,197,94,0.15)" if is_pos else "rgba(239,68,68,0.15)"
    st.markdown(
        f"""
<div class="premium-card" style="padding:0.75rem 1rem;margin-bottom:0.4rem;display:flex;
     justify-content:space-between;align-items:center;background:{bg};border-color:{border};">
  <div>
    <span style="font-weight:600;color:#EFF6EE;font-size:0.875rem;">{t.get('description','')}</span>
    <div style="font-size:0.72rem;color:#9197AE;margin-top:2px;">
      {str(t.get('created_at',''))[:10]}
    </div>
  </div>
  <span style="font-size:1.05rem;font-weight:700;color:{color};">{sign}{amount} 🍅</span>
</div>""",
        unsafe_allow_html=True,
    )


def render(user: dict) -> None:
    user_id = user["id"]

    # Refresh to latest data
    try:
        refreshed = services.UserService.get_by_id(user_id)
        if refreshed:
            user = refreshed
    except Exception:
        pass

    tomatos = user.get("tomatos", 0)
    role = user.get("role", "student")
    role_label = {"student": "Student", "club_admin": "Club Admin", "admin": "Admin"}.get(role, role.title())
    avatar_url = user.get("avatar_url", "")
    member_since = str(user.get("created_at", ""))[:10] or "—"

    ui_components.page_header(
        title="Profile",
        subtitle="Your account overview, activity stats, and notifications.",
        icon="user",
    )

    # ── Fetch stats data ──────────────────────────────────────────────────────
    try:
        user_events = services.EventService.get_user_events(user_id) or []
    except Exception:
        user_events = []

    try:
        saved_announcements = services.AnnouncementService.get_user_saved(user_id) or []
    except Exception:
        saved_announcements = []

    try:
        all_resources = services.ResourceService.get_all() or []
        my_uploads = [r for r in all_resources if r.get("uploader_id") == user_id]
    except Exception:
        my_uploads = []

    try:
        bookmarked_resources = services.ResourceService.get_user_bookmarked(user_id) or []
    except Exception:
        bookmarked_resources = []

    try:
        all_logistics = services.ParcelService.get_all() or []
        completed_deliveries = [
            r for r in all_logistics
            if r.get("helper_id") == user_id and r.get("status") == "Delivered"
        ]
        my_requests = [r for r in all_logistics if r.get("requester_id") == user_id]
    except Exception:
        completed_deliveries = []
        my_requests = []

    try:
        notifications = services.NotificationService.get_all(user_id) or []
    except Exception:
        notifications = []

    # ── Layout: left column (avatar/info) + right column (tabs) ──────────────
    left_col, right_col = st.columns([1, 2])

    with left_col:
        # Avatar or initials
        if avatar_url:
            st.markdown(
                f'<img src="{avatar_url}" style="width:100px;height:100px;border-radius:50%;'
                f'border:3px solid #DD0426;object-fit:cover;display:block;margin:0 auto 1rem auto;" />',
                unsafe_allow_html=True,
            )
        else:
            initials = "".join(w[0].upper() for w in user.get("name", "?").split()[:2])
            st.markdown(
                f'<div style="width:100px;height:100px;border-radius:50%;background:rgba(221,4,38,0.15);'
                f'border:3px solid #DD0426;display:flex;align-items:center;justify-content:center;'
                f'font-size:2rem;font-weight:700;color:#DD0426;margin:0 auto 1rem auto;">{initials}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
<div style="text-align:center;">
  <h3 style="margin:0;color:#EFF6EE;font-size:1.25rem;font-weight:700;">{user.get('name','')}</h3>
  <div style="margin:6px 0;">
    <span style="background:rgba(221,4,38,0.12);border:1px solid rgba(221,4,38,0.3);color:#DD0426;
          border-radius:20px;padding:2px 12px;font-size:0.75rem;font-weight:600;">{role_label}</span>
  </div>
  <div style="color:#9197AE;font-size:0.82rem;margin:6px 0;">{user.get('email','')}</div>
  <div style="color:#9197AE;font-size:0.78rem;">Member since {member_since}</div>
  <div style="margin-top:12px;display:inline-flex;align-items:center;gap:8px;
       background:rgba(240,45,58,0.08);border:1px solid rgba(240,45,58,0.2);
       border-radius:10px;padding:6px 14px;">
    <span style="font-size:1.1rem;font-weight:700;color:#EFF6EE;">{tomatos}</span>
    <span style="font-size:0.75rem;color:#9197AE;font-weight:500;">🍅 Tomato Credits</span>
  </div>
</div>""",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        # Edit Profile expander
        with st.expander("Edit Profile"):
            with st.form("edit_profile_form"):
                new_name = st.text_input("Display Name", value=user.get("name", ""))
                new_bio = st.text_area("Bio", value=user.get("bio", ""), placeholder="Tell campus a bit about yourself…")
                if st.form_submit_button("Save Changes", type="primary"):
                    try:
                        from database import get_client
                        get_client().table("users").update({"name": new_name, "bio": new_bio}).eq("id", user_id).execute()
                        st.success("Profile updated!")
                        # Refresh session state
                        if "user" in st.session_state:
                            st.session_state["user"]["name"] = new_name
                        ui_components.safe_rerun()
                    except Exception as e:
                        st.error(f"Could not save: {e}")

    with right_col:
        tab_stats, tab_notifs, tab_tomatoes = st.tabs([
            "Activity Stats",
            "Notifications",
            "Tomato History",
        ])

        # ── Tab 1: Activity Stats ─────────────────────────────────────────────
        with tab_stats:
            metrics = [
                ("Events Registered", len(user_events), "calendar", "#A855F7"),
                ("Announcements Saved", len(saved_announcements), "megaphone", "#EAB308"),
                ("Resources Uploaded", len(my_uploads), "upload", "#3B82F6"),
                ("Resources Bookmarked", len(bookmarked_resources), "bookmark", "#6366F1"),
                ("Deliveries Completed", len(completed_deliveries), "package-check", "#22C55E"),
                ("Requests Made", len(my_requests), "file-text", "#FB923C"),
            ]

            row1 = st.columns(3)
            row2 = st.columns(3)
            for i, (label, val, icon, color) in enumerate(metrics):
                target_col = (row1 if i < 3 else row2)[i % 3]
                target_col.markdown(
                    f"""
<div class="premium-card" style="text-align:center;padding:1.25rem 0.75rem;">
  <div style="color:{color};margin-bottom:6px;">
    <i data-lucide="{icon}" style="width:22px;height:22px;"></i>
  </div>
  <div style="font-size:1.75rem;font-weight:700;color:#EFF6EE;line-height:1;">{val}</div>
  <div style="font-size:0.75rem;color:#9197AE;margin-top:4px;font-weight:500;">{label}</div>
</div>""",
                    unsafe_allow_html=True,
                )

        # ── Tab 2: Notifications ──────────────────────────────────────────────
        with tab_notifs:
            ctrl1, ctrl2, ctrl3 = st.columns([5, 2, 2])
            unread_count = len([n for n in notifications if not n.get("is_read")])
            with ctrl1:
                st.markdown(
                    f"<h4 style='color:#EFF6EE;margin:0;'>"
                    f"Notifications <span style='color:#9197AE;font-size:0.875rem;font-weight:400;'>"
                    f"({unread_count} unread)</span></h4>",
                    unsafe_allow_html=True,
                )
            with ctrl2:
                if notifications and st.button("Mark All Read", key="notif_mark_all", use_container_width=True):
                    for n in notifications:
                        if not n.get("is_read"):
                            try:
                                services.NotificationService.mark_read(n["id"])
                            except Exception:
                                pass
                    st.success("All marked as read.")
                    ui_components.safe_rerun()
            with ctrl3:
                if notifications and st.button("Clear All", key="notif_clear_all", use_container_width=True):
                    try:
                        services.NotificationService.clear_all(user_id)
                        st.success("Notifications cleared.")
                        ui_components.safe_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

            st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

            if notifications:
                for notif in notifications:
                    is_unread = not notif.get("read", False)
                    bg = "rgba(221,4,38,0.04)" if is_unread else "transparent"
                    border = "rgba(221,4,38,0.15)" if is_unread else "rgba(145,151,174,0.08)"
                    dot = (
                        '<span style="display:inline-block;width:7px;height:7px;background:#DD0426;'
                        'border-radius:50%;margin-right:6px;vertical-align:middle;flex-shrink:0;"></span>'
                        if is_unread
                        else ""
                    )
                    content_preview = str(notif.get("content", ""))[:120]
                    if len(str(notif.get("content", ""))) > 120:
                        content_preview += "…"

                    notif_type = notif.get("type", "info")
                    type_colors = {
                        "info": "#3B82F6",
                        "success": "#22C55E",
                        "warning": "#EAB308",
                        "error": "#EF4444",
                        "delivery": "#FB923C",
                    }
                    badge_color = type_colors.get(notif_type, "#9197AE")

                    st.markdown(
                        f"""
<div class="premium-card" style="padding:0.875rem 1rem;margin-bottom:0.5rem;
     background:{bg};border-color:{border};">
  <div style="display:flex;align-items:flex-start;gap:0.5rem;">
    <div style="flex:1;min-width:0;">
      <div style="font-weight:600;color:#EFF6EE;font-size:0.875rem;display:flex;align-items:center;">
        {dot}{notif.get('title','')}
      </div>
      <div style="font-size:0.8125rem;color:#9197AE;margin-top:3px;line-height:1.4;">{content_preview}</div>
      <div style="font-size:0.72rem;color:rgba(145,151,174,0.6);margin-top:5px;">
        {_time_ago(notif.get('created_at',''))}
      </div>
    </div>
  </div>
</div>""",
                        unsafe_allow_html=True,
                    )

                    if is_unread:
                        mark_col, _ = st.columns([2, 8])
                        with mark_col:
                            if st.button("Mark Read", key=f"notif_read_{notif['id']}", use_container_width=True):
                                try:
                                    services.NotificationService.mark_read(notif["id"])
                                    ui_components.safe_rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
            else:
                ui_components.render_empty_state(
                    "No notifications",
                    "Activity alerts and updates will appear here.",
                    icon="bell-off",
                )

        # ── Tab 3: Tomato History ─────────────────────────────────────────────
        with tab_tomatoes:
            try:
                transactions = services.TomatoService.get_transactions(user_id) or []
            except Exception:
                transactions = []

            if transactions:
                st.markdown(
                    f"<p style='color:#9197AE;font-size:0.875rem;margin-bottom:1rem;'>"
                    f"Current balance: <strong style='color:#EFF6EE;'>{tomatos} 🍅</strong></p>",
                    unsafe_allow_html=True,
                )
                for t in transactions:
                    _txn_row(t)
            else:
                ui_components.render_empty_state(
                    "No transactions",
                    "Tomato Credit transactions from deliveries and requests will appear here.",
                    icon="wallet",
                )

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
