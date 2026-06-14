import streamlit as st
import datetime
import services
import ui_components

def render(user: dict):
    """
    Renders the Announcements Center.
    """
    ui_components.page_header(
        title="Announcements Center",
        subtitle="Stay updated with official college notices, placement alerts, and club announcements.",
        icon="megaphone"
    )
    
    user_id = user["id"]
    role = user["role"]
    
    # Check tabs: Notices Feed, Saved Notices, and Publish Notice (Admins/Club Admins only)
    tab_titles = ["Notice Board", "Saved Notices"]
    if role in ["admin", "club_admin"]:
        tab_titles.append("Publish Notice")
        
    tabs = st.tabs(tab_titles)
    
    announcements = services.AnnouncementService.get_all()
    
    # --- Tab 1: Notice Board (Feed) ---
    with tabs[0]:
        # Search & Filters
        col_search, col_cat, col_priority = st.columns([5, 3, 2])
        with col_search:
            search_query = st.text_input("Search notices...", placeholder="Search by title, author, or content", key="ann_search")
        with col_cat:
            category_filter = st.selectbox("Category", ["All Categories", "Academic", "Clubs", "Placements", "Hostel", "General"])
        with col_priority:
            priority_filter = st.selectbox("Priority", ["All Priorities", "High", "Medium", "Low"])
            
        # Sort by priority first (High > Medium > Low), then by date desc
        priority_rank = {"High": 0, "Medium": 1, "Low": 2}
        announcements_sorted = sorted(
            announcements,
            key=lambda a: (priority_rank.get(a.get("priority", "Low"), 2), a.get("created_at", ""))
        )

        # Apply filters
        filtered_anns = announcements_sorted
        if search_query:
            sq = search_query.lower()
            filtered_anns = [
                a for a in filtered_anns
                if sq in a.get("title", "").lower()
                or sq in a.get("content", "").lower()
                or sq in a.get("author_name", a.get("author", "")).lower()
            ]
        if category_filter != "All Categories":
            filtered_anns = [a for a in filtered_anns if a.get("category") == category_filter]
        if priority_filter != "All Priorities":
            filtered_anns = [a for a in filtered_anns if a.get("priority") == priority_filter]
            
        if filtered_anns:
            for ann in filtered_anns:
                priority_class = f"priority-{ann['priority'].lower()}"
                is_saved = services.AnnouncementService.is_saved(user_id, ann["id"])
                
                # HTML notice card
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div>
                            <span class="category-tag">{ann['category']}</span>
                            <h4 style="margin: 6px 0 0 0; color: #FFFFFF; font-size: 1.15rem;">{ann['title']}</h4>
                        </div>
                        <span class="priority-badge {priority_class}">{ann['priority']} Priority</span>
                    </div>
                    <p style="margin: 0; color: #E2E8F0; font-size: 0.95rem; line-height: 1.5; white-space: pre-line;">{ann['content']}</p>
                    <div class="info-row" style="margin-top: 12px; border-top: 1px solid #2D3748; padding-top: 8px; justify-content: space-between;">
                        <span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="user" style="width: 12px;"></i> Broadcasted by: <strong>{ann.get('author_name', ann.get('author', ''))}</strong></span>
                        <span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="clock" style="width: 12px;"></i> {str(ann.get('created_at',''))[:10]} {str(ann.get('created_at',''))[11:16]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Bookmark action button
                btn_col, _ = st.columns([2, 8])
                with btn_col:
                    if is_saved:
                        if st.button("Unsave Notice", key=f"unsave_{ann['id']}", use_container_width=True):
                            services.AnnouncementService.unsave(user_id, ann["id"])
                            st.success("Removed from Saved Notices!")
                            ui_components.safe_rerun()
                    else:
                        if st.button("Save Notice", key=f"save_{ann['id']}", use_container_width=True):
                            services.AnnouncementService.save(user_id, ann["id"])
                            st.success("Saved notice!")
                            ui_components.safe_rerun()
        else:
            ui_components.render_empty_state(
                title="No notices found",
                description="Try broadening your filters or search keywords.",
                icon="megaphone"
            )
            
    # --- Tab 2: Saved Notices ---
    with tabs[1]:
        saved_notices = services.AnnouncementService.get_user_saved(user_id)
        if saved_notices:
            for ann in saved_notices:
                priority_class = f"priority-{ann['priority'].lower()}"
                
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div>
                            <span class="category-tag">{ann['category']}</span>
                            <h4 style="margin: 6px 0 0 0; color: #FFFFFF; font-size: 1.15rem;">{ann['title']}</h4>
                        </div>
                        <span class="priority-badge {priority_class}">{ann['priority']} Priority</span>
                    </div>
                    <p style="margin: 0; color: #E2E8F0; font-size: 0.95rem; line-height: 1.5;">{ann['content']}</p>
                    <div class="info-row" style="margin-top: 12px; border-top: 1px solid #2D3748; padding-top: 8px; justify-content: space-between;">
                        <span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="user" style="width: 12px;"></i> By {ann.get('author_name', ann.get('author', ''))}</span>
                        <span style="display: flex; align-items: center; gap: 4px;"><i data-lucide="clock" style="width: 12px;"></i> {str(ann.get('created_at',''))[:10]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                btn_col, _ = st.columns([2, 8])
                with btn_col:
                    if st.button("Unsave Notice", key=f"unsave_tab_{ann['id']}", use_container_width=True):
                        services.AnnouncementService.unsave(user_id, ann["id"])
                        st.success("Notice unsaved.")
                        ui_components.safe_rerun()
        else:
            ui_components.render_empty_state(
                title="No saved notices",
                description="Bookmarked announcements will appear here for easy reference.",
                icon="bookmark"
            )
            
    # --- Tab 3: Publish Notice (Admins/Club Admins only) ---
    if role in ["admin", "club_admin"]:
        with tabs[2]:
            st.markdown("<h3 style='margin-top: 0; color: #FFFFFF; font-size: 1.2rem;'>Publish New Notice</h3>", unsafe_allow_html=True)
            
            with st.form("publish_notice_form", clear_on_submit=True):
                ann_title = st.text_input("Title *", placeholder="e.g. Spring 2026 Examination Guidelines")
                
                col_cat, col_prio = st.columns(2)
                with col_cat:
                    ann_category = st.selectbox("Category", ["Academic", "Clubs", "Placements", "Hostel", "General"])
                with col_prio:
                    ann_priority = st.selectbox("Priority Level", ["Low", "Medium", "High"])
                    
                ann_content = st.text_area("Notice Details *", placeholder="Write announcement content details here...")
                
                # Checkbox for author selection based on role
                author_options = [user["name"]]
                if role == "admin":
                    author_options.append("Office of Registrar")
                    author_options.append("University Administration")
                elif role == "club_admin":
                    author_options.append("Club Organizing Committee")
                ann_author = st.selectbox("Publish as *", author_options)
                
                submit_btn = st.form_submit_button("Broadcast Notice", type="primary")
                
                if submit_btn:
                    if not ann_title or not ann_content:
                        st.error("Please provide both a Title and Notice Content.")
                    else:
                        services.AnnouncementService.create(
                            title=ann_title,
                            content=ann_content,
                            category=ann_category,
                            priority=ann_priority,
                            author=ann_author,
                            author_id=user_id,
                        )
                        st.success(f"Announcement '{ann_title}' successfully published and broadcasted!")
                        ui_components.safe_rerun()

    # Refresh icons
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
