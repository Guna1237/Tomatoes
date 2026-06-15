import streamlit as st

LUCIDE_CDN = '<script src="https://unpkg.com/lucide@latest"></script><script>setTimeout(()=>{if(window.lucide)lucide.createIcons();},150);</script>'

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg: #0A0C10;
  --surface: #111318;
  --surface2: #161B23;
  --border: rgba(255,255,255,0.07);
  --border-red: rgba(221,4,38,0.25);
  --text: #F0F2F5;
  --muted: #8B949E;
  --red: #DD0426;
  --red2: #FF4458;
  --sidebar-w: 240px;
}

html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', -apple-system, sans-serif !important;
}

.block-container {
  padding: 1.75rem 2.5rem 3rem calc(var(--sidebar-w) + 2.5rem) !important;
  max-width: 100% !important;
}

/* Hide Streamlit chrome + its sidebar */
#MainMenu, header, footer,
div[data-testid="stDecoration"],
div[data-testid="stToolbar"] { display: none !important; }

/* Hide Streamlit's native sidebar visually but keep buttons in DOM for JS clicks */
section[data-testid="stSidebar"] {
  position: fixed !important;
  left: -9999px !important;
  width: 0 !important;
  min-width: 0 !important;
  opacity: 0 !important;
}
/* Also suppress the sidebar toggle arrow that Streamlit injects */
div[data-testid="collapsedControl"] { display: none !important; }

/* ── Inputs ─────────────────────────────────────────────── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
  transition: border-color 0.2s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stNumberInput"] input:focus {
  border-color: var(--red) !important;
  box-shadow: 0 0 0 3px rgba(221,4,38,0.1) !important;
  outline: none !important;
}
div[data-testid="stSelectbox"] > div {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border-color: var(--border) !important;
}
div[data-testid="stFileUploader"] {
  background: var(--surface) !important;
  border: 1px dashed var(--border) !important;
  border-radius: 10px !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
div[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(135deg, var(--red), var(--red2)) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  transition: opacity 0.2s, transform 0.15s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
  opacity: 0.85 !important;
  transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  transition: border-color 0.2s, background 0.2s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
  border-color: var(--red) !important;
  background: rgba(221,4,38,0.05) !important;
}

/* ── Tabs ────────────────────────────────────────────────── */
div[data-testid="stTabs"] [role="tab"] {
  color: var(--muted) !important; font-weight: 500 !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--text) !important;
  border-bottom-color: var(--red) !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ── Custom Sidebar ──────────────────────────────────────── */
.cc-sidebar {
  position: fixed;
  top: 0; left: 0;
  width: var(--sidebar-w);
  height: 100vh;
  background: linear-gradient(180deg, #0C0E13 0%, #0F1117 50%, #111520 100%);
  border-right: 1px solid rgba(221,4,38,0.1);
  box-shadow: 4px 0 40px rgba(0,0,0,0.6);
  display: flex;
  flex-direction: column;
  z-index: 99999;
  overflow: hidden;
}

.cc-brand {
  padding: 1.25rem 1rem 1.125rem;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  cursor: default;
  user-select: none;
}
.cc-logo {
  width: 30px; height: 30px;
  background: linear-gradient(135deg, #DD0426 0%, #FF4458 100%);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; flex-shrink: 0;
  box-shadow: 0 2px 14px rgba(221,4,38,0.45);
}
.cc-brand-text {
  font-size: 0.9rem; font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
}

.cc-nav {
  flex: 1;
  padding: 0.6rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 1px;
  overflow-y: auto;
}

.cc-nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 10px;
  border-radius: 8px;
  color: var(--muted);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
  position: relative;
  user-select: none;
}
.cc-nav-item:hover {
  background: rgba(255,255,255,0.04);
  color: var(--text);
}
.cc-nav-item.active {
  background: linear-gradient(90deg, rgba(221,4,38,0.13) 0%, rgba(221,4,38,0.03) 100%);
  color: var(--text);
  font-weight: 600;
}
.cc-nav-item.active::before {
  content: '';
  position: absolute;
  left: 0; top: 5px; bottom: 5px;
  width: 3px;
  background: linear-gradient(180deg, #DD0426, #FF4458);
  border-radius: 0 3px 3px 0;
}
.cc-nav-item i, .cc-nav-item svg {
  width: 15px; height: 15px;
  flex-shrink: 0;
}

.cc-footer {
  padding: 0.75rem 0.875rem;
  border-top: 1px solid rgba(255,255,255,0.05);
  display: flex;
  align-items: center;
  gap: 9px;
}
.cc-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(221,4,38,0.2), rgba(221,4,38,0.05));
  border: 1px solid rgba(221,4,38,0.25);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700;
  color: var(--red);
  flex-shrink: 0;
  overflow: hidden;
}
.cc-avatar img { width: 100%; height: 100%; object-fit: cover; }
.cc-user { flex: 1; min-width: 0; }
.cc-user-name {
  font-size: 0.78rem; font-weight: 600; color: var(--text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.cc-user-bal { font-size: 0.68rem; color: var(--muted); margin-top: 1px; }
.cc-signout {
  color: var(--muted);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  width: 26px; height: 26px;
  border-radius: 6px;
  border: none; background: transparent;
  transition: color 0.15s, background 0.15s;
  flex-shrink: 0;
}
.cc-signout:hover { color: var(--red); background: rgba(221,4,38,0.08); }
.cc-signout svg { width: 14px; height: 14px; }

/* ── Cards ───────────────────────────────────────────────── */
.premium-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.premium-card:hover {
  border-color: var(--border-red);
  box-shadow: 0 4px 24px rgba(221,4,38,0.05);
  transform: translateY(-1px);
}

/* ── Page headers ────────────────────────────────────────── */
.page-title {
  font-size: 1.55rem; font-weight: 800;
  color: var(--text); letter-spacing: -0.03em;
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 4px;
}
.page-subtitle { font-size: 0.875rem; color: var(--muted); margin-bottom: 1.75rem; }

/* ── Badges ──────────────────────────────────────────────── */
.category-tag {
  background: rgba(255,255,255,0.04);
  color: var(--muted);
  padding: 2px 8px; border-radius: 5px;
  font-size: 0.72rem; font-weight: 600;
  border: 1px solid var(--border);
}
.priority-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 9px; border-radius: 20px;
  font-size: 0.72rem; font-weight: 600;
}

/* ── Metrics ─────────────────────────────────────────────── */
.metrics-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
  gap: 0.75rem; margin-bottom: 1.5rem;
}
.metric-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.125rem 1.25rem;
  display: flex; align-items: center; gap: 1rem;
  transition: border-color 0.2s, transform 0.2s;
}
.metric-box:hover { border-color: var(--border-red); transform: translateY(-1px); }
.metric-icon-wrapper {
  border-radius: 10px; width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.metric-value { font-size: 1.6rem; font-weight: 800; color: var(--text); line-height: 1; letter-spacing: -0.03em; }
.metric-label { font-size: 0.73rem; color: var(--muted); font-weight: 500; margin-top: 3px; }

/* ── Skeleton ────────────────────────────────────────────── */
@keyframes shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position: 600px 0; }
}
.skeleton-bar {
  background: linear-gradient(90deg, var(--surface) 25%, var(--surface2) 50%, var(--surface) 75%);
  background-size: 1200px 100%;
  animation: shimmer 1.4s infinite linear;
  border-radius: 5px; height: 14px; margin-bottom: 10px;
}
.skeleton-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.25rem; margin-bottom: 0.875rem;
}

/* ── Misc ────────────────────────────────────────────────── */
.info-row { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 0.82rem; margin-top: 6px; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeUp 0.35s ease-out forwards; }

@media (max-width: 768px) {
  :root { --sidebar-w: 54px; }
  .cc-brand-text, .cc-nav-item span, .cc-user, .cc-signout { display: none; }
  .cc-nav-item { justify-content: center; padding: 10px; }
  .cc-brand { justify-content: center; padding: 1rem 0.5rem; }
  .cc-footer { justify-content: center; }
  .block-container { padding-left: calc(var(--sidebar-w) + 1rem) !important; padding-right: 1rem !important; }
}
</style>
"""

GLOBAL_JS = """
<script>
document.addEventListener('keydown', function(e) {
  if (e.key === '/' || (e.ctrlKey && e.key === 'k') || (e.metaKey && e.key === 'k')) {
    const inputs = document.querySelectorAll('input[placeholder]');
    for (let inp of inputs) {
      if (inp.placeholder.toLowerCase().includes('search')) {
        e.preventDefault(); inp.focus(); break;
      }
    }
  }
});
</script>
"""


def inject_custom_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown(GLOBAL_JS, unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, icon: str = "home"):
    st.markdown(f"""
<div class="fade-in">
  <div class="page-title">
    <i data-lucide="{icon}" style="color:#DD0426;width:24px;height:24px;flex-shrink:0;"></i>
    {title}
  </div>
  <div class="page-subtitle">{subtitle}</div>
</div>""", unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_kpis(tomatos_val: int, deliveries_val: int, events_val: int, saved_val: int):
    st.markdown(f"""
<div class="metrics-container fade-in">
  <div class="metric-box">
    <div class="metric-icon-wrapper" style="background:rgba(34,197,94,0.1);color:#22C55E;">
      <i data-lucide="wallet" style="width:18px;height:18px;"></i>
    </div>
    <div><div class="metric-value">{tomatos_val}</div><div class="metric-label">Tomato Balance</div></div>
  </div>
  <div class="metric-box">
    <div class="metric-icon-wrapper" style="background:rgba(59,130,246,0.1);color:#3B82F6;">
      <i data-lucide="package" style="width:18px;height:18px;"></i>
    </div>
    <div><div class="metric-value">{deliveries_val}</div><div class="metric-label">Logistics Requests</div></div>
  </div>
  <div class="metric-box">
    <div class="metric-icon-wrapper" style="background:rgba(168,85,247,0.1);color:#A855F7;">
      <i data-lucide="calendar" style="width:18px;height:18px;"></i>
    </div>
    <div><div class="metric-value">{events_val}</div><div class="metric-label">Registered Events</div></div>
  </div>
  <div class="metric-box">
    <div class="metric-icon-wrapper" style="background:rgba(234,179,8,0.1);color:#EAB308;">
      <i data-lucide="bookmark" style="width:18px;height:18px;"></i>
    </div>
    <div><div class="metric-value">{saved_val}</div><div class="metric-label">Saved Announcements</div></div>
  </div>
</div>""", unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_timeline(status: str):
    steps = ["Created", "Accepted", "Picked Up", "Delivered"]
    icons = ["file-plus", "handshake", "package", "check-circle"]
    try:
        idx = steps.index(status)
    except ValueError:
        idx = 0

    progress = (idx / (len(steps) - 1)) * 80
    circles = ""
    for i, (step, icon) in enumerate(zip(steps, icons)):
        active = i <= idx
        bg = "linear-gradient(135deg,#DD0426,#FF4458)" if active else "var(--surface2)"
        border = "#DD0426" if active else "rgba(255,255,255,0.07)"
        text_c = "var(--text)" if active else "var(--muted)"
        weight = "700" if i == idx else "500"
        shadow = "0 0 12px rgba(221,4,38,0.4)" if active else "none"
        circles += f"""<div style="display:flex;flex-direction:column;align-items:center;width:25%;z-index:3;text-align:center;">
  <div style="width:32px;height:32px;border-radius:50%;background:{bg};border:2px solid {border};
              display:flex;align-items:center;justify-content:center;color:#fff;margin-bottom:7px;box-shadow:{shadow};">
    <i data-lucide="{icon}" style="width:14px;height:14px;"></i>
  </div>
  <span style="font-size:0.76rem;color:{text_c};font-weight:{weight};">{step}</span>
</div>"""

    st.markdown(f"""
<div class="premium-card" style="margin-bottom:1.5rem;">
  <div style="font-size:0.82rem;font-weight:600;color:var(--muted);margin-bottom:1rem;
              display:flex;align-items:center;gap:7px;">
    <i data-lucide="truck" style="width:14px;height:14px;color:#DD0426;"></i> Delivery Progress
  </div>
  <div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;padding:8px 0;">
    <div style="position:absolute;left:12.5%;right:12.5%;top:22px;height:2px;background:rgba(255,255,255,0.06);z-index:1;"></div>
    <div style="position:absolute;left:12.5%;width:{progress}%;top:22px;height:2px;
                background:linear-gradient(90deg,#DD0426,#FF4458);z-index:2;transition:width 0.4s;"></div>
    {circles}
  </div>
</div>""", unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_empty_state(title: str, description: str, icon: str = "inbox"):
    st.markdown(f"""
<div class="premium-card fade-in" style="display:flex;flex-direction:column;align-items:center;
     padding:3rem 1.5rem;text-align:center;border-style:dashed;">
  <div style="width:48px;height:48px;border-radius:50%;background:rgba(255,255,255,0.03);
              border:1px solid rgba(255,255,255,0.07);display:flex;align-items:center;
              justify-content:center;color:var(--muted);margin-bottom:1rem;">
    <i data-lucide="{icon}" style="width:22px;height:22px;"></i>
  </div>
  <div style="font-size:0.95rem;font-weight:600;color:var(--text);margin-bottom:6px;">{title}</div>
  <div style="font-size:0.82rem;color:var(--muted);max-width:300px;line-height:1.55;">{description}</div>
</div>""", unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_skeleton_card():
    st.markdown("""
<div class="skeleton-card">
  <div class="skeleton-bar" style="width:55%;height:17px;margin-bottom:12px;"></div>
  <div class="skeleton-bar" style="width:90%;"></div>
  <div class="skeleton-bar" style="width:70%;"></div>
  <div class="skeleton-bar" style="width:35%;height:11px;margin-top:14px;"></div>
</div>""", unsafe_allow_html=True)


def render_skeleton_grid(count: int = 3):
    for _ in range(count):
        render_skeleton_card()


def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


def _nav_js(label: str) -> str:
    """JS that finds a hidden Streamlit sidebar button by textContent and clicks it."""
    # Use textContent (not innerText) — innerText returns "" for display:none elements
    return (
        f"(function(){{"
        f"var btns=document.querySelectorAll('section[data-testid=\"stSidebar\"] button');"
        f"for(var i=0;i<btns.length;i++){{"
        f"if(btns[i].textContent.trim()==='{label}'){{btns[i].click();return;}}"
        f"}}"
        f"}})();"
    )


def render_custom_sidebar(user: dict, current_page: str):
    nav_items = [
        ("Dashboard",     "home"),
        ("Events",        "calendar"),
        ("Announcements", "megaphone"),
        ("Resources",     "folder-open"),
        ("Logistics",     "truck"),
        ("Lost & Found",  "package-search"),
        ("Profile",       "user"),
    ]

    # ── Hidden Streamlit sidebar buttons (real navigation) ──
    with st.sidebar:
        for name, _ in nav_items:
            if st.button(f"NAV:{name}", key=f"_nav_{name}"):
                try:
                    st.query_params["page"] = name
                except AttributeError:
                    try:
                        st.experimental_set_query_params(page=name)
                    except Exception:
                        pass
                safe_rerun()
        if st.button("NAV:SignOut", key="_nav_signout"):
            from auth import logout
            logout()
            try:
                st.query_params.clear()
            except Exception:
                try:
                    st.experimental_set_query_params()
                except Exception:
                    pass
            safe_rerun()

    # ── Visual sidebar HTML ──────────────────────────────────
    balance = user.get("tomatos", user.get("tomato_balance", 0))
    initials = "".join(w[0].upper() for w in user.get("name", "?").split()[:2])
    avatar_url = user.get("avatar_url") or ""
    avatar_inner = (
        f'<img src="{avatar_url}" alt="" style="width:100%;height:100%;object-fit:cover;">'
        if avatar_url else f"<span>{initials}</span>"
    )

    nav_html = ""
    for name, icon in nav_items:
        active = "active" if current_page == name else ""
        js = _nav_js(f"NAV:{name}")
        nav_html += (
            f'<div class="cc-nav-item {active}" onclick="{js}">'
            f'<i data-lucide="{icon}"></i><span>{name}</span>'
            f'</div>'
        )

    signout_js = _nav_js("NAV:SignOut")

    st.markdown(f"""
<div class="cc-sidebar">
  <div class="cc-brand">
    <div class="cc-logo">🍅</div>
    <span class="cc-brand-text">CampusConnect</span>
  </div>
  <div class="cc-nav">
    {nav_html}
  </div>
  <div class="cc-footer">
    <div class="cc-avatar">{avatar_inner}</div>
    <div class="cc-user">
      <div class="cc-user-name">{user.get('name', '')}</div>
      <div class="cc-user-bal">{balance} 🍅</div>
    </div>
    <button class="cc-signout" onclick="{signout_js}" title="Sign out">
      <i data-lucide="log-out"></i>
    </button>
  </div>
</div>
{LUCIDE_CDN}""", unsafe_allow_html=True)
