import streamlit as st
import datetime
import services
import ui_components

def render(user: dict):
    """
    Renders the Peer Logistics page.
    """
    # Header showing tomatos balance immediately
    user_id = user["id"]
    
    # Reload user info to keep tomatos up to date
    refreshed_user = services.UserService.get_by_id(user_id)
    if refreshed_user:
        user = refreshed_user
        
    tomatos = user["tomatos"]
    
    ui_components.page_header(
        title="Peer Logistics",
        subtitle=f"Earn and spend tomatos by helping peers deliver parcels, books, or notes across campus.",
        icon="truck"
    )
    
    # Display tomatos balance banner
    st.markdown(f"""
    <div class="premium-card" style="border-left: 4px solid #3B82F6; padding: 1rem; display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
            <h4 style="margin: 0; color: #FFFFFF;">Tomatos Balance: <strong>{tomatos} Tomatos</strong></h4>
            <span style="font-size: 0.82rem; color: #94A3B8;">Creating requests costs <strong>5 tomatos</strong>. Completing deliveries earns <strong>5 tomatos</strong>.</span>
        </div>
        <div style="background-color: rgba(59, 130, 246, 0.15); border-radius: 6px; padding: 6px 12px; font-weight: 600; color: #60A5FA; font-size: 0.9rem;">
            No Money Involved
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_open, tab_deliveries, tab_requests, tab_create, tab_ledger = st.tabs([
        "Open Delivery Jobs",
        "My Jobs (Helper)",
        "My Requests (Requester)",
        "Create Request",
        "Tomato Ledger"
    ])
    
    all_requests = services.ParcelService.get_all()
    
    # --- Tab 1: Open Delivery Jobs ---
    with tab_open:
        # Filter requests where status is 'Request Created' and requester is NOT current user
        open_jobs = [r for r in all_requests if r["status"] == "Request Created" and r["requester_id"] != user_id]
        
        if open_jobs:
            for job in open_jobs:
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
                        <h4 style="margin: 0; color: #FFFFFF; font-size: 1.1rem;">{job['title']}</h4>
                        <span class="priority-badge priority-medium" style="background-color: rgba(34, 197, 94, 0.15); color: #22C55E; border-color: rgba(34, 197, 94, 0.3);">+{job['tomatos_offered']} Tomatos Bounty</span>
                    </div>
                    <p style="margin: 0; color: #E2E8F0; font-size: 0.9rem; line-height: 1.4;">{job['description']}</p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; background-color: rgba(45, 55, 72, 0.2); border-radius: 6px; padding: 8px 12px; border: 1px solid rgba(255,255,255,0.02);">
                        <div>
                            <span style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; display:block;">Pickup Location</span>
                            <span style="color: #FFFFFF; font-size: 0.88rem; font-weight: 500; display: flex; align-items:center; gap: 4px;"><i data-lucide="map-pin" style="width: 12px;"></i> {job['pickup_location']}</span>
                        </div>
                        <div>
                            <span style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; display:block;">Delivery Location</span>
                            <span style="color: #FFFFFF; font-size: 0.88rem; font-weight: 500; display: flex; align-items:center; gap: 4px;"><i data-lucide="navigation" style="width: 12px;"></i> {job['delivery_location']}</span>
                        </div>
                    </div>
                    
                    <div class="info-row" style="margin-top: 8px; justify-content: space-between;">
                        <span>Requested by: <strong>{job['requester_name']}</strong></span>
                        <span>{job['created_at'][:10]} {job['created_at'][11:16]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Accept button
                btn_col, _ = st.columns([3, 7])
                with btn_col:
                    if st.button("Accept Delivery Job", key=f"accept_job_{job['id']}", type="primary", use_container_width=True):
                        success = services.ParcelService.accept_request(job["id"], user_id, user["name"])
                        if success:
                            st.success("You have accepted the job! Go to 'My Jobs' to update progress.")
                            ui_components.safe_rerun()
                        else:
                            st.error("Could not accept request. It might have been taken.")
        else:
            ui_components.render_empty_state(
                title="No open delivery jobs",
                description="Check back later or post your own package request to test the peer network.",
                icon="truck"
            )
            
    # --- Tab 2: My Jobs (Helper role) ---
    with tab_deliveries:
        helper_jobs = [r for r in all_requests if r["helper_id"] == user_id]
        if helper_jobs:
            for job in helper_jobs:
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
                        <h4 style="margin: 0; color: #FFFFFF; font-size: 1.1rem;">{job['title']}</h4>
                        <span class="category-tag">Status: {job['status']}</span>
                    </div>
                    <p style="margin: 0 0 10px 0; color: #94A3B8; font-size: 0.9rem;">{job['description']}</p>
                    
                    <div class="info-row" style="margin-bottom: 12px;">
                        <span>Requester: <strong>{job['requester_name']}</strong></span>
                        <span>| Pickup: <strong>{job['pickup_location']}</strong></span>
                        <span>| Delivery: <strong>{job['delivery_location']}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render timeline for job status
                ui_components.render_timeline(job["status"])
                
                # Helper status controls
                status = job["status"]
                btn_col1, btn_col2 = st.columns([3, 7])
                with btn_col1:
                    if status == "Matched":
                        if st.button("Collect Parcel (Picked Up)", key=f"job_pickup_{job['id']}", type="primary", use_container_width=True):
                            services.ParcelService.update_status(job["id"], "Picked Up")
                            st.success("Collected! Status updated to 'Picked Up'.")
                            ui_components.safe_rerun()
                    elif status == "Picked Up":
                        if st.button("Complete Delivery", key=f"job_deliver_{job['id']}", type="primary", use_container_width=True):
                            services.ParcelService.update_status(job["id"], "Delivered")
                            st.success("Delivery completed successfully! +5 tomatos received.")
                            ui_components.safe_rerun()
                    elif status == "Delivered":
                        st.markdown("<span style='color: #22C55E; font-size: 0.85rem; font-weight: 600;'><i data-lucide='check-circle' style='width:12px; display:inline-block;'></i> Completed & Tomatos Received (+5)</span>", unsafe_allow_html=True)
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No helper assignments",
                description="Delivery requests you accept from the 'Open Delivery Jobs' list will show up here.",
                icon="package"
            )
            
    # --- Tab 3: My Requests (Requester role) ---
    with tab_requests:
        requester_jobs = [r for r in all_requests if r["requester_id"] == user_id]
        if requester_jobs:
            for job in requester_jobs:
                helper_text = f"Helper: <strong>{job['helper_name']}</strong>" if job["helper_id"] else "Helper: <em>Waiting for volunteer...</em>"
                
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
                        <h4 style="margin: 0; color: #FFFFFF; font-size: 1.1rem;">{job['title']}</h4>
                        <span class="category-tag">Status: {job['status']}</span>
                    </div>
                    <p style="margin: 0 0 10px 0; color: #94A3B8; font-size: 0.9rem;">{job['description']}</p>
                    
                    <div class="info-row" style="margin-bottom: 12px;">
                        <span>{helper_text}</span>
                        <span>| Pickup: <strong>{job['pickup_location']}</strong></span>
                        <span>| Delivery: <strong>{job['delivery_location']}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render timeline for job status
                ui_components.render_timeline(job["status"])
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No requests created",
                description="Package delivery requests you create will appear here.",
                icon="file-text"
            )
            
    # --- Tab 4: Create Request ---
    with tab_create:
        st.markdown("<h3 style='margin-top: 0; color: #FFFFFF; font-size: 1.2rem;'>Create Package Delivery Request</h3>", unsafe_allow_html=True)
        
        if tomatos < 5:
            st.error("Insufficient tomato balance. You need at least 5 tomatos to request a delivery. Earn tomatos by helping peers with their packages.")
        else:
            with st.form("create_logistics_form", clear_on_submit=True):
                req_title = st.text_input("Item/Package Title *", placeholder="e.g. Return Chemistry Lab manual")
                req_desc = st.text_area("Item Description & Details *", placeholder="Provide helper with details: where to pick up, who to look for, shape/size of package.")
                
                col_p, col_d = st.columns(2)
                with col_p:
                    req_pickup = st.text_input("Pickup Point *", placeholder="e.g. Hostels Gate or Block A Lobby")
                with col_d:
                    req_delivery = st.text_input("Delivery Destination *", placeholder="e.g. Library Desk or Block C Rm 102")
                    
                st.info("Bounty holding: 5 tomatos will be held from your account and transferred to helper upon completion.")
                
                submit_btn = st.form_submit_button("Submit Request", type="primary")
                
                if submit_btn:
                    if not req_title or not req_desc or not req_pickup or not req_delivery:
                        st.error("Please fill in all mandatory fields (*).")
                    else:
                        res = services.ParcelService.create_request(
                            requester_id=user_id,
                            requester_name=user["name"],
                            title=req_title,
                            description=req_desc,
                            pickup_location=req_pickup,
                            delivery_location=req_delivery,
                            tomatos_offered=5
                        )
                        if res:
                            st.success(f"Delivery request '{req_title}' created successfully! 5 tomatos held.")
                            ui_components.safe_rerun()
                        else:
                            st.error("Request creation failed. Please check your tomato balance.")
                            
    # --- Tab 5: Tomato Ledger ---
    with tab_ledger:
        transactions = services.TomatoService.get_transactions(user_id)
        if transactions:
            st.markdown("<h4 style='color:#FFFFFF; margin-top:0;'>Transaction History</h4>", unsafe_allow_html=True)
            for t in transactions:
                # Sign coloring
                is_positive = t["amount"] > 0
                sign = "+" if is_positive else ""
                color = "#22C55E" if is_positive else "#EF4444"
                bg_color = "rgba(34, 197, 94, 0.05)" if is_positive else "rgba(239, 68, 68, 0.05)"
                border_color = "rgba(34, 197, 94, 0.15)" if is_positive else "rgba(239, 68, 68, 0.15)"
                
                st.markdown(f"""
                <div class="premium-card" style="padding: 0.8rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; background-color: {bg_color}; border-color: {border_color};">
                    <div>
                        <span style="font-weight:600; color: #FFFFFF; font-size: 0.9rem;">{t['description']}</span>
                        <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px;">{t['created_at'][:10]} {t['created_at'][11:16]}</div>
                    </div>
                    <span style="font-size: 1.1rem; font-weight: 700; color: {color};">{sign}{t['amount']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No transaction logs",
                description="Logistics requests and delivery tomatos transfers will show up here.",
                icon="wallet"
            )

    # Force load icons
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
