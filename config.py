"""
CampusConnect – application-wide configuration constants.
"""

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
COLORS: dict[str, str] = {
    "deep_space": "#273043",
    "lavender": "#9197AE",
    "mint_cream": "#EFF6EE",
    "strawberry": "#F02D3A",
    "scarlet": "#DD0426",
}

# ---------------------------------------------------------------------------
# User roles
# ---------------------------------------------------------------------------
ROLES: dict[str, str] = {
    "student": "student",
    "club_admin": "club_admin",
    "admin": "admin",
}

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
PAGES: list[str] = [
    "Dashboard",
    "Events",
    "Announcements",
    "Resources",
    "Logistics",
    "Lost & Found",
    "Profile",
]

PAGE_ICONS: dict[str, str] = {
    "Dashboard": "layout-dashboard",
    "Events": "calendar",
    "Announcements": "megaphone",
    "Resources": "folder-open",
    "Logistics": "package",
    "Lost & Found": "search",
    "Profile": "user",
}

# ---------------------------------------------------------------------------
# Supabase storage
# ---------------------------------------------------------------------------
STORAGE_BUCKET: str = "campusconnect"
MAX_FILE_SIZE_MB: int = 25

ALLOWED_FILE_TYPES: list[str] = [
    ".pdf",
    ".pptx",
    ".ppt",
    ".docx",
    ".doc",
    ".png",
    ".jpg",
    ".jpeg",
]

ALLOWED_MIME_TYPES: list[str] = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/png",
    "image/jpeg",
]

# ---------------------------------------------------------------------------
# Feature-specific categories / statuses
# ---------------------------------------------------------------------------
ANNOUNCEMENT_CATEGORIES: list[str] = [
    "Academic",
    "Hostel",
    "Placements",
    "Clubs",
    "General",
]

ANNOUNCEMENT_PRIORITIES: list[str] = [
    "Critical",
    "Important",
    "Normal",
]

RESOURCE_CATEGORIES: list[str] = [
    "Notes",
    "PYQs",
    "PPTs",
    "Study guides",
    "Lab Manuals",
]

LOST_FOUND_CATEGORIES: list[str] = [
    "Electronics",
    "Accessories",
    "Books",
    "Clothing",
    "ID Cards",
    "Keys",
    "Bags",
    "Other",
]

PARCEL_STATUSES: list[str] = [
    "Created",
    "Accepted",
    "Picked Up",
    "Delivered",
    "Cancelled",
]

# ---------------------------------------------------------------------------
# Tomato economy
# ---------------------------------------------------------------------------
DEFAULT_TOMATO_BALANCE: int = 50
TOMATO_DELIVERY_COST: int = 5

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_NAME: str = "CampusConnect"

# Suffix used to validate institutional e-mail addresses.
# Change this to your university's actual domain before deployment.
UNIVERSITY_EMAIL_DOMAIN: str = "university.edu"
