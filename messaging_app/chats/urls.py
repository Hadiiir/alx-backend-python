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
            'login': request.build_absolute_uri('/api/auth/login/'),
            'logout': request.build_absolute_uri('/api/auth/logout/'),
        },
        'documentation': 'This browsable API allows you to interact with the messaging system.',
        'note': 'Most endpoints require authentication. Create a user account first or login to access protected resources.'
    })


# Create a DefaultRouter and register our viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', api_root, name='api-root'),
    path('auth/', include('rest_framework.urls')),
] + router.urls