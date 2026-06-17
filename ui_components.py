import streamlit as st
from html import escape

LUCIDE_CDN = '<script src="https://unpkg.com/lucide@latest"></script><script>setTimeout(()=>{if(window.lucide)lucide.createIcons();},150);</script>'

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #F6F7FB;
  --surface: #FFFFFF;
  --surface2: #F3F5F8;
  --border: #DDE3EB;
  --border-red: rgba(221,4,38,0.18);
  --text: #111827;
  --muted: #667085;
  --red: #DD0426;
  --red2: #F43F5E;
  --green: #0F9F6E;
  --blue: #2563EB;
  --amber: #D97706;
  --sidebar-w: 256px;
  --radius: 8px;
  --shadow-sm: 0 1px 2px rgba(16,24,40,0.06);
  --shadow-md: 0 14px 35px rgba(16,24,40,0.10);
}

html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  background-image:
    linear-gradient(180deg, rgba(255,255,255,0.78), rgba(246,247,251,0.92)),
    radial-gradient(circle at 18% 0%, rgba(221,4,38,0.08), transparent 28%),
    radial-gradient(circle at 100% 8%, rgba(37,99,235,0.07), transparent 25%);
  background-attachment: fixed;
  color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.block-container {
  padding: 2rem 2.25rem 3rem calc(var(--sidebar-w) + 2.25rem) !important;
  max-width: 1440px !important;
}

/* Hide Streamlit chrome + its sidebar */
#MainMenu, header, footer,
div[data-testid="stDecoration"],
div[data-testid="stToolbar"] { display: none !important; }

/* Native Streamlit sidebar is the real app menu. */
section[data-testid="stSidebar"] {
  display: block !important;
  width: var(--sidebar-w) !important;
  min-width: var(--sidebar-w) !important;
  background: rgba(255,255,255,0.96) !important;
  border-right: 1px solid rgba(221,227,235,0.92) !important;
  box-shadow: 8px 0 30px rgba(16,24,40,0.07) !important;
}
section[data-testid="stSidebar"] > div {
  background: transparent !important;
  padding: 0.75rem 0.625rem !important;
}
section[data-testid="stSidebar"] .stButton > button {
  justify-content: flex-start !important;
  height: 38px !important;
  border-radius: var(--radius) !important;
  border: 1px solid transparent !important;
  background: transparent !important;
  color: var(--muted) !important;
  font-weight: 700 !important;
  padding: 0 11px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--surface2) !important;
  border-color: rgba(17,24,39,0.06) !important;
  color: var(--text) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button:disabled {
  background: #FFF1F3 !important;
  border-color: rgba(221,4,38,0.14) !important;
  color: var(--red) !important;
  opacity: 1 !important;
}
div[data-testid="collapsedControl"] { display: none !important; }

/* Streamlit/BaseWeb text can inherit very pale theme colors. Keep form copy readable. */
.stMarkdown, .stMarkdown p, .stText, p, label,
div[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] *,
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label *,
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label *,
div[data-testid="stTextArea"] label,
div[data-testid="stTextArea"] label *,
div[data-testid="stNumberInput"] label,
div[data-testid="stNumberInput"] label *,
div[data-testid="stDateInput"] label,
div[data-testid="stDateInput"] label * {
  color: var(--text) !important;
  opacity: 1 !important;
}

div[data-testid="stRadio"] [role="radiogroup"] {
  gap: 1rem !important;
  justify-content: center !important;
}

div[data-testid="stRadio"] label {
  background: rgba(255,255,255,0.82) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 7px 10px !important;
}

div[data-testid="stRadio"] label:has(input:checked) {
  border-color: rgba(221,4,38,0.35) !important;
  background: #FFF1F3 !important;
}

/* ── Inputs ─────────────────────────────────────────────── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input {
  background: #FFFFFF !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  transition: border-color 0.2s !important;
}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stNumberInput"] input::placeholder,
div[data-testid="stDateInput"] input::placeholder {
  color: #98A2B3 !important;
  opacity: 1 !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stNumberInput"] input:focus {
  border-color: var(--red) !important;
  box-shadow: 0 0 0 3px rgba(221,4,38,0.08) !important;
  outline: none !important;
}
div[data-testid="stSelectbox"] > div {
  background: #FFFFFF !important;
  color: var(--text) !important;
  border-color: var(--border) !important;
}
div[data-testid="stFileUploader"] {
  background: var(--surface2) !important;
  border: 1px dashed var(--border) !important;
  border-radius: 10px !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
div[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(135deg, var(--red), var(--red2)) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius) !important;
  font-weight: 600 !important;
  transition: opacity 0.2s, transform 0.15s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
  opacity: 0.85 !important;
  transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
  background: #FFFFFF !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-weight: 500 !important;
  transition: border-color 0.2s, background 0.2s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
  border-color: var(--red) !important;
  background: rgba(221,4,38,0.04) !important;
}

button,
button *,
div[data-testid^="stBaseButton"] *,
div[data-testid="stButton"] button *,
div[data-testid="stDownloadButton"] button * {
  color: inherit !important;
  opacity: 1 !important;
}

div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button,
div[data-testid^="stBaseButton-secondary"],
div[data-testid^="stBaseButton-tertiary"] {
  background: #FFFFFF !important;
  color: var(--text) !important;
  border-color: var(--border) !important;
  opacity: 1 !important;
}

div[data-testid="stButton"] button[kind="primary"],
button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primaryFormSubmit"],
div[data-testid^="stBaseButton-primary"] {
  background: var(--red) !important;
  color: #FFFFFF !important;
  border-color: var(--red) !important;
  opacity: 1 !important;
  -webkit-text-fill-color: #FFFFFF !important;
}

button:disabled,
button[disabled],
div[data-testid="stButton"] button:disabled,
div[data-testid="stDownloadButton"] button:disabled {
  background: #FFF1F3 !important;
  color: var(--red) !important;
  border-color: rgba(221,4,38,0.18) !important;
  opacity: 1 !important;
  -webkit-text-fill-color: var(--red) !important;
}

div[data-testid="stButton"] button[kind="primary"]:disabled,
button[kind="primaryFormSubmit"]:disabled,
button[data-testid="stBaseButton-primaryFormSubmit"]:disabled,
div[data-testid^="stBaseButton-primary"]:disabled {
  background: var(--red) !important;
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
}

div[data-testid="stPills"] button,
div[data-testid="stPills"] button * {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

div[data-testid="stPills"] button[aria-pressed="true"],
div[data-testid="stPills"] button[aria-selected="true"] {
  background: #FFF1F3 !important;
  border-color: rgba(221,4,38,0.22) !important;
  color: var(--red) !important;
  -webkit-text-fill-color: var(--red) !important;
}

/* Streamlit pills/segmented controls can ignore normal button rules in dark themes. */
button[kind="pills"],
button[kind="secondary"],
button[data-testid*="stBaseButton-pills"],
button[data-testid="stBaseButton-secondary"],
div[data-testid="stPills"] button,
div[data-testid="stPills"] [role="button"] {
  background: #FFFFFF !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  border: 1px solid var(--border) !important;
  opacity: 1 !important;
}

button[kind="pills"] *,
button[kind="secondary"] *,
button[data-testid*="stBaseButton-pills"] *,
button[data-testid="stBaseButton-secondary"] *,
div[data-testid="stPills"] button *,
div[data-testid="stPills"] [role="button"] * {
  color: inherit !important;
  -webkit-text-fill-color: inherit !important;
  opacity: 1 !important;
}

button[kind="pills"][aria-pressed="true"],
button[kind="pills"][aria-selected="true"],
button[data-testid*="stBaseButton-pills"][aria-pressed="true"],
button[data-testid*="stBaseButton-pills"][aria-selected="true"],
div[data-testid="stPills"] button[aria-pressed="true"],
div[data-testid="stPills"] button[aria-selected="true"] {
  background: #FFF1F3 !important;
  color: var(--red) !important;
  -webkit-text-fill-color: var(--red) !important;
  border-color: rgba(221,4,38,0.35) !important;
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
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.18); }

/* ── Custom Sidebar ──────────────────────────────────────── */
.cc-sidebar {
  position: fixed;
  top: 0; left: 0;
  width: var(--sidebar-w);
  height: 100vh;
  background: rgba(255,255,255,0.96);
  border-right: 1px solid rgba(221,227,235,0.92);
  box-shadow: 8px 0 30px rgba(16,24,40,0.07);
  backdrop-filter: blur(14px);
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
  border-bottom: 1px solid var(--border);
  cursor: default;
  user-select: none;
}
.cc-logo {
  width: 34px; height: 34px;
  background: #111827;
  border-radius: var(--radius);
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 8px 18px rgba(17,24,39,0.18);
}
.cc-logo svg, .cc-logo i { width: 18px; height: 18px; }
.cc-brand-text {
  font-size: 0.95rem; font-weight: 800;
  color: var(--text);
  letter-spacing: 0;
}

.cc-nav {
  flex: 1;
  padding: 0.75rem 0.625rem;
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow-y: auto;
}

.cc-nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 11px;
  border-radius: var(--radius);
  color: var(--muted);
  font-size: 0.85rem;
  font-weight: 650;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
  position: relative;
  user-select: none;
  border: 1px solid transparent;
}
.cc-nav-item:hover {
  background: var(--surface2);
  color: var(--text);
  border-color: rgba(17,24,39,0.06);
}
.cc-nav-item.active {
  background: #FFF1F3;
  color: var(--red);
  border-color: rgba(221,4,38,0.14);
  font-weight: 800;
}
.cc-nav-item.active::before {
  content: '';
  position: absolute;
  left: 0; top: 5px; bottom: 5px;
  width: 3px;
  background: linear-gradient(180deg, var(--red), var(--red2));
  border-radius: 0 3px 3px 0;
}
.cc-nav-item i, .cc-nav-item svg {
  width: 16px; height: 16px;
  flex-shrink: 0;
}

.cc-footer {
  padding: 0.75rem 0.875rem;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 9px;
}
.cc-avatar {
  width: 30px; height: 30px;
  border-radius: var(--radius);
  background: #FFF1F3;
  border: 1px solid rgba(221,4,38,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700;
  color: var(--red);
  flex-shrink: 0;
  overflow: hidden;
}
.cc-avatar img { width: 100%; height: 100%; object-fit: cover; }
.cc-user { flex: 1; min-width: 0; }
.cc-user-name {
  font-size: 0.78rem; font-weight: 800; color: var(--text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.cc-user-bal { font-size: 0.68rem; color: var(--muted); margin-top: 1px; }
.cc-signout {
  color: #94A3B8;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  width: 26px; height: 26px;
  border-radius: var(--radius);
  border: none; background: transparent;
  transition: color 0.15s, background 0.15s;
  flex-shrink: 0;
}
.cc-signout:hover { color: var(--red); background: rgba(221,4,38,0.06); }
.cc-signout svg { width: 14px; height: 14px; }

/* ── Cards ───────────────────────────────────────────────── */
.premium-card {
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-bottom: 0.875rem;
  box-shadow: var(--shadow-sm);
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.premium-card:hover {
  border-color: rgba(221,4,38,0.18);
  box-shadow: 0 10px 24px rgba(16,24,40,0.08);
  transform: translateY(-1px);
}

/* ── Page headers ────────────────────────────────────────── */
.page-title {
  font-size: 1.55rem; font-weight: 800;
  color: var(--text); letter-spacing: 0;
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 4px;
}
.page-subtitle { font-size: 0.875rem; color: var(--muted); margin-bottom: 1.75rem; }

/* ── Badges ──────────────────────────────────────────────── */
.category-tag {
  background: var(--surface2);
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
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.125rem 1.25rem;
  display: flex; align-items: center; gap: 1rem;
  box-shadow: var(--shadow-sm);
  transition: border-color 0.2s, transform 0.2s;
}
.metric-box:hover { border-color: rgba(221,4,38,0.18); transform: translateY(-1px); box-shadow: 0 10px 22px rgba(16,24,40,0.08); }
.metric-icon-wrapper {
  border-radius: var(--radius); width: 42px; height: 42px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.metric-value { font-size: 1.6rem; font-weight: 800; color: var(--text); line-height: 1; letter-spacing: 0; }
.metric-label { font-size: 0.73rem; color: var(--muted); font-weight: 500; margin-top: 3px; }

.metric-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dashboard-shell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.25rem;
  background: #111827;
  color: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
}
.dashboard-shell-title {
  margin: 0 0 4px 0;
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0;
}
.dashboard-shell-text {
  margin: 0;
  color: rgba(255,255,255,0.72);
  font-size: 0.83rem;
}
.dashboard-shell-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 10px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.16);
  border-radius: var(--radius);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 750;
  white-space: nowrap;
}

.cc-section-title {
  margin: 0.25rem 0 0.75rem 0;
  color: var(--text);
  font-size: 1.05rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0;
}

.cc-top-menu-label {
  margin: 0;
  color: var(--muted);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
}

.cc-top-menu {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  overflow-x: auto;
  overflow-y: hidden;
  margin: -0.25rem 0 1.25rem;
  padding: 0.75rem;
  width: calc(100vw - var(--sidebar-w) - 5rem);
  max-width: 1184px;
  box-sizing: border-box;
  background: rgba(255,255,255,0.86);
  border: 1px solid rgba(221,227,235,0.92);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(16px);
}

.cc-top-menu a {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  height: 34px;
  padding: 0 11px;
  border-radius: var(--radius);
  color: var(--muted);
  font-size: 0.8rem;
  font-weight: 800;
  text-decoration: none;
  border: 1px solid transparent;
}

.cc-top-menu-label {
  flex: 0 0 auto;
}

.cc-top-menu a:hover {
  color: var(--text);
  background: var(--surface2);
  border-color: rgba(17,24,39,0.06);
}

.cc-top-menu a.active {
  color: var(--red);
  background: #FFF1F3;
  border-color: rgba(221,4,38,0.16);
}

.cc-login-menu-hint {
  background: #FFF7ED;
  border: 1px solid rgba(217,119,6,0.24);
  color: #92400E;
  border-radius: var(--radius);
  padding: 0.75rem 0.85rem;
  margin: 0.75rem 0 1rem;
  font-size: 0.84rem;
  font-weight: 750;
  text-align: center;
}

.cc-login-hero {
  padding: 1.25rem 0 0.5rem;
}

.cc-login-kicker {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 9px;
  border-radius: var(--radius);
  background: #FFF1F3;
  color: var(--red);
  font-size: 0.75rem;
  font-weight: 850;
  border: 1px solid rgba(221,4,38,0.14);
}

.cc-login-title {
  margin: 1rem 0 0;
  color: var(--text);
  font-size: clamp(2.35rem, 5vw, 4.8rem);
  line-height: 0.96;
  font-weight: 900;
  letter-spacing: 0;
}

.cc-login-copy {
  margin: 1rem 0 1.25rem;
  color: var(--muted);
  max-width: 560px;
  font-size: 1rem;
  line-height: 1.65;
}

.cc-login-proof {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.cc-login-proof div {
  background: rgba(255,255,255,0.78);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem;
}

.cc-login-proof strong {
  display: block;
  color: var(--text);
  font-size: 1.25rem;
  line-height: 1;
}

.cc-login-proof span {
  display: block;
  margin-top: 4px;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
}

.cc-auth-panel {
  background: rgba(255,255,255,0.92);
  border: 1px solid rgba(221,227,235,0.92);
  border-radius: var(--radius);
  padding: 1.1rem;
  box-shadow: var(--shadow-md);
}

.cc-auth-title {
  color: var(--text);
  font-size: 1.05rem;
  font-weight: 850;
  margin: 0 0 4px;
}

.cc-auth-subtitle {
  color: var(--muted);
  font-size: 0.8rem;
  line-height: 1.5;
  margin: 0 0 1rem;
}

/* ── Skeleton ────────────────────────────────────────────── */
@keyframes shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position: 600px 0; }
}
.skeleton-bar {
  background: linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 50%, #F1F5F9 75%);
  background-size: 1200px 100%;
  animation: shimmer 1.4s infinite linear;
  border-radius: 5px; height: 14px; margin-bottom: 10px;
}
.skeleton-card {
  background: #FFFFFF; border: 1px solid #E2E8F0;
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
  .block-container { padding: 1.25rem 1rem 2rem calc(var(--sidebar-w) + 1rem) !important; }
  .dashboard-shell { align-items: flex-start; flex-direction: column; }
  .cc-top-menu {
    position: static;
    width: calc(100vw - var(--sidebar-w) - 2rem);
  }
  .cc-login-proof { grid-template-columns: 1fr; }
}

@media (max-width: 980px) {
  .metrics-container { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 560px) {
  .metrics-container { grid-template-columns: 1fr; }
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
        border = "#DD0426" if active else "var(--border)"
        icon_color = "#fff" if active else "var(--muted)"
        text_c = "var(--text)" if active else "var(--muted)"
        weight = "700" if i == idx else "500"
        shadow = "0 0 12px rgba(221,4,38,0.4)" if active else "none"
        circles += f"""<div style="display:flex;flex-direction:column;align-items:center;width:25%;z-index:3;text-align:center;">
  <div style="width:32px;height:32px;border-radius:50%;background:{bg};border:2px solid {border};
              display:flex;align-items:center;justify-content:center;color:{icon_color};margin-bottom:7px;box-shadow:{shadow};">
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
    <div style="position:absolute;left:12.5%;right:12.5%;top:22px;height:2px;background:var(--border);z-index:1;"></div>
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
  <div style="width:48px;height:48px;border-radius:50%;background:rgba(0,0,0,0.03);
              border:1px solid var(--border);display:flex;align-items:center;
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


def render_top_menu(current_page: str):
    """Render a visible in-page navigation fallback above the active module."""
    nav_items = [
        "Dashboard",
        "Events",
        "Announcements",
        "Resources",
        "Logistics",
        "Lost & Found",
        "Profile",
    ]
    active_page = current_page if current_page in nav_items else "Dashboard"
    st.markdown('<div class="cc-top-menu-label">Menu</div>', unsafe_allow_html=True)
    if hasattr(st, "pills"):
        selected = st.pills(
            "Menu",
            nav_items,
            default=active_page,
            key=f"_top_nav_pills_{active_page}",
            label_visibility="collapsed",
        )
    else:
        selected = st.selectbox(
            "Menu",
            nav_items,
            index=nav_items.index(active_page),
            key=f"_top_nav_select_{active_page}",
            label_visibility="collapsed",
        )
    if selected and selected != current_page:
        try:
            st.query_params["page"] = selected
        except AttributeError:
            st.experimental_set_query_params(page=selected)
        safe_rerun()
    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)



def render_custom_sidebar(user: dict, current_page: str):
    """Render a session-safe Streamlit sidebar menu."""
    nav_items = [
        ("Dashboard", "home"),
        ("Events", "calendar"),
        ("Announcements", "megaphone"),
        ("Resources", "folder-open"),
        ("Logistics", "truck"),
        ("Lost & Found", "package-search"),
        ("Profile", "user"),
    ]

    balance = user.get("tomatos", user.get("tomato_balance", 0))
    initials = escape("".join(w[0].upper() for w in user.get("name", "?").split()[:2]) or "?")
    user_name = escape(user.get("name", ""))

    with st.sidebar:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;padding:0.25rem 0.25rem 0.9rem 0.25rem;
            border-bottom:1px solid var(--border);margin-bottom:0.75rem;">
  <div class="cc-logo"><i data-lucide="graduation-cap"></i></div>
  <div>
    <div style="font-weight:800;color:var(--text);font-size:0.95rem;">CampusConnect</div>
    <div style="font-size:0.68rem;color:var(--muted);font-weight:650;">Campus operations hub</div>
  </div>
</div>
""", unsafe_allow_html=True)

        for name, _icon in nav_items:
            if current_page == name:
                st.button(name, key=f"_nav_active_{name}", type="primary", disabled=True, use_container_width=True)
            elif st.button(name, key=f"_nav_{name}", use_container_width=True):
                try:
                    st.query_params["page"] = name
                except AttributeError:
                    st.experimental_set_query_params(page=name)
                safe_rerun()

        st.markdown(f"""
<div style="border-top:1px solid var(--border);margin-top:0.75rem;padding:0.85rem 0.25rem 0.25rem;
            display:flex;align-items:center;gap:9px;">
  <div class="cc-avatar"><span>{initials}</span></div>
  <div style="min-width:0;flex:1;">
    <div class="cc-user-name">{user_name}</div>
    <div class="cc-user-bal">{balance} tomatoes</div>
  </div>
</div>
""", unsafe_allow_html=True)

        if st.button("Sign out", key="_nav_signout", use_container_width=True):
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

    st.markdown(LUCIDE_CDN, unsafe_allow_html=True)
