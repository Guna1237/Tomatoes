import streamlit as st
import datetime
import os
import services
import ui_components

# Ensure local uploads directory exists
UPLOAD_DIR = r"c:\Users\notgu\OneDrive\Documents\campus\uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def render(user: dict):
    """
    Renders the Resource Hub.
    """
    ui_components.page_header(
        title="Resource Hub",
        subtitle="Share and download lecture notes, past exam papers, slides, and study guides.",
        icon="folder-open"
    )
    
    user_id = user["id"]
    
    tab_explore, tab_bookmarks, tab_upload = st.tabs([
        "Explore Resources",
        "Bookmarked Resources",
        "Share a Resource"
    ])
    
    resources = services.ResourceService.get_all()
    
    # --- Tab 1: Explore Resources ---
    with tab_explore:
        col_search, col_course, col_cat = st.columns([4, 3, 3])
        with col_search:
            search_query = st.text_input("Search resources...", placeholder="Search by title or course name", key="res_search")
        with col_course:
            course_codes = ["All Courses"] + sorted(list(set([r["course_code"] for r in resources])))
            course_filter = st.selectbox("Course Code", course_codes)
        with col_cat:
            cat_filter = st.selectbox("Resource Type", ["All Types", "Notes", "PYQs", "PPTs", "PDFs", "Study guides"])
            
        # Apply filters
        filtered_res = resources
        if search_query:
            filtered_res = [
                r for r in filtered_res 
                if search_query.lower() in r["title"].lower() 
                or search_query.lower() in r["course_name"].lower()
            ]
        if course_filter != "All Courses":
            filtered_res = [r for r in filtered_res if r["course_code"] == course_filter]
        if cat_filter != "All Types":
            filtered_res = [r for r in filtered_res if r["category"] == cat_filter]
            
        if filtered_res:
            res_cols = st.columns(2)
            for idx, res in enumerate(filtered_res):
                col = res_cols[idx % 2]
                with col:
                    is_bookmarked = services.ResourceService.is_bookmarked(user_id, res["id"])
                    
                    # Icons mapping
                    cat_icons = {
                        "Notes": "book-open",
                        "PYQs": "help-circle",
                        "PPTs": "presentation",
                        "PDFs": "file",
                        "Study guides": "compass"
                    }
                    icon = cat_icons.get(res["category"], "file")
                    
                    col.markdown(f"""
                    <div class="premium-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <div style="background-color: rgba(59, 130, 246, 0.1); border-radius: 6px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: #3B82F6;">
                                    <i data-lucide="{icon}" style="width: 18px; height: 18px;"></i>
                                </div>
                                <div>
                                    <h4 style="margin: 0; color: #FFFFFF; font-size: 1.05rem;">{res['title']}</h4>
                                    <span style="font-size: 0.8rem; color: #94A3B8;">{res['course_code']} • {res['course_name']}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="info-row" style="margin-top: 10px; margin-bottom: 12px; justify-content: space-between; font-size: 0.8rem;">
                            <span>Uploaded by: <strong>{res['uploader_name']}</strong></span>
                            <span>{res['created_at'][:10]}</span>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: 10px; font-size: 0.8rem; color: #94A3B8;">
                            <span><i data-lucide="bookmark" style="width:12px; display:inline-block;"></i> {res['bookmarks_count']} Bookmarks</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Interactivity Actions row
                    act_col1, act_col2 = col.columns(2)
                    with act_col1:
                        # Bookmark toggle
                        if is_bookmarked:
                            if st.button("Remove Bookmark", key=f"unbm_{res['id']}", use_container_width=True):
                                services.ResourceService.unbookmark(user_id, res["id"])
                                st.success("Removed bookmark.")
                                ui_components.safe_rerun()
                        else:
                            if st.button("Bookmark Resource", key=f"bm_{res['id']}", use_container_width=True):
                                services.ResourceService.bookmark(user_id, res["id"])
                                st.success("Bookmarked resource!")
                                ui_components.safe_rerun()
                                
                    with act_col2:
                        # Resolve physical path vs URL download
                        file_path = res["file_url"]
                        file_name = res["title"] + (".pdf" if res["category"] == "PDFs" else ".zip")
                        
                        if os.path.exists(file_path):
                            try:
                                with open(file_path, "rb") as f:
                                    file_bytes = f.read()
                                st.download_button(
                                    label="Download Resource",
                                    data=file_bytes,
                                    file_name=os.path.basename(file_path),
                                    key=f"dl_{res['id']}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.button("Download Failed", key=f"dl_err_{res['id']}", disabled=True, use_container_width=True)
                        else:
                            # If mock URL, download dummy template PDF
                            dummy_pdf = b"%PDF-1.4 ... Dummy PDF for CampusConnect demonstration ..."
                            st.download_button(
                                label="Download (Mock)",
                                data=dummy_pdf,
                                file_name=f"{res['title'].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                key=f"dl_mock_{res['id']}",
                                use_container_width=True
                            )
        else:
            ui_components.render_empty_state(
                title="No resources found",
                description="Try filtering by another course or sharing your own documents.",
                icon="folder-open"
            )
            
    # --- Tab 2: Bookmarked Resources ---
    with tab_bookmarks:
        bookmarked_res = services.ResourceService.get_user_bookmarked(user_id)
        if bookmarked_res:
            res_cols = st.columns(2)
            for idx, res in enumerate(bookmarked_res):
                col = res_cols[idx % 2]
                with col:
                    cat_icons = {
                        "Notes": "book-open",
                        "PYQs": "help-circle",
                        "PPTs": "presentation",
                        "PDFs": "file",
                        "Study guides": "compass"
                    }
                    icon = cat_icons.get(res["category"], "file")
                    
                    col.markdown(f"""
                    <div class="premium-card">
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                            <div style="background-color: rgba(168, 85, 247, 0.1); border-radius: 6px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; color: #A855F7;">
                                <i data-lucide="{icon}" style="width: 18px; height: 18px;"></i>
                            </div>
                            <div>
                                <h4 style="margin: 0; color: #FFFFFF; font-size: 1.05rem;">{res['title']}</h4>
                                <span style="font-size: 0.8rem; color: #94A3B8;">{res['course_code']} • {res['course_name']}</span>
                            </div>
                        </div>
                        
                        <div class="info-row" style="margin-top: 10px; margin-bottom: 12px; justify-content: space-between; font-size: 0.8rem;">
                            <span>Uploaded by: <strong>{res['uploader_name']}</strong></span>
                            <span>{res['created_at'][:10]}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    act_col1, act_col2 = col.columns(2)
                    with act_col1:
                        if st.button("Remove Bookmark", key=f"unbm_tab_{res['id']}", use_container_width=True):
                            services.ResourceService.unbookmark(user_id, res["id"])
                            st.success("Bookmark removed.")
                            ui_components.safe_rerun()
                    with act_col2:
                        file_path = res["file_url"]
                        if os.path.exists(file_path):
                            try:
                                with open(file_path, "rb") as f:
                                    file_bytes = f.read()
                                st.download_button(
                                    label="Download Resource",
                                    data=file_bytes,
                                    file_name=os.path.basename(file_path),
                                    key=f"dl_tab_{res['id']}",
                                    use_container_width=True
                                )
                            except Exception:
                                st.button("Download Error", key=f"dl_err_tab_{res['id']}", disabled=True, use_container_width=True)
                        else:
                            dummy_pdf = b"%PDF-1.4 ... Dummy PDF for CampusConnect demonstration ..."
                            st.download_button(
                                label="Download (Mock)",
                                data=dummy_pdf,
                                file_name=f"{res['title'].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                key=f"dl_mock_tab_{res['id']}",
                                use_container_width=True
                            )
        else:
            ui_components.render_empty_state(
                title="No bookmarked resources",
                description="Bookmarked lecture slides, question papers, and study guides will appear here.",
                icon="bookmark"
            )
            
    # --- Tab 3: Upload Resource ---
    with tab_upload:
        st.markdown("<h3 style='margin-top: 0; color: #FFFFFF; font-size: 1.2rem;'>Share Academic Material</h3>", unsafe_allow_html=True)
        
        with st.form("upload_resource_form", clear_on_submit=True):
            res_title = st.text_input("Material Title *", placeholder="e.g. DSA Lecture notes 1 to 10")
            
            col_code, col_name = st.columns(2)
            with col_code:
                res_code = st.text_input("Course Code *", placeholder="e.g. CS-201")
            with col_name:
                res_name = st.text_input("Course Name *", placeholder="e.g. Data Structures")
                
            res_cat = st.selectbox("Material Category *", ["Notes", "PYQs", "PPTs", "PDFs", "Study guides"])
            
            uploaded_file = st.file_uploader("Upload File (PDF, PPT, ZIP, DOC) *", type=["pdf", "ppt", "pptx", "zip", "doc", "docx"])
            
            submit_btn = st.form_submit_button("Upload and Share", type="primary")
            
            if submit_btn:
                if not res_title or not res_code or not res_name or not uploaded_file:
                    st.error("Please fill in all mandatory fields (*) and upload a file.")
                else:
                    # Save file locally in our uploads directory
                    safe_filename = f"{uuid.uuid4().hex[:6]}_{uploaded_file.name}"
                    local_path = os.path.join(UPLOAD_DIR, safe_filename)
                    
                    try:
                        with open(local_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        # Save resource metadata into DB
                        services.ResourceService.upload(
                            title=res_title,
                            course_code=res_code,
                            course_name=res_name,
                            category=res_cat,
                            file_url=local_path,
                            uploader_id=user_id,
                            uploader_name=user["name"]
                        )
                        st.success(f"Resource '{res_title}' successfully shared with the campus!")
                        ui_components.safe_rerun()
                    except Exception as e:
                        st.error(f"Failed to upload file: {e}")

    # Reload icons
    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
