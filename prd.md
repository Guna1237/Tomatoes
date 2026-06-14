# CampusConnect - Product Requirements Document (PRD)

## Vision

CampusConnect is a centralized student platform that brings together campus communication, events, resources, announcements, and peer logistics into a single system.

Students currently rely on fragmented channels such as Outlook emails, WhatsApp groups, Euclid, Microsoft folders, and informal networks. This causes missed deadlines, lost opportunities, poor event participation, difficulty finding resources, and unnecessary travel across campus.

CampusConnect serves as the single source of truth for student life.

---

# Problem Statement

Students rely on multiple disconnected platforms such as emails, messaging groups, learning portals, and informal networks to access academic resources, campus announcements, event information, and everyday services.

This fragmentation leads to missed deadlines, reduced participation in campus activities, difficulty accessing resources, and inefficiencies in daily campus life.

Additionally, students often make unnecessary trips across campus for tasks such as collecting parcels, exchanging notes, retrieving forgotten items, or accessing services.

A centralized platform is needed to streamline communication, student engagement, resource sharing, and campus logistics.

---

# Target Users

## Students

* Access events
* Register for activities
* Receive announcements
* Share resources
* Request deliveries

## Clubs

* Publish events
* Manage registrations
* Send announcements

## University Administration

* Broadcast notices
* Manage orientation
* Share official updates

---

# Core Modules

## 1. Smart Dashboard

Single homepage containing:

* Upcoming events
* Registered events
* Important announcements
* Recent resources
* Active parcel requests
* Notification center

Purpose:
Eliminate the need to check multiple platforms.

---

## 2. Events Hub

Features:

* Event creation
* Event registration
* Attendance tracking
* Event reminders
* Event calendar
* Club pages

Event Card:

* Banner image
* Event title
* Date
* Time
* Venue
* Organizer
* Register button

---

## 3. Announcement Center

Categories:

* Academic
* Clubs
* Placements
* Hostel
* General

Features:

* Priority tagging
* Filters
* Search
* Save announcement

---

## 4. Resource Hub

Students can upload:

* Notes
* PYQs
* PPTs
* PDFs
* Study guides

Features:

* Course tagging
* Search
* Download
* Bookmark

---

## 5. Peer Logistics

Credit-based model.

Students:

* Request parcel pickup
* Request note delivery
* Request item transfer

Process:

Request Created
→ Accepted
→ Picked Up
→ Delivered

Credits earned:
+5 per completed delivery

Credits spent:
-5 per request

No money involved.

---

## 6. Lost & Found

Features:

* Upload item image
* Report lost item
* Claim item

Categories:

* Electronics
* IDs
* Books
* Accessories

---

# User Flow

Login
→ Dashboard
→ Select Module
→ Complete Action
→ Receive Notifications

---

# Success Metrics

* Event registrations
* Active users
* Resources uploaded
* Announcements viewed
* Parcels delivered
* Time saved

---

# MVP Scope

Must Have:

✓ Login
✓ Dashboard
✓ Events
✓ Registrations
✓ Announcements
✓ Resources
✓ Parcel Delivery

Optional:

* Lost & Found
* AI Assistant
* Smart Recommendations

---

# Tech Stack

Frontend:
Streamlit

Backend:
Python

Database:
Supabase PostgreSQL

Authentication:
Supabase Auth

Storage:
Supabase Storage

Notifications:
Email + In-App

Deployment:
Streamlit Cloud
