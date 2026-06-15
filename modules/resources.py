import streamlit as st
import datetime
import os
import uuid
import services
import ui_components

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CAT_ICONS = {
    "Notes": "book-open",
    "PYQs": "help-circle",
    "PPTs": "presentation",
    "Lab Manuals": "flask-conical",
    "Study guides": "compass",
}


def _resource_card(col, res: dict, tab_prefix: str, user_id: str) -> None:
    icon = CAT_ICONS.get(res.get("category", ""), "file")
    col.markdown(
        f"""
<div class="premium-card">
  <div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;">
    <div style="background:rgba(59,130,246,0.1);border-radius:8px;width:38px;height:38px;
                display:flex;align-items:center;justify-content:center;color:#3B82F6;flex-shrink:0;">
      <i data-lucide="{icon}" style="width:18px;height:18px;"></i>
    </div>
    <div style="overflow:hidden;">
      <h4 style="margin:0;color:#EFF6EE;font-size:1rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        {res['title']}
      </h4>
      <div style="display:flex;gap:6px;margin-top:4px;flex-wrap:wrap;">
        <span class="category-tag">{res.get('course_code','')}</span>
        <span class="category-tag">{res.get('category','')}</span>
      </div>
    </div>
  </div>
  <div class="info-row" style="justify-content:space-between;font-size:0.8rem;">
    <span>by <strong>{res.get('uploader_name','')}</strong></span>
    <span>{str(res.get('created_at',''))[:10]}</span>
  </div>
  <div style="font-size:0.78rem;color:#9197AE;margin-top:6px;">
    <i data-lucide="bookmark" style="width:12px;display:inline-block;vertical-align:middle;"></i>
    {res.get('bookmarks_count', 0)} bookmarks
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    try:
        is_bookmarked = services.ResourceService.is_bookmarked(user_id, res["id"])
    except Exception:
        is_bookmarked = False

    act1, act2 = col.columns(2)
    with act1:
        if is_bookmarked:
            if st.button("Remove Bookmark", key=f"{tab_prefix}_unbm_{res['id']}", use_container_width=True):
                try:
                    services.ResourceService.unbookmark(user_id, res["id"])
                    st.success("Bookmark removed.")
                    ui_components.safe_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            if st.button("Bookmark", key=f"{tab_prefix}_bm_{res['id']}", use_container_width=True):
                try:
                    services.ResourceService.bookmark(user_id, res["id"])
                    st.success("Bookmarked!")
                    ui_components.safe_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with act2:
        file_url = res.get("file_url", "")
        if file_url and file_url.startswith("http"):
            st.link_button("Download", url=file_url, use_container_width=True)
        elif file_url and os.path.exists(file_url):
            try:
                with open(file_url, "rb") as f:
                    file_bytes = f.read()
                st.download_button(
                    label="Download",
                    data=file_bytes,
                    file_name=os.path.basename(file_url),
                    key=f"{tab_prefix}_dl_{res['id']}",
                    use_container_width=True,
                )
            except Exception:
                st.button("Unavailable", key=f"{tab_prefix}_dlerr_{res['id']}", disabled=True, use_container_width=True)
        else:
            st.button("Unavailable", key=f"{tab_prefix}_na_{res['id']}", disabled=True, use_container_width=True)


def render(user: dict) -> None:
    ui_components.page_header(
        title="Resource Hub",
        subtitle="Share and discover lecture notes, past papers, slides, and study guides.",
        icon="folder-open",
    )

    user_id = user["id"]

    tab_browse, tab_bookmarks, tab_upload = st.tabs([
        "Browse Resources",
        "My Bookmarks",
        "Upload Resource",
    ])

    # Fetch once, reuse across tabs
    try:
        all_resources = services.ResourceService.get_all() or []
    except Exception:
        all_resources = []

    # ── Tab 1: Browse Resources ──────────────────────────────────────────────
    with tab_browse:
        col_search, col_course, col_cat = st.columns([4, 3, 3])
        with col_search:
            search_q = st.text_input(
                "Search", placeholder="Search by title or course…", key="res_search", label_visibility="collapsed"
            )
        with col_course:
            course_codes = ["All Courses"] + sorted({r.get("course_code", "") for r in all_resources if r.get("course_code")})
            course_filter = st.selectbox("Course Code", course_codes, key="res_course")
        with col_cat:
            cat_filter = st.selectbox(
                "Category", ["All Types", "Notes", "PYQs", "PPTs", "Study guides", "Lab Manuals"], key="res_cat"
            )

        filtered = all_resources
        if search_q:
            q = search_q.lower()
            filtered = [r for r in filtered if q in r.get("title", "").lower() or q in r.get("course_name", "").lower()]
        if course_filter != "All Courses":
            filtered = [r for r in filtered if r.get("course_code") == course_filter]
        if cat_filter != "All Types":
            filtered = [r for r in filtered if r.get("category") == cat_filter]

        if filtered:
            cols = st.columns(2)
            for idx, res in enumerate(filtered):
                _resource_card(cols[idx % 2], res, "browse", user_id)
        else:
            ui_components.render_empty_state(
                "No resources found",
                "Try adjusting your filters or be the first to share a resource.",
                icon="folder-open",
            )

    # ── Tab 2: My Bookmarks ──────────────────────────────────────────────────
    with tab_bookmarks:
        try:
            bookmarked = services.ResourceService.get_user_bookmarked(user_id) or []
        except Exception:
            bookmarked = []

        if bookmarked:
            cols = st.columns(2)
            for idx, res in enumerate(bookmarked):
                _resource_card(cols[idx % 2], res, "bm", user_id)
        else:
            ui_components.render_empty_state(
                "No bookmarked resources",
                "Resources you bookmark will appear here for quick access.",
                icon="bookmark",
            )

    # ── Tab 3: Upload Resource ───────────────────────────────────────────────
    with tab_upload:
        st.markdown(
            "<h3 style='margin-top:0;color:#EFF6EE;font-size:1.15rem;'>Share Academic Material</h3>",
            unsafe_allow_html=True,
        )

        with st.form("upload_resource_form", clear_on_submit=True):
            res_title = st.text_input("Material Title *", placeholder="e.g. DSA Lecture Notes Week 1-10")

            c1, c2 = st.columns(2)
            with c1:
                res_code = st.text_input("Course Code *", placeholder="e.g. CS-201")
            with c2:
                res_name = st.text_input("Course Name *", placeholder="e.g. Data Structures")

            res_cat = st.selectbox("Category *", ["Notes", "PYQs", "PPTs", "Study guides", "Lab Manuals"])
            uploaded_file = st.file_uploader(
                "Upload file", type=["pdf", "pptx", "ppt", "docx", "doc"]
            )

            submitted = st.form_submit_button("Upload & Share", type="primary")

            if submitted:
                if not res_title or not res_code or not res_name or uploaded_file is None:
                    st.error("Please fill all required fields (*) and select a file.")
                else:
                    size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
                    if size_mb > 25:
                        st.error(f"File is {size_mb:.1f} MB — maximum allowed size is 25 MB.")
                    else:
                        safe_name = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
                        local_path = os.path.join(UPLOAD_DIR, safe_name)
                        try:
                            with st.spinner("Uploading…"):
                                with open(local_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                services.ResourceService.upload(
                                    title=res_title,
                                    course_code=res_code,
                                    course_name=res_name,
                                    category=res_cat,
                                    file_url=local_path,
                                    uploader_id=user_id,
                                    uploader_name=user["name"],
                                )
                            st.success(f"'{res_title}' shared successfully!")
                            ui_components.safe_rerun()
                        except Exception as e:
                            st.error(f"Upload failed: {e}")

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
