import streamlit as st
import datetime
import os
from html import escape
import services
import ui_components

CAT_ICONS = {
    "Notes": "book-open",
    "PYQs": "help-circle",
    "PPTs": "presentation",
    "Lab Manuals": "flask-conical",
    "Study guides": "compass",
}


def _resolve_download_path(file_url: str) -> str:
    if not file_url:
        return ""
    if file_url.startswith("local://"):
        relative = file_url.removeprefix("local://").replace("/", os.sep)
        direct = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", relative)
        if os.path.exists(direct):
            return direct
        file_name = os.path.basename(relative)
        resource_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "resources")
        for root, _, files in os.walk(resource_dir):
            if file_name in files:
                return os.path.join(root, file_name)
        return ""
    return file_url if os.path.exists(file_url) else ""


def _file_meta(res: dict) -> str:
    file_type = (res.get("file_type") or os.path.splitext(res.get("file_name", ""))[1].lstrip(".") or "file").upper()
    size = res.get("file_size_mb")
    if isinstance(size, (int, float)):
        return f"{file_type} - {size:.1f} MB"
    return file_type


def _resource_card(col, res: dict, tab_prefix: str, user_id: str) -> None:
    icon = CAT_ICONS.get(res.get("category", ""), "file")
    title = escape(res.get("title", "Untitled resource"))
    course_code = escape(res.get("course_code", ""))
    course_name = escape(res.get("course_name", ""))
    category = escape(res.get("category", ""))
    uploader = escape(res.get("uploader_name", ""))
    created_at = str(res.get("created_at", ""))[:10]
    downloads = res.get("downloads_count", 0)
    bookmarks = res.get("bookmarks_count", 0)
    meta = escape(_file_meta(res))
    col.markdown(
        f"""
<div class="premium-card" style="min-height:210px;display:flex;flex-direction:column;gap:0.85rem;">
  <div style="display:flex;gap:12px;align-items:flex-start;">
    <div style="background:#EFF6FF;border:1px solid rgba(37,99,235,0.14);border-radius:8px;width:44px;height:44px;
                display:flex;align-items:center;justify-content:center;color:#2563EB;flex-shrink:0;">
      <i data-lucide="{icon}" style="width:20px;height:20px;"></i>
    </div>
    <div style="overflow:hidden;min-width:0;flex:1;">
      <h4 style="margin:0;color:var(--text);font-size:1rem;line-height:1.35;font-weight:800;">
        {title}
      </h4>
      <div style="display:flex;gap:6px;margin-top:7px;flex-wrap:wrap;">
        <span class="category-tag">{course_code}</span>
        <span class="category-tag">{category}</span>
        <span class="category-tag">{meta}</span>
      </div>
    </div>
  </div>
  <div style="font-size:0.84rem;color:var(--muted);line-height:1.45;min-height:2.4em;">
    {course_name or "General campus resource"}
  </div>
  <div style="display:flex;justify-content:space-between;gap:8px;color:var(--muted);font-size:0.78rem;margin-top:auto;">
    <span>by <strong style="color:var(--text);">{uploader}</strong></span>
    <span>{created_at}</span>
  </div>
  <div style="display:flex;gap:12px;color:var(--muted);font-size:0.78rem;">
    <span><i data-lucide="bookmark" style="width:12px;display:inline-block;vertical-align:middle;"></i> {bookmarks}</span>
    <span><i data-lucide="download" style="width:12px;display:inline-block;vertical-align:middle;"></i> {downloads}</span>
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
        elif _resolve_download_path(file_url):
            try:
                local_file = _resolve_download_path(file_url)
                with open(local_file, "rb") as f:
                    file_bytes = f.read()
                st.download_button(
                    label="Download",
                    data=file_bytes,
                    file_name=res.get("file_name") or os.path.basename(local_file),
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

    tab_browse, tab_bookmarks, tab_upload, tab_ai = st.tabs([
        "Browse Resources",
        "My Bookmarks",
        "Upload Resource",
        "AI Study Planner",
    ])

    # Fetch once, reuse across tabs
    try:
        all_resources = services.ResourceService.get_all() or []
    except Exception:
        all_resources = []

    total_downloads = sum(int(r.get("downloads_count", 0) or 0) for r in all_resources)
    total_bookmarks = sum(int(r.get("bookmarks_count", 0) or 0) for r in all_resources)
    unique_courses = len({r.get("course_code") for r in all_resources if r.get("course_code")})
    st.markdown(f"""
<div class="metrics-container" style="grid-template-columns:repeat(3,minmax(0,1fr));">
  <div class="metric-box"><div class="metric-icon-wrapper" style="background:#EFF6FF;color:#2563EB;">
    <i data-lucide="files" style="width:18px;height:18px;"></i></div>
    <div class="metric-info"><span class="metric-value">{len(all_resources)}</span><span class="metric-label">Shared Files</span></div>
  </div>
  <div class="metric-box"><div class="metric-icon-wrapper" style="background:#ECFDF3;color:#0F9F6E;">
    <i data-lucide="book-open" style="width:18px;height:18px;"></i></div>
    <div class="metric-info"><span class="metric-value">{unique_courses}</span><span class="metric-label">Courses Covered</span></div>
  </div>
  <div class="metric-box"><div class="metric-icon-wrapper" style="background:#FFF7ED;color:#D97706;">
    <i data-lucide="activity" style="width:18px;height:18px;"></i></div>
    <div class="metric-info"><span class="metric-value">{total_downloads + total_bookmarks}</span><span class="metric-label">Saves & Downloads</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

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
            """
<div class="premium-card" style="border-color:rgba(37,99,235,0.18);">
  <h3 style="margin:0 0 6px 0;color:var(--text);font-size:1.12rem;">Share Academic Material</h3>
  <p style="margin:0;color:var(--muted);font-size:0.86rem;line-height:1.5;">
    Upload PDFs, docs, slides, or lab material. Files are stored locally when cloud storage is unavailable.
  </p>
</div>
""",
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
                "Upload file", type=["pdf", "pptx", "ppt", "docx", "doc", "png", "jpg", "jpeg"]
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
                        try:
                            with st.spinner("Uploading…"):
                                file_bytes = uploaded_file.getvalue()
                                services.ResourceService.upload(
                                    title=res_title,
                                    course_code=res_code,
                                    course_name=res_name,
                                    category=res_cat,
                                    file_bytes=file_bytes,
                                    file_name=uploaded_file.name,
                                    uploader=user,
                                )
                            st.success(f"'{res_title}' shared successfully!")
                            ui_components.safe_rerun()
                        except Exception as e:
                            st.error(f"Upload failed: {e}")

    with tab_ai:
        st.markdown(
            """
<div class="premium-card" style="border-color:rgba(15,159,110,0.2);">
  <h3 style="margin:0 0 6px 0;color:var(--text);font-size:1.12rem;">AI Study Planner</h3>
  <p style="margin:0;color:var(--muted);font-size:0.86rem;line-height:1.5;">
    Turn the current resource library into a focused study path for an exam, assignment, or revision goal.
  </p>
</div>
""",
            unsafe_allow_html=True,
        )

        if not services.AIStudyService.is_configured():
            st.info(
                "Add OPENAI_API_KEY to `.streamlit/secrets.toml` or your environment to enable AI planning. "
                "Optional: set OPENAI_MODEL to choose a different model."
            )
        else:
            st.caption(f"Using OpenAI model: {services.AIStudyService.model_name()}")

        with st.form("ai_study_plan_form"):
            study_goal = st.text_area(
                "Study goal",
                placeholder="e.g. I have a DSA quiz tomorrow and need a 2-hour revision plan.",
                height=110,
            )
            submitted_ai = st.form_submit_button(
                "Generate Study Plan",
                type="primary",
                use_container_width=True,
                disabled=not services.AIStudyService.is_configured(),
            )

        if submitted_ai:
            if not study_goal.strip():
                st.error("Tell the planner what you are studying for.")
            else:
                try:
                    with st.spinner("Building your study plan..."):
                        st.session_state["ai_resource_plan"] = services.AIStudyService.generate_resource_plan(
                            study_goal.strip(),
                            all_resources,
                            user,
                        )
                except Exception as e:
                    st.error(f"AI planner failed: {e}")

        if st.session_state.get("ai_resource_plan"):
            st.markdown("#### Suggested Plan")
            st.markdown(st.session_state["ai_resource_plan"])

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
