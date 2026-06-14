-- =============================================================================
-- CampusConnect – Supabase Postgres Schema
-- Run this in the Supabase SQL editor (Dashboard → SQL Editor → New Query).
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLES
-- =============================================================================

-- Users table (profile, extends auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'club_admin', 'admin')),
    tomato_balance INTEGER NOT NULL DEFAULT 50,
    avatar_url TEXT,
    bio TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Events
CREATE TABLE IF NOT EXISTS public.events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    banner_url TEXT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    venue TEXT NOT NULL,
    organizer_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    organizer_name TEXT NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 100 CHECK (capacity > 0),
    registered_count INTEGER NOT NULL DEFAULT 0 CHECK (registered_count >= 0),
    category TEXT DEFAULT 'General',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Event registrations
CREATE TABLE IF NOT EXISTS public.event_registrations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    attended BOOLEAN DEFAULT FALSE,
    UNIQUE(event_id, user_id)
);

-- Announcements
CREATE TABLE IF NOT EXISTS public.announcements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'General' CHECK (category IN ('Academic', 'Hostel', 'Placements', 'Clubs', 'General')),
    priority TEXT NOT NULL DEFAULT 'Normal' CHECK (priority IN ('Critical', 'Important', 'Normal')),
    author_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    author_name TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Saved announcements
CREATE TABLE IF NOT EXISTS public.saved_announcements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    announcement_id UUID NOT NULL REFERENCES public.announcements(id) ON DELETE CASCADE,
    saved_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, announcement_id)
);

-- Resources
CREATE TABLE IF NOT EXISTS public.resources (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    course_code TEXT,
    course_name TEXT,
    category TEXT NOT NULL DEFAULT 'Notes' CHECK (category IN ('Notes', 'PYQs', 'PPTs', 'Study guides', 'Lab Manuals')),
    file_url TEXT NOT NULL,
    file_name TEXT,
    file_size INTEGER,
    file_type TEXT,
    uploader_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    uploader_name TEXT,
    bookmarks_count INTEGER NOT NULL DEFAULT 0,
    downloads_count INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bookmarked resources
CREATE TABLE IF NOT EXISTS public.bookmarked_resources (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    resource_id UUID NOT NULL REFERENCES public.resources(id) ON DELETE CASCADE,
    bookmarked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, resource_id)
);

-- Parcel requests
CREATE TABLE IF NOT EXISTS public.parcel_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    requester_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    requester_name TEXT NOT NULL,
    helper_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    helper_name TEXT,
    title TEXT NOT NULL,
    description TEXT,
    pickup_location TEXT NOT NULL,
    delivery_location TEXT NOT NULL,
    tomatoes_offered INTEGER NOT NULL DEFAULT 5 CHECK (tomatoes_offered > 0),
    status TEXT NOT NULL DEFAULT 'Created' CHECK (status IN ('Created', 'Accepted', 'Picked Up', 'Delivered', 'Cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tomato transactions
CREATE TABLE IF NOT EXISTS public.tomato_transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL DEFAULT 'general' CHECK (transaction_type IN ('delivery_reward', 'delivery_spend', 'bonus', 'admin_grant', 'general')),
    description TEXT,
    related_request_id UUID REFERENCES public.parcel_requests(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Lost and found
CREATE TABLE IF NOT EXISTS public.lost_found (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    item_type TEXT NOT NULL CHECK (item_type IN ('Lost', 'Found')),
    location TEXT NOT NULL,
    image_url TEXT,
    reporter_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    reporter_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Claimed', 'Resolved')),
    claimed_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT,
    notification_type TEXT NOT NULL DEFAULT 'general' CHECK (notification_type IN ('event', 'parcel', 'resource', 'announcement', 'lost_found', 'general')),
    read BOOLEAN NOT NULL DEFAULT FALSE,
    related_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit logs
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_events_date ON public.events(date);
CREATE INDEX IF NOT EXISTS idx_events_organizer ON public.events(organizer_id);
CREATE INDEX IF NOT EXISTS idx_event_reg_event ON public.event_registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_event_reg_user ON public.event_registrations(user_id);
CREATE INDEX IF NOT EXISTS idx_announcements_created ON public.announcements(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_announcements_priority ON public.announcements(priority);
CREATE INDEX IF NOT EXISTS idx_resources_created ON public.resources(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_resources_course ON public.resources(course_code);
CREATE INDEX IF NOT EXISTS idx_parcel_status ON public.parcel_requests(status);
CREATE INDEX IF NOT EXISTS idx_parcel_requester ON public.parcel_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_parcel_helper ON public.parcel_requests(helper_id);
CREATE INDEX IF NOT EXISTS idx_tomato_user ON public.tomato_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_lost_found_type ON public.lost_found(item_type);
CREATE INDEX IF NOT EXISTS idx_lost_found_status ON public.lost_found(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON public.notifications(user_id, read);
CREATE INDEX IF NOT EXISTS idx_audit_user ON public.audit_logs(user_id);

-- =============================================================================
-- ROW-LEVEL SECURITY
-- =============================================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.event_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookmarked_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.parcel_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tomato_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lost_found ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- RLS POLICIES
-- =============================================================================

-- Users: anyone authenticated can read profiles; only owner can insert/update
CREATE POLICY "users_select_all" ON public.users
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "users_insert_own" ON public.users
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = id);
CREATE POLICY "users_update_own" ON public.users
    FOR UPDATE TO authenticated USING (auth.uid() = id);

-- Events: all authenticated read active; club_admin/admin insert; owner/admin update/delete
CREATE POLICY "events_select_active" ON public.events
    FOR SELECT TO authenticated USING (is_active = true);
CREATE POLICY "events_insert_admin" ON public.events
    FOR INSERT TO authenticated
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.users WHERE id = auth.uid() AND role IN ('club_admin', 'admin')
    ));
CREATE POLICY "events_update_owner" ON public.events
    FOR UPDATE TO authenticated
    USING (
        organizer_id = auth.uid()
        OR EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
    );
CREATE POLICY "events_delete_owner" ON public.events
    FOR DELETE TO authenticated
    USING (
        organizer_id = auth.uid()
        OR EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
    );

-- Event registrations: all can read; users manage own registrations
CREATE POLICY "event_reg_select" ON public.event_registrations
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "event_reg_insert" ON public.event_registrations
    FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
CREATE POLICY "event_reg_delete" ON public.event_registrations
    FOR DELETE TO authenticated USING (user_id = auth.uid());

-- Announcements: all read active; club_admin/admin insert/update/delete
CREATE POLICY "ann_select" ON public.announcements
    FOR SELECT TO authenticated USING (is_active = true);
CREATE POLICY "ann_insert" ON public.announcements
    FOR INSERT TO authenticated
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.users WHERE id = auth.uid() AND role IN ('club_admin', 'admin')
    ));
CREATE POLICY "ann_update" ON public.announcements
    FOR UPDATE TO authenticated
    USING (
        author_id = auth.uid()
        OR EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
    );
CREATE POLICY "ann_delete" ON public.announcements
    FOR DELETE TO authenticated
    USING (
        author_id = auth.uid()
        OR EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
    );

-- Saved announcements: own only
CREATE POLICY "saved_ann_select" ON public.saved_announcements
    FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE POLICY "saved_ann_insert" ON public.saved_announcements
    FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
CREATE POLICY "saved_ann_delete" ON public.saved_announcements
    FOR DELETE TO authenticated USING (user_id = auth.uid());

-- Resources: all read active; authenticated upload own; owner/admin delete
CREATE POLICY "resources_select" ON public.resources
    FOR SELECT TO authenticated USING (is_active = true);
CREATE POLICY "resources_insert" ON public.resources
    FOR INSERT TO authenticated WITH CHECK (uploader_id = auth.uid());
CREATE POLICY "resources_delete" ON public.resources
    FOR DELETE TO authenticated
    USING (
        uploader_id = auth.uid()
        OR EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
    );

-- Bookmarked resources: own only
CREATE POLICY "bm_res_select" ON public.bookmarked_resources
    FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE POLICY "bm_res_insert" ON public.bookmarked_resources
    FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
CREATE POLICY "bm_res_delete" ON public.bookmarked_resources
    FOR DELETE TO authenticated USING (user_id = auth.uid());

-- Parcel requests: all authenticated read; requester inserts; requester/helper/admin update
CREATE POLICY "parcel_select" ON public.parcel_requests
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "parcel_insert" ON public.parcel_requests
    FOR INSERT TO authenticated WITH CHECK (requester_id = auth.uid());
CREATE POLICY "parcel_update" ON public.parcel_requests
    FOR UPDATE TO authenticated
    USING (
        requester_id = auth.uid()
        OR helper_id = auth.uid()
        OR EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
    );

-- Tomato transactions: own read; any authenticated insert (controlled by app logic)
CREATE POLICY "tomato_select" ON public.tomato_transactions
    FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE POLICY "tomato_insert" ON public.tomato_transactions
    FOR INSERT TO authenticated WITH CHECK (true);

-- Lost and found: all read; reporter inserts; reporter/admin update
CREATE POLICY "lf_select" ON public.lost_found
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "lf_insert" ON public.lost_found
    FOR INSERT TO authenticated WITH CHECK (reporter_id = auth.uid());
CREATE POLICY "lf_update" ON public.lost_found
    FOR UPDATE TO authenticated
    USING (
        reporter_id = auth.uid()
        OR EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
    );

-- Notifications: own only
CREATE POLICY "notif_select" ON public.notifications
    FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE POLICY "notif_insert" ON public.notifications
    FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "notif_update" ON public.notifications
    FOR UPDATE TO authenticated USING (user_id = auth.uid());
CREATE POLICY "notif_delete" ON public.notifications
    FOR DELETE TO authenticated USING (user_id = auth.uid());

-- Audit logs: only admins read; any authenticated insert
CREATE POLICY "audit_select" ON public.audit_logs
    FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin'));
CREATE POLICY "audit_insert" ON public.audit_logs
    FOR INSERT TO authenticated WITH CHECK (true);

-- =============================================================================
-- TRIGGERS – auto-update updated_at
-- =============================================================================

CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER trg_events_updated_at
    BEFORE UPDATE ON public.events
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER trg_announcements_updated_at
    BEFORE UPDATE ON public.announcements
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER trg_parcel_updated_at
    BEFORE UPDATE ON public.parcel_requests
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER trg_lf_updated_at
    BEFORE UPDATE ON public.lost_found
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- =============================================================================
-- TRIGGER – auto-create public.users profile on Supabase Auth signup
-- Runs with SECURITY DEFINER so it bypasses RLS (no JWT required).
-- =============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_auth_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, role, tomato_balance)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
    'student',
    50
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_auth_user();

-- =============================================================================
-- STORAGE
-- =============================================================================
-- Run these steps manually in the Supabase Dashboard → Storage:
--   1. Create a bucket named "campusconnect".
--   2. Set the bucket to PUBLIC (enables direct URL access for file_url columns).
--   3. Add the following storage policies:
--      * SELECT (read):   allow anon and authenticated
--      * INSERT (upload): allow authenticated only
--      * UPDATE/DELETE:   allow file owner or admin only
-- =============================================================================
