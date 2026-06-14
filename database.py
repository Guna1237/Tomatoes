import os
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

# Check for Supabase configuration in secrets or environment safely
SUPABASE_URL = None
SUPABASE_KEY = None

try:
    if hasattr(st, "secrets") and st.secrets is not None:
        if "SUPABASE_URL" in st.secrets:
            SUPABASE_URL = st.secrets["SUPABASE_URL"]
        if "SUPABASE_KEY" in st.secrets:
            SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    pass

if not SUPABASE_URL:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
if not SUPABASE_KEY:
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
supabase_client = None

if USE_SUPABASE:
    try:
        from supabase import create_client, Client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}. Falling back to Mock Database.")
        USE_SUPABASE = False


class CampusMockDatabase:
    """
    A file-backed mock database using JSON.
    Mimics database queries and writes for zero-setup demonstration.
    """
    def __init__(self, filepath: str = "campus_db.json"):
        self.filepath = filepath
        self.data = {}
        self.load_or_initialize()

    def load_or_initialize(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.data = json.load(f)
                    return
            except Exception as e:
                pass
        
        # Initialize default mock data if file doesn't exist or is corrupted
        self.initialize_default_data()
        self.save()

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving database: {e}")

    def initialize_default_data(self):
        self.data = {
            "users": [
                {
                    "id": "u-jane-doe",
                    "email": "jane@university.edu",
                    "name": "Jane Doe",
                    "credits": 75,
                    "avatar_url": "https://api.dicebear.com/7.x/adventurer/svg?seed=jane",
                    "role": "student",
                    "created_at": "2026-06-01T10:00:00Z"
                },
                {
                    "id": "u-john-smith",
                    "email": "john@university.edu",
                    "name": "John Smith",
                    "credits": 45,
                    "avatar_url": "https://api.dicebear.com/7.x/adventurer/svg?seed=john",
                    "role": "student",
                    "created_at": "2026-06-02T11:00:00Z"
                },
                {
                    "id": "u-club-acs",
                    "email": "acs@university.edu",
                    "name": "Association of Computer Students (ACS)",
                    "credits": 150,
                    "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=ACS",
                    "role": "club_admin",
                    "created_at": "2026-05-15T09:00:00Z"
                },
                {
                    "id": "u-registrar",
                    "email": "registrar@university.edu",
                    "name": "Dr. Arthur (Registrar Office)",
                    "credits": 999,
                    "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=registrar",
                    "role": "admin",
                    "created_at": "2026-05-01T08:00:00Z"
                }
            ],
            "events": [
                {
                    "id": 1,
                    "title": "HackCampus 2026",
                    "description": "The ultimate 24-hour university hackathon. Team up to solve local campus challenges, build cool prototypes, and win awesome gadgets! Free pizza, energy drinks, and swag for all participants. Organized by ACS.",
                    "banner_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&q=80&w=800",
                    "date": "2026-06-25",
                    "time": "10:00",
                    "venue": "Main Auditorium & Lab Area",
                    "organizer_id": "u-club-acs",
                    "organizer_name": "ACS Club",
                    "capacity": 150,
                    "registered_count": 85,
                    "created_at": "2026-06-10T12:00:00Z"
                },
                {
                    "id": 2,
                    "title": "Summer Tech Symposium",
                    "description": "Join us for guest lectures from top industry experts in Artificial Intelligence, Cybersecurity, and Software Architecture. Interactive Q&A and networking session following the panel. Organized by ACS.",
                    "banner_url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&q=80&w=800",
                    "date": "2026-06-28",
                    "time": "14:00",
                    "venue": "Hall B, Academic Block 2",
                    "organizer_id": "u-club-acs",
                    "organizer_name": "ACS Club",
                    "capacity": 200,
                    "registered_count": 120,
                    "created_at": "2026-06-11T14:00:00Z"
                },
                {
                    "id": 3,
                    "title": "Campus Cultural Fest 2026",
                    "description": "A vibrant celebration of music, dance, theater, and international cuisines! Enjoy live band performances, stand-up comedy, and food stalls from local restaurants. Open to all students and faculty.",
                    "banner_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&q=80&w=800",
                    "date": "2026-07-02",
                    "time": "18:00",
                    "venue": "Open Air Theater",
                    "organizer_id": "u-registrar",
                    "organizer_name": "Student Council",
                    "capacity": 500,
                    "registered_count": 342,
                    "created_at": "2026-06-12T10:00:00Z"
                }
            ],
            "event_registrations": [
                {"id": "er-1", "event_id": 1, "user_id": "u-jane-doe", "registered_at": "2026-06-12T09:00:00Z", "attended": False},
                {"id": "er-2", "event_id": 2, "user_id": "u-john-smith", "registered_at": "2026-06-12T09:30:00Z", "attended": False},
                {"id": "er-3", "event_id": 3, "user_id": "u-jane-doe", "registered_at": "2026-06-13T10:00:00Z", "attended": False},
                {"id": "er-4", "event_id": 3, "user_id": "u-john-smith", "registered_at": "2026-06-13T10:15:00Z", "attended": False}
            ],
            "announcements": [
                {
                    "id": "a-1",
                    "title": "Spring 2026 Final Exam Schedule",
                    "content": "The official schedule for Spring 2026 Final Exams has been uploaded to the university portal. Exams will commence on July 6th and conclude on July 20th. Please check your course list for exact dates and venues. Make sure your dues are cleared to download admit cards.",
                    "category": "Academic",
                    "priority": "High",
                    "author": "Dr. Arthur (Registrar Office)",
                    "created_at": "2026-06-12T08:30:00Z"
                },
                {
                    "id": "a-2",
                    "title": "HackCampus 2026 Registration Closing Soon",
                    "content": "Registration for HackCampus 2026 closes in 48 hours. Ensure your team of 2-4 members has registered on CampusConnect. High-value prizes including iPads, mechanical keyboards, and smart speakers are up for grabs. Don't miss out!",
                    "category": "Clubs",
                    "priority": "High",
                    "author": "Association of Computer Students",
                    "created_at": "2026-06-14T09:00:00Z"
                },
                {
                    "id": "a-3",
                    "title": "Campus Placement Drive: TechCorp Recruitment",
                    "content": "TechCorp is visiting campus next week on June 22nd for recruitment of Graduate Engineer Trainees. Eligible branches: CSE, IT, ECE. Minimum CGPA: 7.5. Submit your updated resumes in the Placement Cell by Friday 5 PM.",
                    "category": "Placements",
                    "priority": "High",
                    "author": "Placement Office",
                    "created_at": "2026-06-13T11:00:00Z"
                },
                {
                    "id": "a-4",
                    "title": "Hostel B Power Grid Maintenance",
                    "content": "Please note that Hostel Block B will experience a scheduled power outage on Wednesday, June 17th from 9 AM to 1 PM due to electrical grid maintenance and elevator servicing. We regret the inconvenience.",
                    "category": "Hostel",
                    "priority": "Medium",
                    "author": "Hostel Warden",
                    "created_at": "2026-06-14T10:15:00Z"
                },
                {
                    "id": "a-5",
                    "title": "Library Extended Hours for Exams",
                    "content": "Starting June 20th, the Central Library will remain open 24/7 until the end of final exams on July 20th. ID cards are mandatory for entry between 10 PM and 6 AM. Quiet study policies will be strictly enforced.",
                    "category": "General",
                    "priority": "Low",
                    "author": "Chief Librarian",
                    "created_at": "2026-06-14T14:30:00Z"
                }
            ],
            "saved_announcements": [
                {"id": "sa-1", "user_id": "u-jane-doe", "announcement_id": "a-1"},
                {"id": "sa-2", "user_id": "u-jane-doe", "announcement_id": "a-3"}
            ],
            "resources": [
                {
                    "id": "r-1",
                    "title": "Data Structures & Algorithms Exam Cheat Sheet",
                    "course_code": "CS-201",
                    "course_name": "Data Structures & Algorithms",
                    "category": "Notes",
                    "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "uploader_id": "u-jane-doe",
                    "uploader_name": "Jane Doe",
                    "bookmarks_count": 12,
                    "created_at": "2026-06-11T15:20:00Z"
                },
                {
                    "id": "r-2",
                    "title": "Intro to Algorithms PYQ (Spring 2025)",
                    "course_code": "CS-201",
                    "course_name": "Data Structures & Algorithms",
                    "category": "PYQs",
                    "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "uploader_id": "u-john-smith",
                    "uploader_name": "John Smith",
                    "bookmarks_count": 8,
                    "created_at": "2026-06-08T10:15:00Z"
                },
                {
                    "id": "r-3",
                    "title": "Linear Algebra Lecture 1-10 Slides",
                    "course_code": "MATH-102",
                    "course_name": "Linear Algebra",
                    "category": "PPTs",
                    "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "uploader_id": "u-jane-doe",
                    "uploader_name": "Jane Doe",
                    "bookmarks_count": 5,
                    "created_at": "2026-06-12T16:40:00Z"
                },
                {
                    "id": "r-4",
                    "title": "Web Development Bootcamp Lab Guide",
                    "course_code": "CS-302",
                    "course_name": "Web Technology",
                    "category": "Study guides",
                    "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                    "uploader_id": "u-club-acs",
                    "uploader_name": "ACS Club",
                    "bookmarks_count": 25,
                    "created_at": "2026-06-05T09:00:00Z"
                }
            ],
            "bookmarked_resources": [
                {"id": "br-1", "user_id": "u-jane-doe", "resource_id": "r-1"},
                {"id": "br-2", "user_id": "u-jane-doe", "resource_id": "r-4"},
                {"id": "br-3", "user_id": "u-john-smith", "resource_id": "r-1"}
            ],
            "peer_logistics": [
                {
                    "id": "pl-1",
                    "requester_id": "u-jane-doe",
                    "requester_name": "Jane Doe",
                    "helper_id": "u-john-smith",
                    "helper_name": "John Smith",
                    "title": "Library Book Return",
                    "description": "Return 'Introduction to Python' to the library desk. Book is on the desk at Hostel Block A, Room 204. I need it done before library closes at 8 PM.",
                    "pickup_location": "Hostel Block A, Room 204",
                    "delivery_location": "Central Library Counter",
                    "credits_offered": 5,
                    "status": "Delivered",
                    "created_at": "2026-06-12T11:00:00Z",
                    "updated_at": "2026-06-12T13:45:00Z"
                },
                {
                    "id": "pl-2",
                    "requester_id": "u-john-smith",
                    "requester_name": "John Smith",
                    "helper_id": None,
                    "helper_name": None,
                    "title": "Lab Manual Pickup",
                    "description": "Pick up my printed Chemistry Lab manual from the Xerox shop. It is already paid for under name John. Please drop it off in C hostel.",
                    "pickup_location": "Campus Xerox Shop",
                    "delivery_location": "Hostel Block C, Room 102",
                    "credits_offered": 5,
                    "status": "Requested",
                    "created_at": "2026-06-14T09:00:00Z",
                    "updated_at": "2026-06-14T09:00:00Z"
                },
                {
                    "id": "pl-3",
                    "requester_id": "u-jane-doe",
                    "requester_name": "Jane Doe",
                    "helper_id": "u-john-smith",
                    "helper_name": "John Smith",
                    "title": "Chemistry Notes Handover",
                    "description": "Hand over the organic chemistry lecture notes binder to me. John has it in C block.",
                    "pickup_location": "Hostel Block C Lobby",
                    "delivery_location": "Hostel Block A Room 204",
                    "credits_offered": 5,
                    "status": "Accepted",
                    "created_at": "2026-06-14T10:00:00Z",
                    "updated_at": "2026-06-14T10:30:00Z"
                }
            ],
            "lost_found": [
                {
                    "id": "lf-1",
                    "title": "Keys with Blue Keychain",
                    "description": "Found a set of 3 keys with a rubber blue rocket keychain on the round cafeteria table. Left them with the cafeteria cashier.",
                    "category": "Accessories",
                    "type": "Found",
                    "location": "Cafeteria",
                    "image_url": "https://images.unsplash.com/photo-1582139329536-e7284fece509?auto=format&fit=crop&q=80&w=400",
                    "reporter_id": "u-john-smith",
                    "reporter_name": "John Smith",
                    "status": "Open",
                    "created_at": "2026-06-13T14:00:00Z"
                },
                {
                    "id": "lf-2",
                    "title": "Black MacBook Air 13-inch",
                    "description": "Forgot my MacBook Air in Lab 3 (Block A) on the middle row. It has a sticker of Octocat on the lid. Please contact if found!",
                    "category": "Electronics",
                    "type": "Lost",
                    "location": "Lab 3, Block A",
                    "image_url": None,
                    "reporter_id": "u-jane-doe",
                    "reporter_name": "Jane Doe",
                    "status": "Open",
                    "created_at": "2026-06-14T12:00:00Z"
                }
            ],
            "credit_transactions": [
                {"id": "ct-1", "user_id": "u-jane-doe", "amount": -5, "description": "Requested logistics 'Library Book Return'", "created_at": "2026-06-12T11:00:00Z"},
                {"id": "ct-2", "user_id": "u-john-smith", "amount": 5, "description": "Completed logistics delivery 'Library Book Return'", "created_at": "2026-06-12T13:45:00Z"}
            ],
            "notifications": [
                {
                    "id": "n-1",
                    "user_id": "u-jane-doe",
                    "title": "Welcome to CampusConnect",
                    "content": "Welcome to CampusConnect! Start exploring events, checking announcements, and sharing resources.",
                    "read": False,
                    "created_at": "2026-06-14T08:00:00Z"
                },
                {
                    "id": "n-2",
                    "user_id": "u-john-smith",
                    "title": "Delivery Completed",
                    "content": "Your logistics delivery for 'Library Book Return' has been marked as delivered. +5 credits earned!",
                    "read": True,
                    "created_at": "2026-06-12T13:45:00Z"
                },
                {
                    "id": "n-3",
                    "user_id": "u-jane-doe",
                    "title": "Logistics Accepted",
                    "content": "John Smith accepted your request 'Chemistry Notes Handover'. Check dashboard for details.",
                    "read": False,
                    "created_at": "2026-06-14T10:30:00Z"
                }
            ]
        }


# Initialize local DB object
mock_db = CampusMockDatabase()


# --- DATABASE INTERFACE FUNCTIONS ---

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("users").select("*").eq("email", email).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
    
    # Fallback to local DB
    for user in mock_db.data["users"]:
        if user["email"].lower() == email.lower():
            return user
    return None

def register_user(email: str, name: str, role: str = "student") -> Dict[str, Any]:
    new_user_id = f"u-{uuid.uuid4().hex[:8]}"
    avatar = f"https://api.dicebear.com/7.x/adventurer/svg?seed={name.replace(' ', '')}"
    created_at = datetime.datetime.now().isoformat()
    
    user_data = {
        "id": new_user_id,
        "email": email.lower(),
        "name": name,
        "credits": 50,
        "avatar_url": avatar,
        "role": role,
        "created_at": created_at
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("users").insert(user_data).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Local DB fallback
    mock_db.data["users"].append(user_data)
    
    # Also add a welcome notification
    add_notification(
        user_id=new_user_id,
        title="Welcome to CampusConnect",
        content=f"Hey {name}! Start exploring events, checking announcements, and sharing resources."
    )
    
    mock_db.save()
    return user_data

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("users").select("*").eq("id", user_id).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
    
    # Fallback to local DB
    for user in mock_db.data["users"]:
        if user["id"] == user_id:
            return user
    return None

def update_user_credits(user_id: str, new_credits: int) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("users").update({"credits": new_credits}).eq("id", user_id).execute()
            if res.data:
                return True
        except Exception as e:
            print(f"Supabase error: {e}")
    
    # Fallback to local DB
    for user in mock_db.data["users"]:
        if user["id"] == user_id:
            user["credits"] = new_credits
            mock_db.save()
            return True
    return False

# --- Events Hub ---

def get_events() -> List[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("events").select("*").order("date", desc=False).execute()
            return res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    return sorted(mock_db.data["events"], key=lambda x: x["date"])

def create_event(title: str, description: str, date: str, time: str, venue: str, banner_url: str, organizer_id: str, organizer_name: str, capacity: int) -> Dict[str, Any]:
    event_data = {
        "title": title,
        "description": description,
        "date": date,
        "time": time,
        "venue": venue,
        "banner_url": banner_url or "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?auto=format&fit=crop&q=80&w=800",
        "organizer_id": organizer_id,
        "organizer_name": organizer_name,
        "capacity": capacity,
        "registered_count": 0,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("events").insert(event_data).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    new_id = len(mock_db.data["events"]) + 1
    event_data["id"] = new_id
    mock_db.data["events"].append(event_data)
    mock_db.save()
    return event_data

def register_for_event(event_id: int, user_id: str) -> bool:
    # Check if already registered
    if is_user_registered_for_event(event_id, user_id):
        return False
        
    reg_id = f"er-{uuid.uuid4().hex[:8]}"
    reg_data = {
        "id": reg_id,
        "event_id": event_id,
        "user_id": user_id,
        "registered_at": datetime.datetime.now().isoformat(),
        "attended": False
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("event_registrations").insert(reg_data).execute()
            if res.data:
                # Increment count
                events = supabase_client.table("events").select("registered_count").eq("id", event_id).execute()
                if events.data:
                    current_count = events.data[0]["registered_count"] or 0
                    supabase_client.table("events").update({"registered_count": current_count + 1}).eq("id", event_id).execute()
                return True
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    mock_db.data["event_registrations"].append(reg_data)
    for event in mock_db.data["events"]:
        if event["id"] == event_id:
            event["registered_count"] = event.get("registered_count", 0) + 1
            # Add notification
            add_notification(
                user_id=user_id,
                title="Event Registration Successful",
                content=f"You've successfully registered for '{event['title']}'."
            )
            break
    mock_db.save()
    return True

def unregister_from_event(event_id: int, user_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("event_registrations").delete().eq("event_id", event_id).eq("user_id", user_id).execute()
            if res.data:
                events = supabase_client.table("events").select("registered_count").eq("id", event_id).execute()
                if events.data:
                    current_count = events.data[0]["registered_count"] or 0
                    supabase_client.table("events").update({"registered_count": max(0, current_count - 1)}).eq("id", event_id).execute()
                return True
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    registrations = mock_db.data["event_registrations"]
    initial_len = len(registrations)
    mock_db.data["event_registrations"] = [r for r in registrations if not (r["event_id"] == event_id and r["user_id"] == user_id)]
    
    if len(mock_db.data["event_registrations"]) < initial_len:
        for event in mock_db.data["events"]:
            if event["id"] == event_id:
                event["registered_count"] = max(0, event.get("registered_count", 0) - 1)
                break
        mock_db.save()
        return True
    return False

def is_user_registered_for_event(event_id: int, user_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("event_registrations").select("*").eq("event_id", event_id).eq("user_id", user_id).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for r in mock_db.data["event_registrations"]:
        if r["event_id"] == event_id and r["user_id"] == user_id:
            return True
    return False

def get_user_registered_events(user_id: str) -> List[Dict[str, Any]]:
    event_ids = []
    if USE_SUPABASE:
        try:
            res = supabase_client.table("event_registrations").select("event_id").eq("user_id", user_id).execute()
            event_ids = [item["event_id"] for item in res.data]
            if not event_ids:
                return []
            events_res = supabase_client.table("events").select("*").in_("id", event_ids).execute()
            return events_res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for r in mock_db.data["event_registrations"]:
        if r["user_id"] == user_id:
            event_ids.append(r["event_id"])
    return [e for e in mock_db.data["events"] if e["id"] in event_ids]


# --- Announcements Center ---

def get_announcements() -> List[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("announcements").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    return sorted(mock_db.data["announcements"], key=lambda x: x["created_at"], reverse=True)

def create_announcement(title: str, content: str, category: str, priority: str, author: str) -> Dict[str, Any]:
    ann_data = {
        "title": title,
        "content": content,
        "category": category,
        "priority": priority,
        "author": author,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("announcements").insert(ann_data).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    new_id = f"a-{uuid.uuid4().hex[:8]}"
    ann_data["id"] = new_id
    mock_db.data["announcements"].append(ann_data)
    
    # Broadcast notice to all students via notifications
    for user in mock_db.data["users"]:
        add_notification(
            user_id=user["id"],
            title=f"New Announcement: {title}",
            content=f"Priority: {priority}. Read details in the Announcement Center."
        )
        
    mock_db.save()
    return ann_data

def save_announcement(user_id: str, announcement_id: str) -> bool:
    if is_announcement_saved(user_id, announcement_id):
        return False
        
    save_data = {
        "id": f"sa-{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "announcement_id": announcement_id
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("saved_announcements").insert(save_data).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    mock_db.data["saved_announcements"].append(save_data)
    mock_db.save()
    return True

def unsave_announcement(user_id: str, announcement_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("saved_announcements").delete().eq("user_id", user_id).eq("announcement_id", announcement_id).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    saved = mock_db.data["saved_announcements"]
    initial_len = len(saved)
    mock_db.data["saved_announcements"] = [s for s in saved if not (s["user_id"] == user_id and s["announcement_id"] == announcement_id)]
    if len(mock_db.data["saved_announcements"]) < initial_len:
        mock_db.save()
        return True
    return False

def is_announcement_saved(user_id: str, announcement_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("saved_announcements").select("*").eq("user_id", user_id).eq("announcement_id", announcement_id).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for s in mock_db.data["saved_announcements"]:
        if s["user_id"] == user_id and s["announcement_id"] == announcement_id:
            return True
    return False

def get_saved_announcements(user_id: str) -> List[Dict[str, Any]]:
    ann_ids = []
    if USE_SUPABASE:
        try:
            res = supabase_client.table("saved_announcements").select("announcement_id").eq("user_id", user_id).execute()
            ann_ids = [item["announcement_id"] for item in res.data]
            if not ann_ids:
                return []
            ann_res = supabase_client.table("announcements").select("*").in_("id", ann_ids).execute()
            return ann_res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for s in mock_db.data["saved_announcements"]:
        if s["user_id"] == user_id:
            ann_ids.append(s["announcement_id"])
    return [a for a in mock_db.data["announcements"] if a["id"] in ann_ids]


# --- Resource Hub ---

def get_resources() -> List[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("resources").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    return sorted(mock_db.data["resources"], key=lambda x: x["created_at"], reverse=True)

def upload_resource(title: str, course_code: str, course_name: str, category: str, file_url: str, uploader_id: str, uploader_name: str) -> Dict[str, Any]:
    res_data = {
        "title": title,
        "course_code": course_code.upper(),
        "course_name": course_name,
        "category": category,
        "file_url": file_url,
        "uploader_id": uploader_id,
        "uploader_name": uploader_name,
        "bookmarks_count": 0,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("resources").insert(res_data).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    new_id = f"r-{uuid.uuid4().hex[:8]}"
    res_data["id"] = new_id
    mock_db.data["resources"].append(res_data)
    mock_db.save()
    return res_data

def bookmark_resource(user_id: str, resource_id: str) -> bool:
    if is_resource_bookmarked(user_id, resource_id):
        return False
        
    bm_data = {
        "id": f"br-{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "resource_id": resource_id
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("bookmarked_resources").insert(bm_data).execute()
            if res.data:
                # Increment count
                res_obj = supabase_client.table("resources").select("bookmarks_count").eq("id", resource_id).execute()
                if res_obj.data:
                    current = res_obj.data[0]["bookmarks_count"] or 0
                    supabase_client.table("resources").update({"bookmarks_count": current + 1}).eq("id", resource_id).execute()
                return True
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    mock_db.data["bookmarked_resources"].append(bm_data)
    for r in mock_db.data["resources"]:
        if r["id"] == resource_id:
            r["bookmarks_count"] = r.get("bookmarks_count", 0) + 1
            break
    mock_db.save()
    return True

def unbookmark_resource(user_id: str, resource_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("bookmarked_resources").delete().eq("user_id", user_id).eq("resource_id", resource_id).execute()
            if res.data:
                res_obj = supabase_client.table("resources").select("bookmarks_count").eq("id", resource_id).execute()
                if res_obj.data:
                    current = res_obj.data[0]["bookmarks_count"] or 0
                    supabase_client.table("resources").update({"bookmarks_count": max(0, current - 1)}).eq("id", resource_id).execute()
                return True
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    bms = mock_db.data["bookmarked_resources"]
    initial_len = len(bms)
    mock_db.data["bookmarked_resources"] = [b for b in bms if not (b["user_id"] == user_id and b["resource_id"] == resource_id)]
    if len(mock_db.data["bookmarked_resources"]) < initial_len:
        for r in mock_db.data["resources"]:
            if r["id"] == resource_id:
                r["bookmarks_count"] = max(0, r.get("bookmarks_count", 0) - 1)
                break
        mock_db.save()
        return True
    return False

def is_resource_bookmarked(user_id: str, resource_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("bookmarked_resources").select("*").eq("user_id", user_id).eq("resource_id", resource_id).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for b in mock_db.data["bookmarked_resources"]:
        if b["user_id"] == user_id and b["resource_id"] == resource_id:
            return True
    return False

def get_bookmarked_resources(user_id: str) -> List[Dict[str, Any]]:
    res_ids = []
    if USE_SUPABASE:
        try:
            res = supabase_client.table("bookmarked_resources").select("resource_id").eq("user_id", user_id).execute()
            res_ids = [item["resource_id"] for item in res.data]
            if not res_ids:
                return []
            resources_res = supabase_client.table("resources").select("*").in_("id", res_ids).execute()
            return resources_res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for b in mock_db.data["bookmarked_resources"]:
        if b["user_id"] == user_id:
            res_ids.append(b["resource_id"])
    return [r for r in mock_db.data["resources"] if r["id"] in res_ids]


# --- Peer Logistics ---

def get_logistics_requests() -> List[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("peer_logistics").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    return sorted(mock_db.data["peer_logistics"], key=lambda x: x["created_at"], reverse=True)

def create_logistics_request(requester_id: str, requester_name: str, title: str, description: str, pickup_location: str, delivery_location: str, credits_offered: int = 5) -> Optional[Dict[str, Any]]:
    # Check if user has enough credits
    user = get_user_by_id(requester_id)
    if not user or user["credits"] < credits_offered:
        return None
        
    req_data = {
        "requester_id": requester_id,
        "requester_name": requester_name,
        "helper_id": None,
        "helper_name": None,
        "title": title,
        "description": description,
        "pickup_location": pickup_location,
        "delivery_location": delivery_location,
        "credits_offered": credits_offered,
        "status": "Requested",
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    # Deduct credits
    new_credits = user["credits"] - credits_offered
    
    if USE_SUPABASE:
        try:
            # Update credits
            supabase_client.table("users").update({"credits": new_credits}).eq("id", requester_id).execute()
            # Insert request
            res = supabase_client.table("peer_logistics").insert(req_data).execute()
            if res.data:
                # Log transaction
                supabase_client.table("credit_transactions").insert({
                    "user_id": requester_id,
                    "amount": -credits_offered,
                    "description": f"Created delivery request '{title}'"
                }).execute()
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    new_id = f"pl-{uuid.uuid4().hex[:8]}"
    req_data["id"] = new_id
    mock_db.data["peer_logistics"].append(req_data)
    
    # Deduct credits locally
    for u in mock_db.data["users"]:
        if u["id"] == requester_id:
            u["credits"] = new_credits
            break
            
    # Log transaction locally
    mock_db.data["credit_transactions"].append({
        "id": f"ct-{uuid.uuid4().hex[:8]}",
        "user_id": requester_id,
        "amount": -credits_offered,
        "description": f"Created delivery request '{title}'",
        "created_at": datetime.datetime.now().isoformat()
    })
    
    # Add confirmation notification
    add_notification(
        user_id=requester_id,
        title="Delivery Request Created",
        content=f"Requested '{title}'. {credits_offered} credits held."
    )
    
    mock_db.save()
    return req_data

def accept_logistics_request(request_id: str, helper_id: str, helper_name: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("peer_logistics").update({
                "helper_id": helper_id,
                "helper_name": helper_name,
                "status": "Accepted",
                "updated_at": datetime.datetime.now().isoformat()
            }).eq("id", request_id).execute()
            if res.data:
                # Notify requester
                add_notification(
                    user_id=res.data[0]["requester_id"],
                    title="Logistics Request Accepted",
                    content=f"{helper_name} accepted your delivery request '{res.data[0]['title']}'."
                )
                return True
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for req in mock_db.data["peer_logistics"]:
        if req["id"] == request_id:
            if req["status"] != "Requested":
                return False  # Already accepted
            req["helper_id"] = helper_id
            req["helper_name"] = helper_name
            req["status"] = "Accepted"
            req["updated_at"] = datetime.datetime.now().isoformat()
            
            # Notify requester
            add_notification(
                user_id=req["requester_id"],
                title="Logistics Request Accepted",
                content=f"{helper_name} has accepted your request '{req['title']}'."
            )
            mock_db.save()
            return True
    return False

def update_logistics_status(request_id: str, status: str) -> bool:
    # Status can be 'Picked Up' or 'Delivered'
    if USE_SUPABASE:
        try:
            req_check = supabase_client.table("peer_logistics").select("*").eq("id", request_id).execute()
            if not req_check.data:
                return False
            req = req_check.data[0]
            
            res = supabase_client.table("peer_logistics").update({
                "status": status,
                "updated_at": datetime.datetime.now().isoformat()
            }).eq("id", request_id).execute()
            
            if res.data:
                # Notify requester
                add_notification(
                    user_id=req["requester_id"],
                    title=f"Logistics Status: {status}",
                    content=f"Your delivery request '{req['title']}' is now {status.lower()}."
                )
                
                # If delivered, credit the helper
                if status == "Delivered" and req["helper_id"]:
                    helper = get_user_by_id(req["helper_id"])
                    if helper:
                        new_helper_credits = helper["credits"] + req["credits_offered"]
                        supabase_client.table("users").update({"credits": new_helper_credits}).eq("id", req["helper_id"]).execute()
                        # Log transaction
                        supabase_client.table("credit_transactions").insert({
                            "user_id": req["helper_id"],
                            "amount": req["credits_offered"],
                            "description": f"Completed delivery for '{req['title']}'"
                        }).execute()
                        # Notify helper
                        add_notification(
                            user_id=req["helper_id"],
                            title="Credits Rewarded",
                            content=f"Earned +{req['credits_offered']} credits for delivering '{req['title']}'."
                        )
                return True
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for req in mock_db.data["peer_logistics"]:
        if req["id"] == request_id:
            req["status"] = status
            req["updated_at"] = datetime.datetime.now().isoformat()
            
            # Notify requester
            add_notification(
                user_id=req["requester_id"],
                title=f"Logistics Status: {status}",
                content=f"Your delivery request '{req['title']}' is now {status.lower()}."
            )
            
            # Credit the helper if delivered
            if status == "Delivered" and req["helper_id"]:
                for u in mock_db.data["users"]:
                    if u["id"] == req["helper_id"]:
                        u["credits"] = u.get("credits", 0) + req["credits_offered"]
                        break
                mock_db.data["credit_transactions"].append({
                    "id": f"ct-{uuid.uuid4().hex[:8]}",
                    "user_id": req["helper_id"],
                    "amount": req["credits_offered"],
                    "description": f"Completed delivery for '{req['title']}'",
                    "created_at": datetime.datetime.now().isoformat()
                })
                # Notify helper
                add_notification(
                    user_id=req["helper_id"],
                    title="Credits Earned!",
                    content=f"Earned +{req['credits_offered']} credits for delivering '{req['title']}'."
                )
            mock_db.save()
            return True
    return False

def get_credit_transactions(user_id: str) -> List[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("credit_transactions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    return sorted([t for t in mock_db.data["credit_transactions"] if t["user_id"] == user_id], key=lambda x: x["created_at"], reverse=True)


# --- Lost & Found ---

def get_lost_found_items() -> List[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("lost_found").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    return sorted(mock_db.data["lost_found"], key=lambda x: x["created_at"], reverse=True)

def report_lost_found_item(title: str, description: str, category: str, item_type: str, location: str, image_url: str, reporter_id: str, reporter_name: str) -> Dict[str, Any]:
    item_data = {
        "title": title,
        "description": description,
        "category": category,
        "type": item_type, # 'Lost' or 'Found'
        "location": location,
        "image_url": image_url or None,
        "reporter_id": reporter_id,
        "reporter_name": reporter_name,
        "status": "Open",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("lost_found").insert(item_data).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    new_id = f"lf-{uuid.uuid4().hex[:8]}"
    item_data["id"] = new_id
    mock_db.data["lost_found"].append(item_data)
    mock_db.save()
    return item_data

def update_lost_found_status(item_id: str, status: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("lost_found").update({"status": status}).eq("id", item_id).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for item in mock_db.data["lost_found"]:
        if item["id"] == item_id:
            item["status"] = status
            mock_db.save()
            return True
    return False


# --- Notifications ---

def get_notifications(user_id: str) -> List[Dict[str, Any]]:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    return sorted([n for n in mock_db.data["notifications"] if n["user_id"] == user_id], key=lambda x: x["created_at"], reverse=True)

def add_notification(user_id: str, title: str, content: str) -> Dict[str, Any]:
    notif_data = {
        "user_id": user_id,
        "title": title,
        "content": content,
        "read": False,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    if USE_SUPABASE:
        try:
            res = supabase_client.table("notifications").insert(notif_data).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    new_id = f"n-{uuid.uuid4().hex[:8]}"
    notif_data["id"] = new_id
    mock_db.data["notifications"].append(notif_data)
    # mock_db.save() is called by the parent operation
    return notif_data

def mark_notification_as_read(notif_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("notifications").update({"read": True}).eq("id", notif_id).execute()
            return len(res.data) > 0
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    for n in mock_db.data["notifications"]:
        if n["id"] == notif_id:
            n["read"] = True
            mock_db.save()
            return True
    return False

def clear_all_notifications(user_id: str) -> bool:
    if USE_SUPABASE:
        try:
            res = supabase_client.table("notifications").delete().eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Supabase error: {e}")
            
    # Fallback to local DB
    mock_db.data["notifications"] = [n for n in mock_db.data["notifications"] if n["user_id"] != user_id]
    mock_db.save()
    return True
