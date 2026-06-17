# CampusConnect - Centralized Student Platform

CampusConnect is a premium, dark-themed SaaS-style platform designed to unify university communications, events, study resources, announcements, and peer logistics into a single hub. 

Inspired by modern interfaces like Stripe, Linear, Notion, and Discord, it completely hides standard Streamlit branding, offering a bespoke web application experience powered by custom HTML, CSS, and JavaScript.

---

## ✨ Features

1. **Smart Dashboard**: Personalized greetings based on local time, KPI metric cards, active parcel tracking timelines, upcoming registered events, and a quick-alerts feed.
2. **Events Hub**: Clean event search, monthly calendar visual grids, registration toggles, and club organizing tools to host/post new events.
3. **Announcements Center**: Broadcast notices filtered by categories (Academic, Hostel, Placements, General) and priority tags (High, Medium, Low) with bookmarking options.
4. **Resource Hub**: Course-specific study guides, past exams (PYQs), notes, and presentations with support for direct uploads, bookmarked shortcuts, and download capabilities.
5. **Peer Logistics (Credit-Based)**: A gamified, cashless campus parcel/notes delivery system. Creating a request holds 5 credits, and completing the delivery transfers those 5 credits to the helper student.
6. **Lost & Found**: Item reports with local image upload references, categorizations, and automated claim notifications dispatched to owners.
7. **Profile & Notification Logs**: Activity counters (completed deliveries, registrations, files shared), notification logs, and a profile switcher.

---

## 🛠️ Technology Stack

- **Frontend/Backend**: Python & Streamlit (Version-agnostic wrapper)
- **Styling**: Vanilla HTML5, CSS3, Google Fonts (Inter), and Lucide Icons (CDN)
- **Database**: Supabase PostgreSQL / Local JSON storage fallback
- **Authentication**: Supabase Auth / Local email validation

---

## ⚙️ How to Configure & Run

### Prerequisites
Make sure you have Python installed, then install the required dependencies:
```bash
pip install streamlit supabase
```

### Running the App
Start the Streamlit application from the project root directory:
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 📂 Database Configuration (Dual-Mode)

CampusConnect is designed to work out of the box without any setup. 

- **Local Mock Mode (Default)**: If no database credentials are found, the app automatically runs in Mock Mode, serializing data to a local `campus_db.json` file. The app starts preloaded with rich mock data.
- **Production Supabase Mode**: To connect to a live Supabase instance, create a `.streamlit/secrets.toml` file or set environment variables:
  ```toml
  SUPABASE_URL = "your-supabase-url"
  SUPABASE_KEY = "your-supabase-anon-key"
  ```
  Run the SQL queries in [schema.sql](file:///c:/Users/notgu/OneDrive/Documents/campus/schema.sql) inside your Supabase SQL editor to create all tables.

### OpenAI Configuration
The Resource Hub includes an optional AI Study Planner. Add an OpenAI API key to `.streamlit/secrets.toml` or your environment:
```toml
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_MODEL = "gpt-4.1-mini" # optional
```
If no key is configured, the app still runs normally and shows setup guidance in the AI tab.

---

## 👥 Demo Profiles for Evaluation

For easy testing and presentation, the login screen includes a **Demo Profile Switcher**:

1. **Jane Doe (Student)**:
   - Email: `jane@university.edu`
   - Permissions: Discover events, claim lost items, bookmark resources, request parcel delivery, earn credits.
2. **ACS Club (Club Admin)**:
   - Email: `acs@university.edu`
   - Permissions: Host and create events, publish club announcements, share resources.
3. **Dr. Arthur (Admin)**:
   - Email: `registrar@university.edu`
   - Permissions: Broadcast official high-priority announcements, manage admin configurations, switch test roles.
