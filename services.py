import repositories

class UserService:
    @staticmethod
    def get_by_email(email):
        return repositories.get_user_by_email(email)
        
    @staticmethod
    def register(email, name, role="student"):
        return repositories.register_user(email, name, role)
        
    @staticmethod
    def get_by_id(user_id):
        return repositories.get_user_by_id(user_id)

class EventService:
    @staticmethod
    def get_all():
        return repositories.get_events()
        
    @staticmethod
    def create(title, description, banner_url, date, time, venue, organizer_id, organizer_name, capacity):
        return repositories.create_event(title, description, banner_url, date, time, venue, organizer_id, organizer_name, capacity)
        
    @staticmethod
    def register(event_id, user_id):
        return repositories.register_for_event(event_id, user_id)
        
    @staticmethod
    def unregister(event_id, user_id):
        return repositories.unregister_from_event(event_id, user_id)
        
    @staticmethod
    def is_registered(event_id, user_id):
        return repositories.is_user_registered_for_event(event_id, user_id)
        
    @staticmethod
    def get_user_events(user_id):
        return repositories.get_user_registered_events(user_id)

class AnnouncementService:
    @staticmethod
    def get_all():
        return repositories.get_announcements()
        
    @staticmethod
    def create(title, content, category, priority, author):
        return repositories.create_announcement(title, content, category, priority, author)
        
    @staticmethod
    def save(user_id, announcement_id):
        return repositories.save_announcement(user_id, announcement_id)
        
    @staticmethod
    def unsave(user_id, announcement_id):
        return repositories.unsave_announcement(user_id, announcement_id)
        
    @staticmethod
    def is_saved(user_id, announcement_id):
        return repositories.is_announcement_saved(user_id, announcement_id)
        
    @staticmethod
    def get_user_saved(user_id):
        return repositories.get_saved_announcements(user_id)

class ResourceService:
    @staticmethod
    def get_all():
        return repositories.get_resources()
        
    @staticmethod
    def upload(title, course_code, course_name, category, file_url, uploader_id, uploader_name):
        return repositories.upload_resource(title, course_code, course_name, category, file_url, uploader_id, uploader_name)
        
    @staticmethod
    def bookmark(user_id, resource_id):
        return repositories.bookmark_resource(user_id, resource_id)
        
    @staticmethod
    def unbookmark(user_id, resource_id):
        return repositories.unbookmark_resource(user_id, resource_id)
        
    @staticmethod
    def is_bookmarked(user_id, resource_id):
        return repositories.is_resource_bookmarked(user_id, resource_id)
        
    @staticmethod
    def get_user_bookmarked(user_id):
        return repositories.get_bookmarked_resources(user_id)

class ParcelService:
    @staticmethod
    def get_all():
        return repositories.get_logistics_requests()
        
    @staticmethod
    def create_request(requester_id, title, description, pickup_location, delivery_location, tomatoes_offered=5):
        # Validate balance
        user = UserService.get_by_id(requester_id)
        if user and user.get("tomatoes", 0) >= tomatoes_offered:
            req = repositories.create_logistics_request(requester_id, title, description, pickup_location, delivery_location, tomatoes_offered)
            if req:
                TomatoService.deduct(requester_id, tomatoes_offered, f"Created parcel request: {title}")
                return req
        return None
        
    @staticmethod
    def accept_request(request_id, helper_id):
        return repositories.accept_logistics_request(request_id, helper_id)
        
    @staticmethod
    def update_status(request_id, new_status):
        req = repositories.update_logistics_status(request_id, new_status)
        if req and new_status == "Delivered":
            helper_id = req.get("helper_id")
            tomatoes_offered = req.get("tomatoes_offered", 5)
            if helper_id:
                TomatoService.add(helper_id, tomatoes_offered, f"Completed delivery: {req['title']}")
        return req

class LostFoundService:
    @staticmethod
    def get_all():
        return repositories.get_lost_found_items()
        
    @staticmethod
    def report(title, description, category, item_type, location, image_url, reporter_id, reporter_name):
        return repositories.report_lost_found_item(title, description, category, item_type, location, image_url, reporter_id, reporter_name)
        
    @staticmethod
    def update_status(item_id, status):
        return repositories.update_lost_found_status(item_id, status)

class NotificationService:
    @staticmethod
    def get_all(user_id):
        return repositories.get_notifications(user_id)
        
    @staticmethod
    def add(user_id, title, content):
        return repositories.add_notification(user_id, title, content)
        
    @staticmethod
    def mark_read(notification_id):
        return repositories.mark_notification_as_read(notification_id)
        
    @staticmethod
    def clear_all(user_id):
        return repositories.clear_all_notifications(user_id)

class TomatoService:
    @staticmethod
    def get_transactions(user_id):
        return repositories.get_tomato_transactions(user_id)
        
    @staticmethod
    def add(user_id, amount, description):
        user = repositories.get_user_by_id(user_id)
        if user:
            new_balance = user.get("tomatos", 0) + amount
            repositories.update_user_tomatos(user_id, new_balance)
            repositories.add_tomato_transaction(user_id, amount, description)
            
    @staticmethod
    def deduct(user_id, amount, description):
        user = repositories.get_user_by_id(user_id)
        if user:
            new_balance = user.get("tomatos", 0) - amount
            repositories.update_user_tomatos(user_id, new_balance)
            repositories.add_tomato_transaction(user_id, -amount, description)

