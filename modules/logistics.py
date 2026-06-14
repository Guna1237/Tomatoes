import streamlit as st
import services
import ui_components


def _tomato_badge(amount: int) -> str:
    color = "#22C55E" if amount > 0 else "#EF4444"
    bg = "rgba(34,197,94,0.1)" if amount > 0 else "rgba(239,68,68,0.1)"
    border = "rgba(34,197,94,0.25)" if amount > 0 else "rgba(239,68,68,0.25)"
    sign = "+" if amount > 0 else ""
    return (
        f'<span style="background:{bg};border:1px solid {border};color:{color};'
        f'border-radius:20px;padding:2px 10px;font-size:0.78rem;font-weight:700;">'
        f'{sign}{amount} 🍅</span>'
    )


def _status_badge(status: str) -> str:
    colors = {
        "Created": ("#9197AE", "rgba(145,151,174,0.1)", "rgba(145,151,174,0.2)"),
        "Accepted": ("#3B82F6", "rgba(59,130,246,0.1)", "rgba(59,130,246,0.25)"),
        "Picked Up": ("#FB923C", "rgba(251,146,60,0.1)", "rgba(251,146,60,0.25)"),
        "Delivered": ("#22C55E", "rgba(34,197,94,0.1)", "rgba(34,197,94,0.25)"),
        "Cancelled": ("#EF4444", "rgba(239,68,68,0.1)", "rgba(239,68,68,0.25)"),
    }
    c, bg, border = colors.get(status, ("#9197AE", "rgba(145,151,174,0.1)", "rgba(145,151,174,0.2)"))
    return (
        f'<span style="background:{bg};border:1px solid {border};color:{c};'
        f'border-radius:20px;padding:2px 10px;font-size:0.75rem;font-weight:600;">{status}</span>'
    )


def _txn_row(t: dict) -> None:
    is_pos = t.get("amount", 0) > 0
    sign = "+" if is_pos else ""
    color = "#22C55E" if is_pos else "#EF4444"
    bg = "rgba(34,197,94,0.04)" if is_pos else "rgba(239,68,68,0.04)"
    border = "rgba(34,197,94,0.15)" if is_pos else "rgba(239,68,68,0.15)"
    st.markdown(
        f"""
<div class="premium-card" style="padding:0.8rem;margin-bottom:0.4rem;display:flex;
     justify-content:space-between;align-items:center;background:{bg};border-color:{border};">
  <div>
    <span style="font-weight:600;color:#EFF6EE;font-size:0.9rem;">{t.get('description','')}</span>
    <div style="font-size:0.72rem;color:#9197AE;margin-top:2px;">
      {str(t.get('created_at',''))[:10]} {str(t.get('created_at',''))[11:16]}
    </div>
  </div>
  <span style="font-size:1.1rem;font-weight:700;color:{color};">{sign}{t.get('amount',0)} 🍅</span>
</div>""",
        unsafe_allow_html=True,
    )


def render(user: dict) -> None:
    user_id = user["id"]

    # Refresh user to get latest balance
    try:
        refreshed = services.UserService.get_by_id(user_id)
        if refreshed:
            user = refreshed
    except Exception:
        pass

    tomatos = user.get("tomatos", 0)

    ui_components.page_header(
        title="Peer Logistics",
        subtitle="Earn and spend Tomato Credits by helping peers deliver items across campus.",
        icon="truck",
    )

    # Balance banner
    st.markdown(
        f"""
<div class="premium-card" style="border-left:4px solid #DD0426;padding:1rem 1.25rem;
     display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
  <div>
    <div style="font-size:1.5rem;font-weight:700;color:#EFF6EE;display:flex;align-items:center;gap:10px;">
      <i data-lucide="wallet" style="width:22px;color:#DD0426;"></i>
      {tomatos} <span style="font-size:1rem;color:#9197AE;font-weight:500;">Tomato Credits</span>
    </div>
    <div style="font-size:0.8rem;color:#9197AE;margin-top:4px;">
      Creating a request deducts credits · Completing a delivery earns credits
    </div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    tab_open, tab_my_req, tab_my_del, tab_create, tab_history = st.tabs([
        "Open Requests",
        "My Requests",
        "My Deliveries",
        "Create Request",
        "Tomato History",
    ])

    try:
        all_requests = services.ParcelService.get_all() or []
    except Exception:
        all_requests = []

    # ── Tab 1: Open Requests ─────────────────────────────────────────────────
    with tab_open:
        open_reqs = [
            r for r in all_requests
            if r.get("status") == "Created"
            and r.get("requester_id") != user_id
        ]
        if open_reqs:
            for req in open_reqs:
                tomatoes_offered = req.get("tomatos_offered", req.get("tomatoes_offered", 5))
                st.markdown(
                    f"""
<div class="premium-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
    <h4 style="margin:0;color:#EFF6EE;font-size:1.05rem;">{req.get('title','')}</h4>
    {_tomato_badge(tomatoes_offered)}
  </div>
  <p style="margin:0 0 10px 0;color:#9197AE;font-size:0.875rem;line-height:1.5;">
    {req.get('description','')}
  </p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;
       background:rgba(26,32,51,0.6);border-radius:8px;padding:10px;border:1px solid rgba(145,151,174,0.08);">
    <div>
      <div style="font-size:0.7rem;color:#9197AE;text-transform:uppercase;font-weight:600;margin-bottom:3px;">Pickup</div>
      <div style="color:#EFF6EE;font-size:0.875rem;display:flex;align-items:center;gap:4px;">
        <i data-lucide="map-pin" style="width:12px;"></i> {req.get('pickup_location','')}
      </div>
    </div>
    <div>
      <div style="font-size:0.7rem;color:#9197AE;text-transform:uppercase;font-weight:600;margin-bottom:3px;">Delivery</div>
      <div style="color:#EFF6EE;font-size:0.875rem;display:flex;align-items:center;gap:4px;">
        <i data-lucide="navigation" style="width:12px;"></i> {req.get('delivery_location','')}
      </div>
    </div>
  </div>
  <div class="info-row" style="margin-top:10px;justify-content:space-between;font-size:0.8rem;">
    <span>By <strong>{req.get('requester_name','')}</strong></span>
    <span>{str(req.get('created_at',''))[:10]}</span>
  </div>
</div>""",
                    unsafe_allow_html=True,
                )
                btn_col, _ = st.columns([3, 7])
                with btn_col:
                    if st.button("Accept Request", key=f"open_accept_{req['id']}", type="primary", use_container_width=True):
                        try:
                            ok = services.ParcelService.accept_request(req["id"], user_id)
                            if ok:
                                st.success("Request accepted! Check My Deliveries to update progress.")
                                ui_components.safe_rerun()
                            else:
                                st.error("Could not accept — it may have been taken.")
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            ui_components.render_empty_state(
                "No open requests",
                "Check back later — peer delivery requests will appear here.",
                icon="inbox",
            )

    # ── Tab 2: My Requests ───────────────────────────────────────────────────
    with tab_my_req:
        my_reqs = [r for r in all_requests if r.get("requester_id") == user_id]
        if my_reqs:
            for req in my_reqs:
                status = req.get("status", "")
                helper_name = req.get("helper_name") or req.get("helper_id")
                helper_text = f"Helper: <strong>{helper_name}</strong>" if helper_name else "Waiting for a helper…"
                tomatoes_offered = req.get("tomatos_offered", req.get("tomatoes_offered", 5))
                st.markdown(
                    f"""
<div class="premium-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
    <h4 style="margin:0;color:#EFF6EE;font-size:1.05rem;">{req.get('title','')}</h4>
    {_status_badge(status)}
  </div>
  <p style="margin:0 0 8px 0;color:#9197AE;font-size:0.875rem;">{req.get('description','')}</p>
  <div class="info-row" style="font-size:0.8rem;flex-wrap:wrap;gap:8px;">
    <span>{helper_text}</span>
    <span>· Pickup: <strong>{req.get('pickup_location','')}</strong></span>
    <span>· Delivery: <strong>{req.get('delivery_location','')}</strong></span>
    <span>· Offered: {_tomato_badge(tomatoes_offered)}</span>
  </div>
</div>""",
                    unsafe_allow_html=True,
                )
                if status == "Created":
                    cancel_col, _ = st.columns([2, 8])
                    with cancel_col:
                        if st.button("Cancel Request", key=f"myreq_cancel_{req['id']}", use_container_width=True):
                            try:
                                services.ParcelService.update_status(req["id"], "Cancelled")
                                st.success("Request cancelled.")
                                ui_components.safe_rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
        else:
            ui_components.render_empty_state(
                "No requests yet",
                "Delivery requests you create will show up here.",
                icon="file-text",
            )

    # ── Tab 3: My Deliveries ─────────────────────────────────────────────────
    with tab_my_del:
        my_dels = [r for r in all_requests if r.get("helper_id") == user_id]
        if my_dels:
            for req in my_dels:
                status = req.get("status", "")
                tomatoes_offered = req.get("tomatos_offered", req.get("tomatoes_offered", 5))
                st.markdown(
                    f"""
<div class="premium-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
    <h4 style="margin:0;color:#EFF6EE;font-size:1.05rem;">{req.get('title','')}</h4>
    {_status_badge(status)}
  </div>
  <div class="info-row" style="font-size:0.8rem;flex-wrap:wrap;gap:8px;">
    <span>Requester: <strong>{req.get('requester_name','')}</strong></span>
    <span>· Pickup: <strong>{req.get('pickup_location','')}</strong></span>
    <span>· Delivery: <strong>{req.get('delivery_location','')}</strong></span>
    <span>· Reward: {_tomato_badge(tomatoes_offered)}</span>
  </div>
</div>""",
                    unsafe_allow_html=True,
                )
                ui_components.render_timeline(status)
                btn_col, _ = st.columns([3, 7])
                with btn_col:
                    if status == "Accepted":
                        if st.button("Mark Picked Up", key=f"mydel_pickup_{req['id']}", type="primary", use_container_width=True):
                            try:
                                services.ParcelService.update_status(req["id"], "Picked Up")
                                st.success("Status updated to Picked Up.")
                                ui_components.safe_rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    elif status == "Picked Up":
                        if st.button("Mark Delivered", key=f"mydel_deliver_{req['id']}", type="primary", use_container_width=True):
                            try:
                                services.ParcelService.update_status(req["id"], "Delivered")
                                st.success(f"Delivered! +{tomatoes_offered} Tomato Credits earned.")
                                ui_components.safe_rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    elif status == "Delivered":
                        st.markdown(
                            '<span style="color:#22C55E;font-size:0.85rem;font-weight:600;">'
                            '<i data-lucide="check-circle" style="width:13px;display:inline-block;vertical-align:middle;"></i>'
                            ' Completed — credits received</span>',
                            unsafe_allow_html=True,
                        )
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                "No deliveries yet",
                "Accept open requests from the Open Requests tab to start earning Tomato Credits.",
                icon="package",
            )

    # ── Tab 4: Create Request ────────────────────────────────────────────────
    with tab_create:
        st.markdown(
            "<h3 style='margin-top:0;color:#EFF6EE;font-size:1.15rem;'>Create Delivery Request</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='color:#9197AE;font-size:0.875rem;'>Your current balance: "
            f"<strong style='color:#EFF6EE;'>{tomatos} 🍅</strong></p>",
            unsafe_allow_html=True,
        )

        if tomatos < 1:
            st.error("You need at least 1 Tomato Credit to create a request. Earn credits by completing deliveries.")
        else:
            with st.form("create_logistics_form", clear_on_submit=True):
                req_title = st.text_input("Title *", placeholder="e.g. Return library book to Block C")
                req_desc = st.text_area(
                    "Description *",
                    placeholder="Details for the helper: item description, who to contact, any special instructions.",
                )
                c1, c2 = st.columns(2)
                with c1:
                    req_pickup = st.text_input("Pickup Location *", placeholder="e.g. Hostel Block A, Room 204")
                with c2:
                    req_delivery = st.text_input("Delivery Location *", placeholder="e.g. Library Main Desk")

                req_tomatoes = st.number_input(
                    f"Tomato Credits Offered (your balance: {tomatos})",
                    min_value=1,
                    max_value=tomatos,
                    value=min(5, tomatos),
                    step=1,
                )

                submitted = st.form_submit_button("Submit Request", type="primary")
                if submitted:
                    if not req_title or not req_desc or not req_pickup or not req_delivery:
                        st.error("Please fill in all required fields (*).")
                    elif req_tomatoes > tomatos:
                        st.error(f"Insufficient balance. You have {tomatos} 🍅 but offered {req_tomatoes}.")
                    else:
                        try:
                            result = services.ParcelService.create_request(
                                requester_id=user_id,
                                title=req_title,
                                description=req_desc,
                                pickup_location=req_pickup,
                                delivery_location=req_delivery,
                                tomatoes_offered=int(req_tomatoes),
                            )
                            # Note: ParcelService.create_request checks user.get("tomatoes", 0)
                            # which maps to the "tomatoes" column; our local balance check
                            # uses user.get("tomatos") which is the session key — both valid paths
                            if result:
                                st.success(f"Request '{req_title}' created! {req_tomatoes} 🍅 held from balance.")
                                ui_components.safe_rerun()
                            else:
                                st.error("Failed to create request. Check your balance and try again.")
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ── Tab 5: Tomato History ────────────────────────────────────────────────
    with tab_history:
        try:
            transactions = services.TomatoService.get_transactions(user_id) or []
        except Exception:
            transactions = []

        if transactions:
            st.markdown(
                "<h4 style='color:#EFF6EE;margin-top:0;'>Transaction History</h4>",
                unsafe_allow_html=True,
            )
            running = 0
            for t in reversed(transactions):
                running += t.get("amount", 0)
            st.markdown(
                f"<p style='color:#9197AE;font-size:0.85rem;margin-bottom:1rem;'>"
                f"Running balance: <strong style='color:#EFF6EE;'>{tomatos} 🍅</strong></p>",
                unsafe_allow_html=True,
            )
            for t in transactions:
                _txn_row(t)
        else:
            ui_components.render_empty_state(
                "No transactions yet",
                "Tomato Credit transactions will appear here as you create and complete deliveries.",
                icon="wallet",
            )

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
