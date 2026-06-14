import streamlit as st
import datetime
import os
import uuid
import database
import ui_components

# Use shared uploads directory
UPLOAD_DIR = r"c:\Users\notgu\OneDrive\Documents\campus\uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def render(user: dict):
    """
    Renders the Lost & Found section.
    """
    ui_components.page_header(
        title="Lost & Found",
        subtitle="Report items lost or found on campus and claim your misplaced belongings.",
        icon="package"
    )
    
    user_id = user["id"]
    
    tab_explore, tab_report = st.tabs([
        "Explore Items",
        "Report Lost / Found Item"
    ])
    
    items = database.get_lost_found_items()
    
    # --- Tab 1: Explore Items ---
    with tab_explore:
        col_search, col_type, col_cat = st.columns([4, 3, 3])
        with col_search:
            search_query = st.text_input("Search items...", placeholder="Search by item name or description", key="lf_search")
        with col_type:
            type_filter = st.selectbox("Report Type", ["All Items", "Lost", "Found"])
        with col_cat:
            cat_filter = st.selectbox("Category", ["All Categories", "Electronics", "IDs", "Books", "Accessories", "Other"])
            
        # Apply filters
        filtered_items = items
        if search_query:
            filtered_items = [
                i for i in filtered_items 
                if search_query.lower() in i["title"].lower() 
                or search_query.lower() in i["description"].lower()
            ]
        if type_filter != "All Items":
            filtered_items = [i for i in filtered_items if i["type"] == type_filter]
        if cat_filter != "All Categories":
            filtered_items = [i for i in filtered_items if i["category"] == cat_filter]
            
        # Filter out resolved items for general viewing
        visible_items = [i for i in filtered_items if i["status"] != "Resolved"]
        
        if visible_items:
            res_cols = st.columns(2)
            for idx, item in enumerate(visible_items):
                col = res_cols[idx % 2]
                with col:
                    # Determine type badge styling
                    is_lost = item["type"] == "Lost"
                    badge_color = "rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3);" if is_lost else "rgba(34, 197, 94, 0.15); color: #4ADE80; border: 1px solid rgba(34, 197, 94, 0.3);"
                    
                    col.markdown(f"""
                    <div class="premium-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div>
                                <span class="category-tag">{item['category']}</span>
                                <h4 style="margin: 6px 0 0 0; color: #FFFFFF; font-size: 1.1rem;">{item['title']}</h4>
                            </div>
                            <span class="priority-badge" style="{badge_color}">{item['type']}</span>
                        </div>
                        
                        <p style="margin: 0 0 10px 0; color: #E2E8F0; font-size: 0.9rem; line-height: 1.4; height: 50px; overflow: hidden; text-overflow: ellipsis;">
                            {item['description']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display uploaded image if path exists, otherwise display a small alert
                    img_path = item["image_url"]
                    if img_path and os.path.exists(img_path):
                        try:
                            col.image(img_path, use_container_width=True)
                        except Exception:
                            pass
                    elif img_path and img_path.startswith("http"):
                        try:
                            col.image(img_path, use_container_width=True)
                        except Exception:
                            pass
                            
                    # Location and contact info
                    col.markdown(f"""
                    <div style="padding: 0 10px 10px 10px;">
                        <div class="info-row" style="font-size: 0.82rem; margin-top: 6px;">
                            <span style="display:flex; align-items:center; gap: 4px;"><i data-lucide="map-pin" style="width:12px;"></i> Last Seen: <strong>{item['location']}</strong></span>
                        </div>
                        <div class="info-row" style="font-size: 0.82rem; margin-top: 4px; justify-content: space-between;">
                            <span>Post by: <strong>{item['reporter_name']}</strong></span>
                            <span>{item['created_at'][:10]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    btn_col1, btn_col2 = col.columns(2)
                    with btn_col1:
                        # If current user reported it, let them mark it as resolved
                        if item["reporter_id"] == user_id:
                            if st.button("Mark Resolved", key=f"resolve_lf_{item['id']}", type="primary", use_container_width=True):
                                database.update_lost_found_status(item["id"], "Resolved")
                                st.success("Marked as resolved!")
                                ui_components.safe_rerun()
                        else:
                            # Claim or Contact button
                            button_label = "Claim Item" if is_lost else "Contact Poster"
                            if st.button(button_label, key=f"claim_lf_{item['id']}", type="primary", use_container_width=True):
                                # Send notification to the reporter
                                contact_msg = f"{user['name']} ({user['email']}) is claiming/inquiring about your item '{item['title']}'. Please contact them."
                                database.add_notification(
                                    user_id=item["reporter_id"],
                                    title=f"Lost & Found Claim: {item['title']}",
                                    content=contact_msg
                                )
                                database.mock_db.save()
                                st.success("Poster has been notified! They will contact you shortly.")
                    with btn_col2:
                        # Empty spacer or secondary info
                        st.markdown(f"<span style='font-size:0.75rem; color:#94A3B8; text-align:right; display:block; padding-top:10px;'>Post ID: {item['id'][:8]}</span>", unsafe_allow_html=True)
                    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 15px 0;'>", unsafe_allow_html=True)
        else:
            ui_components.render_empty_state(
                title="No lost & found reports",
                description="Everything is in its place! Or try modifying filters to see items.",
                icon="package"
            )
            
    # --- Tab 2: Report Lost / Found Item ---
    with tab_report:
        st.markdown("<h3 style='margin-top: 0; color: #FFFFFF; font-size: 1.2rem;'>Report a Misplaced Item</h3>", unsafe_allow_html=True)
        
        with st.form("lost_found_report_form", clear_on_submit=True):
            lf_title = st.text_input("Item Name *", placeholder="e.g. Red water bottle, House key set")
            
            col_type, col_cat = st.columns(2)
            with col_type:
                lf_type = st.selectbox("Report Type *", ["Lost", "Found"])
            with col_cat:
                lf_cat = st.selectbox("Category *", ["Electronics", "IDs", "Books", "Accessories", "Other"])
                
            lf_desc = st.text_area("Item Description *", placeholder="Describe shape, color, marks, size, content. Mention any details that only the owner would know.")
            lf_location = st.text_input("Location *", placeholder="e.g. Near Cafeteria or Main Auditorium Block 3")
            
            uploaded_img = st.file_uploader("Upload Item Image (Optional)", type=["jpg", "png", "jpeg"])
            
            submit_btn = st.form_submit_button("Submit Report", type="primary")
            
            if submit_btn:
                if not lf_title or not lf_desc or not lf_location:
                    st.error("Please fill in all mandatory fields (*).")
                else:
                    image_path = None
                    if uploaded_img:
                        # Save file locally
                        safe_filename = f"lf_{uuid.uuid4().hex[:6]}_{uploaded_img.name}"
                        image_path = os.path.join(UPLOAD_DIR, safe_filename)
                        try:
                            with open(image_path, "wb") as f:
                                f.write(uploaded_img.getbuffer())
                        except Exception as e:
                            st.warning(f"Failed to save image: {e}")
                            image_path = None
                            
                    # Save report
                    database.report_lost_found_item(
                        title=lf_title,
                        description=lf_desc,
                        category=lf_cat,
                        item_type=lf_type,
                        location=lf_location,
                        image_url=image_path,
                        reporter_id=user_id,
                        reporter_name=user["name"]
                    )
                    st.success(f"Report for '{lf_title}' successfully published!")
                    ui_components.safe_rerun()

    # Refresh icons
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
