import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden
from collections import defaultdict

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that require special permissions
        admin_paths = ['/admin/', '/admin-dashboard/']  # Add your admin paths here
        moderator_paths = ['/moderate/', '/moderator-dashboard/']  # Add moderator paths
        
        # Check if current path requires admin permissions
        if any(request.path.startswith(path) for path in admin_paths):
            if not request.user.is_authenticated or not request.user.is_superuser:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Admin access required")

        # Check if current path requires moderator permissions
        if any(request.path.startswith(path) for path in moderator_paths):
            if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Moderator access required")

        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_counts = defaultdict(list)
        self.limit = 5  # 5 messages per minute
        self.window = 60  # 60 seconds

    def __call__(self, request):
        if request.method == 'POST' and request.path == '/path_to_chat_endpoint':  # Update with your chat endpoint
            ip = request.META.get('REMOTE_ADDR')
            now = datetime.now()
            
            # Remove old timestamps
            self.message_counts[ip] = [
                timestamp for timestamp in self.message_counts[ip]
                if now - timestamp < timedelta(seconds=self.window)
            ]
            
            # Check if limit exceeded
            if len(self.message_counts[ip]) >= self.limit:
                return HttpResponseForbidden("Rate limit exceeded. Please wait before sending more messages.")
            
            # Add current timestamp
            self.message_counts[ip].append(now)
        
        return self.get_response(request)
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if current_hour < 18 and current_hour >= 9:  # Between 9AM and 6PM
            return HttpResponseForbidden("Chat access is restricted between 9AM and 6PM")
        return self.get_response(request)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configure logger
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('chats/requests.log')
        self.logger.addHandler(handler)

    def __call__(self, request):
        user = request.user.username if request.user.is_authenticated else "Anonymous"
        self.logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        return self.get_response(request)
