"""
URL configuration for the chats app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Try to import nested routers, if not available, use basic router
try:
    from rest_framework_nested import routers as nested_routers
    HAS_NESTED_ROUTERS = True
except ImportError:
    HAS_NESTED_ROUTERS = False
    nested_routers = None


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API root endpoint showing available endpoints.
    """
    return Response({
        'message': 'Welcome to Django Messaging API',
        'version': '1.0.0',
        'endpoints': {
            'users': reverse('user-list', request=request, format=format),
            'conversations': reverse('conversation-list', request=request, format=format),
            'messages': reverse('message-list', request=request, format=format),
        },
        'authentication': {
            'login': request.build_absolute_uri('/api/token/'),
            'refresh': request.build_absolute_uri('/api/token/refresh/'),
            'api-auth': request.build_absolute_uri('/api-auth/'),
        },
        'documentation': 'This browsable API allows you to interact with the messaging system.',
        'note': 'Most endpoints require authentication. Create a user account first or login to access protected resources.'
    })


# Create a DefaultRouter and register our viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Create nested router if available
nested_urls = []
if HAS_NESTED_ROUTERS and nested_routers:
    conversations_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
    conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')
    nested_urls = conversations_router.urls

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', api_root, name='api-root'),
    path('auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
] + nested_urls