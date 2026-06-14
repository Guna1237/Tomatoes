import streamlit as st
import datetime

# Lucide Icons CDN Script
LUCIDE_CDN = '<script src="https://unpkg.com/lucide@latest"></script><script>setTimeout(() => { lucide.createIcons(); }, 100);</script>'

# Global CSS stylesheet for custom styling, theme, animations, and overriding Streamlit UI
GLOBAL_CSS = """
<style>
/* Import Space Grotesk and Space Mono */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap');

:root {
  --bg-primary: #eff6ee;
  --bg-secondary: #ffffff;
  --sidebar: #273043;
  --sidebar-hover: #323d56;
  --text-primary: #273043;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
  --accent: #dd0426;
  --accent-hover: #f02d3a;
  --success: #10b981;
  --warning: #f59e0b;
}

/* Apply base light theme and layout settings */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Remove default Streamlit padding */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
}

/* Hide Streamlit Header, Footer, MainMenu, and Sidebar! */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
div[data-testid="stDecoration"] {display: none;}
div[data-testid="stToolbar"] {display: none;}
div[data-testid="stSidebar"] {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}

/* Custom styled inputs and dropdowns */
div[data-testid="stTextInput"] input, 
div[data-testid="stTextArea"] textarea, 
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 0.5rem 0.75rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

div[data-testid="stTextInput"] input:focus, 
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(221, 4, 38, 0.2) !important;
}

/* Style Selectboxes */
div[data-testid="stSelectbox"] > div {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}

/* Style File Uploader */
div[data-testid="stFileUploader"] {
    background-color: var(--bg-secondary) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
}

/* CSS Scrollbar override */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Custom CSS Classes for Premium Components */

/* Premium Cards */
.premium-card {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    animation: fadeIn 0.4s ease-out forwards;
    color: var(--text-primary);
}
.premium-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
    box-shadow: 0 4px 12px rgba(221, 4, 38, 0.08);
}

/* Fade In Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeIn 0.4s ease-out forwards;
}

/* Custom Header styling */
.page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.page-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
}

/* Priority Tags */
.priority-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.priority-high {
    background-color: rgba(221, 4, 38, 0.1);
    color: var(--accent);
    border: 1px solid rgba(221, 4, 38, 0.2);
}
.priority-medium {
    background-color: rgba(245, 158, 11, 0.1);
    color: var(--warning);
    border: 1px solid rgba(245, 158, 11, 0.2);
}
.priority-low {
    background-color: rgba(16, 185, 129, 0.1);
    color: var(--success);
    border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Category Tags */
.category-tag {
    background-color: var(--bg-primary);
    color: var(--text-secondary);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid var(--border);
}

/* Skeleton Loading Animation */
@keyframes skeletonPulse {
    0% { background-color: var(--bg-secondary); }
    50% { background-color: var(--border); }
    100% { background-color: var(--bg-secondary); }
}
.skeleton-card {
    border-radius: 8px;
    border: 1px solid var(--border);
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.skeleton-bar {
    animation: skeletonPulse 1.5s infinite ease-in-out;
    height: 16px;
    background-color: var(--bg-secondary);
    border-radius: 4px;
    margin-bottom: 10px;
}
.skeleton-title {
    width: 60%;
    height: 20px;
}
.skeleton-desc {
    width: 90%;
    height: 14px;
}
.skeleton-meta {
    width: 35%;
    height: 12px;
}

/* Info stats row */
.info-row {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-top: 6px;
}

/* Event banner styling */
.event-banner {
    width: 100%;
    height: 140px;
    object-fit: cover;
    border-radius: 6px;
    margin-bottom: 0.75rem;
}

/* Flex metrics box */
.metrics-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.metric-box {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.metric-icon-wrapper {
    background-color: var(--bg-primary);
    border-radius: 8px;
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-primary);
}
.metric-info {
    display: flex;
    flex-direction: column;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
}
.metric-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 500;
}

/* Custom Sidebar Layout */
.custom-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 250px;
    height: 100vh;
    background-color: var(--sidebar);
    color: #ffffff;
    z-index: 999999;
    transition: width 0.3s ease;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.custom-sidebar.collapsed {
    width: 80px;
}

/* Adjust Streamlit main container to accommodate sidebar */
[data-testid="stAppViewContainer"] .block-container {
    margin-left: 250px !important;
    transition: margin-left 0.3s ease !important;
    max-width: calc(100% - 250px) !important;
}

body.sidebar-collapsed [data-testid="stAppViewContainer"] .block-container {
    margin-left: 80px !important;
    max-width: calc(100% - 80px) !important;
}

.sidebar-header {
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-header h2 {
    color: #ffffff;
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    white-space: nowrap;
    opacity: 1;
    transition: opacity 0.2s;
}
.custom-sidebar.collapsed .sidebar-header h2 {
    opacity: 0;
    width: 0;
    overflow: hidden;
}

.sidebar-toggle {
    background: none;
    border: none;
    color: #ffffff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    border-radius: 6px;
}
.sidebar-toggle:hover {
    background-color: var(--sidebar-hover);
}

.sidebar-nav {
    flex-grow: 1;
    padding: 1.5rem 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
    overflow-y: auto;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 1.5rem;
    color: #94A3B8;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    transition: all 0.2s;
    white-space: nowrap;
}
.nav-item:hover {
    background-color: var(--sidebar-hover);
    color: #ffffff;
}
.nav-item.active {
    background-color: var(--accent);
    color: #ffffff;
    border-right: 4px solid #ffffff;
}
.custom-sidebar.collapsed .nav-text {
    display: none;
}
.custom-sidebar.collapsed .nav-item {
    justify-content: center;
    padding: 10px 0;
}

.sidebar-footer {
    padding: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    gap: 12px;
}
.custom-sidebar.collapsed .sidebar-footer {
    justify-content: center;
    padding: 1.5rem 0;
}
.custom-sidebar.collapsed .footer-info {
    display: none;
}

@media (max-width: 768px) {
    .custom-sidebar { width: 60px !important; }
    .custom-sidebar .nav-text, .custom-sidebar .sidebar-header h2, .custom-sidebar .footer-info { display: none !important; }
    .custom-sidebar .nav-item { justify-content: center !important; padding: 10px 0 !important; }
    .custom-sidebar .sidebar-footer { justify-content: center !important; padding: 1.5rem 0 !important; }
    [data-testid="stAppViewContainer"] .block-container { margin-left: 60px !important; max-width: calc(100% - 60px) !important; padding-top: 50px !important;}
}

</style>
"""

# Global JS Keyboard Shortcut Listener (focus search input on '/' or 'Ctrl+K')
GLOBAL_JS = """
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === '/' || (e.ctrlKey && e.key === 'k') || (e.metaKey && e.key === 'k')) {
        // Find input inside the top search bar (styled with custom placeholder text)
        const inputs = parent.document.querySelectorAll('input');
        for (let input of inputs) {
            if (input.placeholder.toLowerCase().includes('search')) {
                e.preventDefault();
                input.focus();
                break;
            }
        }
    }
});
</script>
"""


def inject_custom_styles():
    """
    Injects custom styles and keyboard shortcut scripts into the Streamlit app.
    """
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown(GLOBAL_JS, unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, icon: str = "home"):
    """
    Renders a premium header with matching subtitle and a Lucide icon.
    """
    st.markdown(f"""
<div class="fade-in">
<div class="page-title">
<i data-lucide="{icon}" style="color: #3B82F6; width: 28px; height: 28px;"></i>
{title}
</div>
<div class="page-subtitle">{subtitle}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_kpis(tomatos_val: int, deliveries_val: int, events_val: int, saved_val: int):
    """
    Renders the dashboard KPIs in a clean, modern grid.
    """
    html = f"""
<div class="metrics-container fade-in">
<div class="metric-box">
<div class="metric-icon-wrapper" style="color: #22C55E; background-color: rgba(34, 197, 94, 0.1);">
<i data-lucide="wallet"></i>
</div>
<div class="metric-info">
<span class="metric-value">{tomatos_val}</span>
<span class="metric-label">Tomatos Balance</span>
</div>
</div>
<div class="metric-box">
<div class="metric-icon-wrapper" style="color: #3B82F6; background-color: rgba(59, 130, 246, 0.1);">
<i data-lucide="package"></i>
</div>
<div class="metric-info">
<span class="metric-value">{deliveries_val}</span>
<span class="metric-label">Logistics Requests</span>
</div>
</div>
<div class="metric-box">
<div class="metric-icon-wrapper" style="color: #A855F7; background-color: rgba(168, 85, 247, 0.1);">
<i data-lucide="calendar"></i>
</div>
<div class="metric-info">
<span class="metric-value">{events_val}</span>
<span class="metric-label">Registered Events</span>
</div>
</div>
<div class="metric-box">
<div class="metric-icon-wrapper" style="color: #EAB308; background-color: rgba(234, 179, 8, 0.1);">
<i data-lucide="bookmark"></i>
</div>
<div class="metric-info">
<span class="metric-value">{saved_val}</span>
<span class="metric-label">Saved Announcements</span>
</div>
</div>
</div>
"""
    html = html.replace('\n\n', '\n'); html = html.replace('\n    \n', '\n'); st.markdown(html, unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_timeline(status: str):
    """
    Renders a premium horizontal timeline tracking parcel logistics progress.
    """
    steps = ["Request Created", "Matched", "Picked Up", "Delivered"]
    try:
        current_idx = steps.index(status)
    except ValueError:
        current_idx = 0
        
    html = '<div class="premium-card fade-in" style="margin-bottom: 1.5rem;">'
    html += '<h4 style="margin-top: 0; margin-bottom: 1rem; color: #FFFFFF; font-size: 1rem; display: flex; align-items: center; gap: 8px;"><i data-lucide="truck" style="width: 18px; color: #3B82F6;"></i> Active Delivery Progress</h4>'
    html += '<div style="display: flex; justify-content: space-between; align-items: center; position: relative; padding: 10px 0; overflow-x: auto;">'
    
    # Draw horizontal bar background
    html += '<div style="position: absolute; left: 10%; right: 10%; top: 26px; height: 3px; background-color: #2D3748; z-index: 1;"></div>'
    
    # Draw progress fill
    progress_width = (current_idx / (len(steps) - 1)) * 80
    html += f'<div style="position: absolute; left: 10%; width: {progress_width}%; top: 26px; height: 3px; background-color: #22C55E; z-index: 2; transition: width 0.3s ease;"></div>'
    
    for i, step in enumerate(steps):
        is_active = i <= current_idx
        is_current = i == current_idx
        
        # Color definitions
        circle_bg = "#22C55E" if is_active else "#161B22"
        circle_border = "#22C55E" if is_active else "#2D3748"
        icon_color = "#FFFFFF" if is_active else "#94A3B8"
        text_color = "#FFFFFF" if is_active else "#94A3B8"
        font_weight = "600" if is_current else "500"
        
        # Select icon for each stage
        icons = ["file-plus", "handshake", "package", "check-circle"]
        
        html += f"""<div style="display: flex; flex-direction: column; align-items: center; width: 20%; z-index: 3; text-align: center;">
<div style="width: 32px; height: 32px; border-radius: 50%; background-color: {circle_bg}; border: 2px solid {circle_border}; display: flex; align-items: center; justify-content: center; color: {icon_color}; margin-bottom: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.5);">
<i data-lucide="{icons[i]}" style="width: 14px; height: 14px;"></i>
</div>
<span style="font-size: 0.8rem; color: {text_color}; font-weight: {font_weight};">{step}</span>
</div>"""
        
    html += '</div></div>'
    html = html.replace('\n\n', '\n'); html = html.replace('\n    \n', '\n'); st.markdown(html, unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_empty_state(title: str, description: str, icon: str = "inbox"):
    """
    Renders an elegant dark placeholder for empty data lists.
    """
    st.markdown(f"""
<div class="premium-card fade-in" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem 1.5rem; text-align: center; border-style: dashed;">
<div style="background-color: rgba(45, 55, 72, 0.3); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #94A3B8; margin-bottom: 1rem; border: 1px solid #2D3748;">
<i data-lucide="{icon}" style="width: 30px; height: 30px;"></i>
</div>
<h4 style="margin: 0; color: #FFFFFF; font-size: 1.1rem; font-weight: 600;">{title}</h4>
<p style="margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 0.9rem; max-width: 350px;">{description}</p>
</div>
""", unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)


def render_skeleton_card():
    """
    Renders a single skeleton pulse card placeholder.
    """
    st.markdown("""
<div class="skeleton-card">
<div class="skeleton-bar skeleton-title"></div>
<div class="skeleton-bar skeleton-desc"></div>
<div class="skeleton-bar skeleton-desc" style="width: 75%;"></div>
<div class="skeleton-bar skeleton-meta" style="margin-top: 15px;"></div>
</div>
""", unsafe_allow_html=True)


def render_skeleton_grid(count: int = 3):
    """
    Renders a grid layout of skeleton pulse cards.
    """
    for _ in range(count):
        render_skeleton_card()


def safe_rerun():
    """
    Reruns the Streamlit application using the available rerun method.
    """
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()



SIDEBAR_CSS = """
/* Custom Sidebar Layout */
.custom-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 250px;
    height: 100vh;
    background-color: var(--sidebar);
    color: #ffffff;
    z-index: 999999;
    transition: width 0.3s ease;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.custom-sidebar.collapsed {
    width: 80px;
}

/* Adjust Streamlit main container to accommodate sidebar */
[data-testid="stAppViewContainer"] .block-container {
    margin-left: 250px !important;
    transition: margin-left 0.3s ease !important;
    max-width: calc(100% - 250px) !important;
}

body.sidebar-collapsed [data-testid="stAppViewContainer"] .block-container {
    margin-left: 80px !important;
    max-width: calc(100% - 80px) !important;
}

.sidebar-header {
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-header h2 {
    color: #ffffff;
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    white-space: nowrap;
    opacity: 1;
    transition: opacity 0.2s;
}
.custom-sidebar.collapsed .sidebar-header h2 {
    opacity: 0;
    width: 0;
    overflow: hidden;
}

.sidebar-toggle {
    background: none;
    border: none;
    color: #ffffff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    border-radius: 6px;
}
.sidebar-toggle:hover {
    background-color: var(--sidebar-hover);
}

.sidebar-nav {
    flex-grow: 1;
    padding: 1.5rem 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
    overflow-y: auto;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 1.5rem;
    color: #94A3B8;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    transition: all 0.2s;
    white-space: nowrap;
}
.nav-item:hover {
    background-color: var(--sidebar-hover);
    color: #ffffff;
}
.nav-item.active {
    background-color: var(--accent);
    color: #ffffff;
    border-right: 4px solid #ffffff;
}
.custom-sidebar.collapsed .nav-text {
    display: none;
}
.custom-sidebar.collapsed .nav-item {
    justify-content: center;
    padding: 10px 0;
}

.sidebar-footer {
    padding: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    gap: 12px;
}
.custom-sidebar.collapsed .sidebar-footer {
    justify-content: center;
    padding: 1.5rem 0;
}
.custom-sidebar.collapsed .footer-info {
    display: none;
}
"""

SIDEBAR_JS = """
<script>
function toggleSidebar() {
    const sidebar = window.parent.document.querySelector('.custom-sidebar');
    const body = window.parent.document.body;
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        body.classList.toggle('sidebar-collapsed');
    }
}

// Inject sidebar directly into the parent document body so it breaks out of the iframe
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        const parentBody = window.parent.document.body;
        const mySidebar = document.getElementById("campus-custom-sidebar");
        
        if (mySidebar && !window.parent.document.getElementById("campus-custom-sidebar")) {
            parentBody.appendChild(mySidebar);
        }
    }, 500);
});
</script>
"""


def render_custom_sidebar(user, current_page):
    nav_items = [
        {"name": "Dashboard", "icon": "home"},
        {"name": "Events", "icon": "calendar"},
        {"name": "Announcements", "icon": "megaphone"},
        {"name": "Resources", "icon": "folder-open"},
        {"name": "Logistics", "icon": "truck"},
        {"name": "Lost & Found", "icon": "package"},
        {"name": "Profile", "icon": "user"}
    ]
    
    html = f"""
<style>{SIDEBAR_CSS}
@media (max-width: 768px) {{
    .custom-sidebar {{ width: 60px !important; }}
    .custom-sidebar .nav-text, .custom-sidebar .sidebar-header h2, .custom-sidebar .footer-info {{ display: none !important; }}
    .custom-sidebar .nav-item {{ justify-content: center !important; padding: 10px 0 !important; }}
    .custom-sidebar .sidebar-footer {{ justify-content: center !important; padding: 1.5rem 0 !important; }}
    [data-testid="stAppViewContainer"] .block-container {{ margin-left: 60px !important; max-width: calc(100% - 60px) !important; padding-top: 50px !important;}}
}}
</style>
{SIDEBAR_JS}

<div id="campus-custom-sidebar" class="custom-sidebar">
<div class="sidebar-header">
<button class="sidebar-toggle" onclick="toggleSidebar()">
<i data-lucide="menu"></i>
</button>
<h2>CampusConnect</h2>
</div>

<div class="sidebar-nav">
"""
    
    for item in nav_items:
        active_class = "active" if current_page == item["name"] else ""
        html += f"""<a href="javascript:void(0);" onclick="window.top.location.href = window.top.location.pathname + '?page=' + encodeURIComponent('{item['name']}');" class="nav-item {active_class}">
<i data-lucide="{item['icon']}"></i>
<span class="nav-text">{item['name']}</span>
</a>"""
        
    html += f"""</div>
<div class="sidebar-footer">
<img src="{user['avatar_url']}" style="width: 36px; height: 36px; border-radius: 50%; background-color:#161B22; border: 1px solid #2D3748;" />
<div class="footer-info" style="overflow: hidden; flex-grow: 1;">
<div style="font-weight: 600; color: #FFFFFF; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user['name']}</div>
<div style="font-size: 0.75rem; color: var(--success); font-weight: 500;">{user.get('tomatos', 0)} Tomatoes</div>
</div>
<a href="/?page=SignOut" target="_parent" class="nav-text" style="color: #94A3B8; margin-left: auto;">
<i data-lucide="log-out" style="width: 18px;"></i>
</a>
</div>
</div>"""
    
    html = html.replace('\n\n', '\n'); html = html.replace('\n    \n', '\n'); st.markdown(html, unsafe_allow_html=True)
    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)
