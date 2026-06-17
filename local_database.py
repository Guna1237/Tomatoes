from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional


DB_PATH = Path(__file__).with_name("campus_db.json")
SEED_UPLOAD_DIR = Path(__file__).with_name("uploads") / "resources"


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _id() -> str:
    return str(uuid.uuid4())


def _seed_resource_path() -> str:
    SEED_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = SEED_UPLOAD_DIR / "sample-data-structures-notes.pdf"
    if not path.exists():
        path.write_bytes(
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Count 0>>endobj\n"
            b"trailer<</Root 1 0 R>>\n%%EOF\n"
        )
    return str(path)


DEMO_USERS = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "jane@university.edu",
        "name": "Jane Doe",
        "role": "student",
        "tomato_balance": 50,
        "tomatos": 50,
        "bio": "Computer Science, Year 3",
        "avatar_url": "",
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "email": "acs@university.edu",
        "name": "ACS Club",
        "role": "club_admin",
        "tomato_balance": 50,
        "tomatos": 50,
        "bio": "Association of Computer Science",
        "avatar_url": "",
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "email": "registrar@university.edu",
        "name": "Dr. Arthur",
        "role": "admin",
        "tomato_balance": 100,
        "tomatos": 100,
        "bio": "Office of the Registrar",
        "avatar_url": "",
    },
    {
        "id": "00000000-0000-0000-0000-000000000009",
        "email": "sm25ubef009@mahindrauniversity",
        "name": "Guna Ratnam Pasupuleti",
        "role": "student",
        "tomato_balance": 50,
        "tomatos": 50,
        "bio": "Mahindra University student",
        "avatar_url": "",
        "password_hash": "sha256$738531198d1b9cfe0e9973d0bbf87845e560f6438dface20acb4de1fc836c3df",
    },
]


def _seed() -> dict[str, list[dict[str, Any]]]:
    today = date.today()
    created = _now()
    users = [{**u, "created_at": created, "updated_at": created} for u in DEMO_USERS]
    return {
        "users": users,
        "events": [
            {
                "id": _id(),
                "title": "AI Study Jam",
                "description": "Hands-on session for building useful campus tools with AI.",
                "banner_url": "",
                "date": (today + timedelta(days=5)).isoformat(),
                "time": "16:00:00",
                "venue": "Innovation Lab",
                "organizer_id": users[1]["id"],
                "organizer_name": users[1]["name"],
                "capacity": 80,
                "registered_count": 0,
                "category": "Clubs",
                "is_active": True,
                "created_at": created,
                "updated_at": created,
            }
        ],
        "event_registrations": [],
        "announcements": [
            {
                "id": _id(),
                "title": "Semester Registration Opens",
                "content": "Course registration is open this week. Please review your elective choices.",
                "category": "Academic",
                "priority": "Important",
                "author_id": users[2]["id"],
                "author_name": users[2]["name"],
                "is_active": True,
                "created_at": created,
                "updated_at": created,
            }
        ],
        "saved_announcements": [],
        "resources": [
            {
                "id": _id(),
                "title": "Data Structures Quick Notes",
                "course_code": "CS201",
                "course_name": "Data Structures",
                "category": "Notes",
                "file_url": _seed_resource_path(),
                "file_name": "sample-data-structures-notes.pdf",
                "file_type": "pdf",
                "file_size_mb": 0.01,
                "uploader_id": users[1]["id"],
                "uploader_name": users[1]["name"],
                "bookmarks_count": 0,
                "downloads_count": 0,
                "is_active": True,
                "created_at": created,
            }
        ],
        "bookmarked_resources": [],
        "parcel_requests": [],
        "tomato_transactions": [],
        "lost_found": [],
        "notifications": [],
    }


def _load() -> dict[str, list[dict[str, Any]]]:
    if not DB_PATH.exists():
        data = _seed()
        _save(data)
        return data
    try:
        with DB_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        data = _seed()
    seed = _seed()
    changed = False
    for table, rows in seed.items():
        if table not in data:
            data[table] = rows
            changed = True
    existing_users = {u.get("email", "").lower(): u for u in data.get("users", [])}
    for seeded_user in seed["users"]:
        email = seeded_user.get("email", "").lower()
        existing_user = existing_users.get(email)
        if existing_user is None:
            data.setdefault("users", []).append(seeded_user)
            changed = True
            continue
        for field in ("password_hash",):
            if seeded_user.get(field) and existing_user.get(field) != seeded_user[field]:
                existing_user[field] = seeded_user[field]
                changed = True
    if changed:
        _save(data)
    return data


def _save(data: dict[str, list[dict[str, Any]]]) -> None:
    with DB_PATH.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def _with_aliases(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row)
    if "tomato_balance" in row:
        row.setdefault("tomatos", row["tomato_balance"])
    if "tomatos" in row:
        row.setdefault("tomato_balance", row["tomatos"])
    if "tomato_reward" in row:
        row.setdefault("tomatoes_offered", row["tomato_reward"])
        row.setdefault("tomatos_offered", row["tomato_reward"])
    if "tomatoes_offered" in row:
        row.setdefault("tomato_reward", row["tomatoes_offered"])
        row.setdefault("tomatos_offered", row["tomatoes_offered"])
    return row


def all_rows(table: str, predicate: Optional[Callable[[dict[str, Any]], bool]] = None) -> list[dict[str, Any]]:
    rows = deepcopy(_load().get(table, []))
    if predicate:
        rows = [r for r in rows if predicate(r)]
    return [_with_aliases(r) for r in rows]


def one(table: str, predicate: Callable[[dict[str, Any]], bool]) -> Optional[dict[str, Any]]:
    for row in all_rows(table, predicate):
        return row
    return None


def insert(table: str, data: dict[str, Any]) -> dict[str, Any]:
    db = _load()
    row = _with_aliases(data)
    row.setdefault("id", _id())
    row.setdefault("created_at", _now())
    if table in {"users", "events", "announcements", "parcel_requests", "lost_found"}:
        row.setdefault("updated_at", row["created_at"])
    db.setdefault(table, []).append(row)
    _save(db)
    return deepcopy(row)


def update(table: str, row_id: str, data: dict[str, Any]) -> dict[str, Any]:
    db = _load()
    for idx, row in enumerate(db.get(table, [])):
        if row.get("id") == row_id:
            merged = _with_aliases({**row, **data, "updated_at": _now()})
            db[table][idx] = merged
            _save(db)
            return deepcopy(merged)
    return {}


def delete_where(table: str, predicate: Callable[[dict[str, Any]], bool]) -> bool:
    db = _load()
    before = len(db.get(table, []))
    db[table] = [row for row in db.get(table, []) if not predicate(row)]
    _save(db)
    return len(db[table]) != before


def set_count(table: str, row_id: str, field: str, delta: int) -> bool:
    row = one(table, lambda r: r.get("id") == row_id)
    if not row:
        return False
    update(table, row_id, {field: max(0, int(row.get(field, 0)) + delta)})
    return True
