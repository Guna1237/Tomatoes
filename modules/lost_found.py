import streamlit as st
import os
import uuid
import services
import ui_components

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CATEGORIES = ["Electronics", "IDs", "Books", "Accessories", "Clothing", "Keys", "Other"]


def _type_badge(item_type: str) -> str:
    if item_type == "Lost":
        return (
            '<span style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);'
            'color:#F87171;border-radius:20px;padding:2px 10px;font-size:0.75rem;font-weight:600;">Lost</span>'
        )
    return (
        '<span style="background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);'
        'color:#4ADE80;border-radius:20px;padding:2px 10px;font-size:0.75rem;font-weight:600;">Found</span>'
    )


def _status_badge(status: str) -> str:
    colors = {
        "Open": ("#3B82F6", "rgba(59,130,246,0.1)", "rgba(59,130,246,0.25)"),
        "Claimed": ("#FB923C", "rgba(251,146,60,0.1)", "rgba(251,146,60,0.25)"),
        "Resolved": ("#22C55E", "rgba(34,197,94,0.1)", "rgba(34,197,94,0.25)"),
    }
    c, bg, border = colors.get(status, ("#64748B", "rgba(100,116,139,0.08)", "rgba(100,116,139,0.15)"))
    return (
        f'<span style="background:{bg};border:1px solid {border};color:{c};'
        f'border-radius:20px;padding:2px 10px;font-size:0.75rem;font-weight:600;">{status}</span>'
    )


def render(user: dict) -> None:
    ui_components.page_header(
        title="Lost & Found",
        subtitle="Report and reclaim misplaced items across campus.",
        icon="package",
    )

    user_id = user["id"]

    # ── Report Item Expander ──────────────────────────────────────────────────
    with st.expander("Report a Lost or Found Item", expanded=False):
        with st.form("lf_report_form", clear_on_submit=True):
            lf_title = st.text_input("Item Name *", placeholder="e.g. Blue water bottle, Student ID card")

            c1, c2 = st.columns(2)
            with c1:
                lf_type = st.radio("Type *", ["Lost", "Found"], horizontal=True)
            with c2:
                lf_cat = st.selectbox("Category *", CATEGORIES)

            lf_desc = st.text_area(
                "Description *",
                placeholder="Describe the item: color, size, brand, distinguishing marks…",
            )
            lf_location = st.text_input(
                "Location *",
                placeholder="e.g. Near the cafeteria, Library 2nd floor",
            )
            lf_image = st.file_uploader("Image (optional)", type=["png", "jpg", "jpeg"])

            if st.form_submit_button("Submit Report", type="primary"):
                if not lf_title or not lf_desc or not lf_location:
                    st.error("Please fill in all required fields (*).")
                else:
                    image_path = None
                    if lf_image:
                        safe_name = f"lf_{uuid.uuid4().hex[:8]}_{lf_image.name}"
                        image_path = os.path.join(UPLOAD_DIR, safe_name)
                        try:
                            with open(image_path, "wb") as f:
                                f.write(lf_image.getbuffer())
                        except Exception as e:
                            st.warning(f"Image could not be saved: {e}")
                            image_path = None

                    try:
                        services.LostFoundService.report(
                            title=lf_title,
                            description=lf_desc,
                            category=lf_cat,
                            item_type=lf_type,
                            location=lf_location,
                            image_url=image_path or "",
                            reporter_id=user_id,
                            reporter_name=user["name"],
                        )
                        st.success(f"Report for '{lf_title}' published successfully!")
                        ui_components.safe_rerun()
                    except Exception as e:
                        st.error(f"Failed to submit report: {e}")

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ── Filter bar ────────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns([2, 2, 4])
    with f1:
        type_filter = st.selectbox("Type", ["All", "Lost", "Found"], key="lf_type_filter", label_visibility="collapsed")
    with f2:
        cat_filter = st.selectbox(
            "Category", ["All Categories"] + CATEGORIES, key="lf_cat_filter", label_visibility="collapsed"
        )
    with f3:
        search_q = st.text_input("Search", placeholder="Search items…", key="lf_search", label_visibility="collapsed")

    # ── Fetch & filter ────────────────────────────────────────────────────────
    try:
        items = services.LostFoundService.get_all() or []
    except Exception:
        items = []

    filtered = items
    if type_filter != "All":
        filtered = [i for i in filtered if i.get("item_type") == type_filter]
    if cat_filter != "All Categories":
        filtered = [i for i in filtered if i.get("category") == cat_filter]
    if search_q:
        q = search_q.lower()
        filtered = [
            i for i in filtered
            if q in i.get("title", "").lower() or q in i.get("description", "").lower()
        ]

    # Show open + claimed, hide fully resolved unless it's the user's own
    visible = [
        i for i in filtered
        if i.get("status") != "Resolved" or i.get("reporter_id") == user_id
    ]

    if not visible:
        ui_components.render_empty_state(
            "No items found",
            "No lost & found reports match your filters. Try adjusting or report a new item above.",
            icon="search",
        )
        st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
        return

    # ── Item grid ─────────────────────────────────────────────────────────────
    cols = st.columns(2)
    for idx, item in enumerate(visible):
        col = cols[idx % 2]
        status = item.get("status", "Open")
        is_reporter = item.get("reporter_id") == user_id
        image_url = item.get("image_url", "")

        with col:
            # Image
            if image_url:
                if os.path.exists(image_url):
                    try:
                        st.image(image_url, use_container_width=True, clamp=True)
                    except Exception:
                        pass
                elif image_url.startswith("http"):
                    try:
                        st.markdown(
                            f'<img src="{image_url}" style="width:100%;max-height:160px;object-fit:cover;border-radius:8px;margin-bottom:8px;" />',
                            unsafe_allow_html=True,
                        )
                    except Exception:
                        pass

            st.markdown(
                f"""
<div class="premium-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
    <div>
      <span class="category-tag">{item.get('category','')}</span>
      <h4 style="margin:6px 0 0 0;color:var(--text);font-size:1rem;font-weight:600;">{item.get('title','')}</h4>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
      {_type_badge(item.get('item_type','Lost'))}
      {_status_badge(status)}
    </div>
  </div>
  <p style="margin:0 0 10px 0;color:var(--muted);font-size:0.875rem;line-height:1.5;
     max-height:60px;overflow:hidden;text-overflow:ellipsis;">
    {item.get('description','')}
  </p>
  <div class="info-row" style="font-size:0.8rem;margin-bottom:4px;">
    <i data-lucide="map-pin" style="width:12px;"></i>
    <span><strong>{item.get('location','')}</strong></span>
  </div>
  <div class="info-row" style="font-size:0.78rem;justify-content:space-between;">
    <span>by <strong>{item.get('reporter_name','')}</strong></span>
    <span>{str(item.get('created_at',''))[:10]}</span>
  </div>
</div>""",
                unsafe_allow_html=True,
            )

            # Action buttons
            if is_reporter:
                if status == "Claimed":
                    if st.button("Mark Resolved", key=f"lf_resolve_{item['id']}", type="primary", use_container_width=True):
                        try:
                            services.LostFoundService.update_status(item["id"], "Resolved")
                            st.success("Marked as resolved!")
                            ui_components.safe_rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                elif status == "Open":
                    if st.button("Mark Resolved", key=f"lf_resolve_open_{item['id']}", use_container_width=True):
                        try:
                            services.LostFoundService.update_status(item["id"], "Resolved")
                            st.success("Marked as resolved.")
                            ui_components.safe_rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                if status == "Open":
                    if st.button("Claim Item", key=f"lf_claim_{item['id']}", type="primary", use_container_width=True):
                        try:
                            services.LostFoundService.update_status(item["id"], "Claimed")
                            try:
                                services.NotificationService.add(
                                    user_id=item["reporter_id"],
                                    title=f"Claim on '{item['title']}'",
                                    content=(
                                        f"{user['name']} ({user.get('email','')}) has claimed your "
                                        f"{item.get('type','').lower()} item '{item['title']}'. "
                                        f"Please contact them to arrange handover."
                                    ),
                                )
                            except Exception:
                                pass
                            st.success("Item claimed! The reporter has been notified.")
                            ui_components.safe_rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                elif status == "Claimed":
                    st.markdown(
                        '<span style="color:#FB923C;font-size:0.8rem;font-weight:600;">'
                        '<i data-lucide="clock" style="width:12px;display:inline-block;vertical-align:middle;"></i>'
                        " Already claimed — pending resolution</span>",
                        unsafe_allow_html=True,
                    )

    st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)
