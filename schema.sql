-- CampusConnect - Supabase PostgreSQL Database Schema Reference

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    tomatoes INT NOT NULL DEFAULT 50,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'student', -- 'student', 'club_admin', 'admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create Events Table
CREATE TABLE IF NOT EXISTS public.events (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    banner_url TEXT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    venue TEXT NOT NULL,
    organizer_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    organizer_name TEXT NOT NULL,
    capacity INT DEFAULT 100,
    registered_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Create Event Registrations Table
CREATE TABLE IF NOT EXISTS public.event_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id INT REFERENCES public.events(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    attended BOOLEAN DEFAULT FALSE,
    UNIQUE(event_id, user_id)
);

-- 4. Create Announcements Table
CREATE TABLE IF NOT EXISTS public.announcements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL, -- 'Academic', 'Clubs', 'Placements', 'Hostel', 'General'
    priority TEXT NOT NULL, -- 'High', 'Medium', 'Low'
    author TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Create Saved Announcements Table
CREATE TABLE IF NOT EXISTS public.saved_announcements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    announcement_id UUID REFERENCES public.announcements(id) ON DELETE CASCADE,
    UNIQUE(user_id, announcement_id)
);

-- 6. Create Resources Table
CREATE TABLE IF NOT EXISTS public.resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    category TEXT NOT NULL, -- 'Notes', 'PYQs', 'PPTs', 'PDFs', 'Study guides'
    file_url TEXT NOT NULL,
    uploader_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    uploader_name TEXT NOT NULL,
    bookmarks_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. Create Bookmarked Resources Table
CREATE TABLE IF NOT EXISTS public.bookmarked_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES public.resources(id) ON DELETE CASCADE,
    UNIQUE(user_id, resource_id)
);

-- 8. Create Peer Logistics Table
CREATE TABLE IF NOT EXISTS public.peer_logistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    requester_name TEXT NOT NULL,
    helper_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    helper_name TEXT,
    title TEXT NOT NULL,
    description TEXT,
    pickup_location TEXT NOT NULL,
    delivery_location TEXT NOT NULL,
    tomatoes_offered INT DEFAULT 5,
    status TEXT NOT NULL DEFAULT 'Request Created', -- 'Request Created', 'Matched', 'Picked Up', 'Delivered'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 9. Create Lost & Found Table
CREATE TABLE IF NOT EXISTS public.lost_found (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL, -- 'Electronics', 'IDs', 'Books', 'Accessories', 'Other'
    type TEXT NOT NULL, -- 'Lost', 'Found'
    location TEXT NOT NULL,
    image_url TEXT,
    reporter_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    reporter_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open', -- 'Open', 'Claimed', 'Resolved'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 10. Create Tomato Transactions Table
CREATE TABLE IF NOT EXISTS public.tomato_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    amount INT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 11. Create Notifications Table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
