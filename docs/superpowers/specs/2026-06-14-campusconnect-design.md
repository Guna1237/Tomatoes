# CampusConnect Design Spec — 2026-06-14

## Stack
- Frontend/Backend: Python + Streamlit (single-entry SPA pattern, URL-param routing)
- DB: Supabase PostgreSQL (RLS enforced)
- Storage: Supabase Storage (bucket: `campusconnect`)
- Auth: Supabase Auth (email/password, JWT sessions)
- Icons: Lucide (CDN)
- Charts: Plotly

## Color System
```
deep_space:  #273043   (backgrounds, cards)
lavender:    #9197AE   (secondary text, borders)
mint_cream:  #EFF6EE   (primary text on dark)
strawberry:  #F02D3A   (alerts, destructive)
scarlet:     #DD0426   (primary actions, CTA)
```
No gradients. No glassmorphism. No neon.

## File Structure
```
app.py                         # Entry point + router
config.py                      # Colors, roles, constants
database.py                    # @cache_resource Supabase singleton
auth.py                        # Supabase Auth wrappers
schema.sql                     # Complete DB schema + RLS + indexes
requirements.txt
.streamlit/
  config.toml
  secrets.toml.example
ui/
  __init__.py
  styles.py                    # All CSS injected once at startup
  components.py                # Reusable cards, badges, empty states
  sidebar.py                   # Custom collapsible sidebar
  auth_ui.py                   # Login + signup screens
services/
  __init__.py
  user_service.py
  event_service.py
  announcement_service.py
  resource_service.py
  logistics_service.py
  lost_found_service.py
  notification_service.py
  tomato_service.py
repositories/
  __init__.py
  user_repo.py
  event_repo.py
  announcement_repo.py
  resource_repo.py
  logistics_repo.py
  lost_found_repo.py
  notification_repo.py
modules/
  __init__.py
  dashboard.py
  events.py
  announcements.py
  resources.py
  logistics.py
  lost_found.py
  profile.py
```

## Roles
- `student` — read all, write own data, register events, request logistics
- `club_admin` — all student perms + create/edit/delete own events + post announcements
- `admin` — full access, delete any record, broadcast critical announcements

## Database Tables
```
users               id(uuid PK→auth.users), email, name, role, tomato_balance(int=50), avatar_url, bio, created_at, updated_at
events              id(uuid), title, description, banner_url, date, time, venue, organizer_id(→users), organizer_name, capacity(int), registered_count(int=0), category, is_active(bool=true), created_at, updated_at
event_registrations id(uuid), event_id(→events CASCADE), user_id(→users CASCADE), registered_at, attended(bool=false), UNIQUE(event_id,user_id)
announcements       id(uuid), title, content, category(CHECK: Academic/Hostel/Placements/Clubs/General), priority(CHECK: Critical/Important/Normal), author_id(→users), author_name, is_active(bool=true), created_at, updated_at
saved_announcements id(uuid), user_id(→users), announcement_id(→announcements), saved_at, UNIQUE(user_id,announcement_id)
resources           id(uuid), title, course_code, course_name, category(Notes/PYQs/PPTs/Study guides/Lab Manuals), file_url, file_name, file_size, file_type, uploader_id(→users), uploader_name, bookmarks_count(int=0), downloads_count(int=0), is_active(bool=true), created_at
bookmarked_resources id(uuid), user_id(→users), resource_id(→resources), bookmarked_at, UNIQUE(user_id,resource_id)
parcel_requests     id(uuid), requester_id(→users), requester_name, helper_id(→users nullable), helper_name, title, description, pickup_location, delivery_location, tomatoes_offered(int=5), status(CHECK: Created/Accepted/Picked Up/Delivered/Cancelled), created_at, updated_at
tomato_transactions id(uuid), user_id(→users), amount(int), transaction_type(delivery_reward/delivery_spend/bonus/admin_grant), description, related_request_id(→parcel_requests nullable), created_at
lost_found          id(uuid), title, description, category, item_type(CHECK: Lost/Found), location, image_url, reporter_id(→users), reporter_name, status(CHECK: Open/Claimed/Resolved), claimed_by(→users nullable), created_at, updated_at
notifications       id(uuid), user_id(→users CASCADE), title, content, notification_type(event/parcel/resource/announcement/general), read(bool=false), related_id(uuid nullable), created_at
audit_logs          id(uuid), user_id(→users), action, table_name, record_id, old_values(jsonb), new_values(jsonb), created_at
```

## Key Interface Contracts

### database.py
```python
def get_client() -> Client  # @st.cache_resource
```

### auth.py
```python
def login(email, password) -> tuple[dict|None, str|None]       # (user_data, error_msg)
def signup(email, password, name, role) -> tuple[dict|None, str|None]
def logout() -> None
def get_current_session() -> dict|None                          # returns user dict or None
def reset_password(email: str) -> bool
def refresh_session() -> dict|None
```

### config.py
```python
COLORS: dict[str, str]
ROLES: dict[str, str]
PAGES: list[str]
STORAGE_BUCKET = "campusconnect"
MAX_FILE_SIZE_MB = 25
ALLOWED_FILE_TYPES = [".pdf", ".pptx", ".ppt", ".docx", ".doc", ".png", ".jpg", ".jpeg"]
```

### ui/components.py
```python
def render_card(title, subtitle="", body_html="", badge=None, actions_html="", key="") -> None
def render_metric(label, value, sub="") -> str  # returns HTML string
def render_badge(text, level="normal") -> str   # level: critical/important/normal/success
def render_empty_state(icon, title, description="", cta_label="", cta_key="") -> bool  # returns True if CTA clicked
def render_page_header(title, subtitle="", actions_html="") -> None
def inject_toast(message, kind="success") -> None    # kind: success/error/info/warning
def render_skeleton(rows=3) -> None
```

### ui/sidebar.py
```python
def render_sidebar(user: dict, current_page: str) -> str  # returns selected page name
```

### Service patterns (all services follow this):
```python
# All list methods: @st.cache_data(ttl=300) on underlying repo calls
# All write methods: call st.cache_data.clear() after mutation
# Permission errors raise PermissionError
# Validation errors raise ValueError with message
# Return type: dict for single, list[dict] for collection, bool for operations
```

### Key service methods:
```python
# EventService
get_all(search="", category="", upcoming_only=False) -> list[dict]
create(data: dict, user: dict) -> dict          # user must be club_admin or admin
register(event_id, user_id) -> tuple[bool, str]
unregister(event_id, user_id) -> tuple[bool, str]
get_registered(user_id) -> list[dict]
is_registered(event_id, user_id) -> bool

# AnnouncementService
get_all(search="", category="", priority="") -> list[dict]
create(data: dict, user: dict) -> dict          # user must be club_admin or admin
save(user_id, ann_id) -> bool
get_saved(user_id) -> list[dict]

# ResourceService
get_all(search="", category="", course="") -> list[dict]
upload(title, course_code, course_name, category, file_bytes, file_name, uploader: dict) -> dict
download_url(resource_id, user_id) -> str
bookmark(user_id, res_id) -> bool
unbookmark(user_id, res_id) -> bool

# LogisticsService
get_open_requests(exclude_user_id) -> list[dict]
get_user_requests(user_id) -> list[dict]
create_request(data: dict, user: dict) -> tuple[dict|None, str]
accept_request(req_id, helper: dict) -> tuple[bool, str]
update_status(req_id, status, user: dict) -> tuple[bool, str]

# LostFoundService
get_all(item_type="", category="") -> list[dict]
report(data: dict, image_bytes, image_name, user: dict) -> dict
claim(item_id, user: dict) -> tuple[bool, str]
resolve(item_id, user: dict) -> bool

# NotificationService
get_all(user_id) -> list[dict]
get_unread_count(user_id) -> int
mark_read(notif_id) -> bool
mark_all_read(user_id) -> bool
add(user_id, title, content, notif_type="general", related_id=None) -> None

# TomatoService
get_balance(user_id) -> int
credit(user_id, amount, desc, txn_type, related_id=None) -> bool
debit(user_id, amount, desc, txn_type, related_id=None) -> tuple[bool, str]
get_transactions(user_id) -> list[dict]
```

## Routing (app.py pattern)
```python
# Navigation: st.query_params["page"] = "Events" then st.rerun()
# Pages: Dashboard, Events, Announcements, Resources, Logistics, Lost & Found, Profile
# Auth gate: if not session → show auth_ui
# Page rendering: modules/<page>.render(user: dict)
```

## UI Patterns
- Streamlit chrome hidden via CSS (menu, footer, header, deploy button)
- Custom sidebar: HTML/CSS, toggle via st.session_state["sidebar_collapsed"]
- All cards: dark background (#1E2533), border 1px solid rgba(145,151,174,0.15), border-radius 12px
- Hover: translateY(-2px) + border-color rgba(221,4,38,0.4)
- Font: Inter (Google Fonts CDN)
- Transitions: 0.2s ease on all interactive elements
- No emojis in production UI (use Lucide icons only)
- Lucide: loaded via CDN script tag injected after every render

## Caching Strategy
- `@st.cache_data(ttl=300)` on all repo read functions
- After any write: `st.cache_data.clear()` + `st.rerun()`
- Supabase client: `@st.cache_resource` (never expires, one instance)
- Notification count: `@st.cache_data(ttl=30)` (shorter TTL for real-time feel)

## Security
- All file uploads: validate extension + MIME type + size ≤ 25MB
- Supabase SDK: parameterized queries (no SQL injection possible)
- RLS: users can only access their own private data; public data readable by all authenticated users
- Service layer: re-validate permissions even if RLS is set (defense in depth)
- Audit log every: event create/delete, announcement create, resource upload, parcel status change
