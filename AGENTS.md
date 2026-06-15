# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Running the App

```bash
pip install streamlit supabase
streamlit run app.py
```

App runs at `http://localhost:8501`. No build step needed.

## Architecture

Three-layer architecture with strict separation:

1. **`app.py`** — Entry point. Handles login/session state, page routing via `?page=` query params, and renders the active module.
2. **`services.py`** — Business logic layer. Stateless service classes (`UserService`, `EventService`, `ParcelService`, `TomatoService`, etc.) that validate constraints before delegating to repositories.
3. **`repositories.py`** — Data access layer. Every function has a dual-mode pattern: try Supabase first, fall back to `CampusMockDatabase` (JSON file).

**Modules** (`modules/`): Each page is a standalone module with a single `render(user)` function — `dashboard`, `events`, `announcements`, `resources`, `logistics`, `lost_found`, `profile`.

**`ui_components.py`**: All custom HTML/CSS/JS. Injects global styles, renders the custom sidebar, and provides the Lucide icon CDN. Streamlit's native sidebar is hidden; navigation uses `st.experimental_set_query_params(page=...)`.

## Database: Dual-Mode

`repositories.py` auto-detects credentials at import time:
- **Mock mode (default):** JSON file at `campus_db.json`. Initialized with seed data on first run.
- **Supabase mode:** Set `SUPABASE_URL` and `SUPABASE_KEY` in `.streamlit/secrets.toml` or as env vars. Run `schema.sql` in the Supabase SQL editor first.

The `CampusMockDatabase` class is a singleton (`mock_db`) initialized at module load. Every repository function calls `mock_db.load_or_initialize()` before operating — this means the JSON file is re-read on every call, so edits to `campus_db.json` are picked up at runtime.

## Credit System ("Tomatoes")

The in-app currency is called **tomatoes** (`tomatos` in the data model — note the intentional typo in the field name throughout). Logistics requests cost 5 tomatoes up front (held on creation); delivery completion transfers them to the helper. `TomatoService` wraps `update_user_tomatos` + `add_tomato_transaction`.

## Roles

Three user roles with different permissions:
- `student` — default
- `club_admin` — can create events and post announcements
- `admin` — can broadcast high-priority announcements

Role-based UI gating is done inside each module's `render()` function by checking `user["role"]`.

## Demo Accounts (pre-seeded in mock DB)

| Name | Email | Role |
|------|-------|------|
| Jane Doe | `jane@university.edu` | student |
| ACS Club | `acs@university.edu` | club_admin |
| Dr. Arthur | `registrar@university.edu` | admin |

## Key Conventions

- Navigation: always use `st.experimental_set_query_params(page="PageName")` followed by `ui_components.safe_rerun()`.
- All HTML rendered with `st.markdown(..., unsafe_allow_html=True)`.
- Lucide icons are loaded via CDN and rendered after every page — `st.markdown(ui_components.LUCIDE_CDN, unsafe_allow_html=True)` must appear at the end of each page render.
- The `tomatos` field (not `tomatoes`) is the canonical field name in both the JSON schema and Supabase tables — keep this consistent.
