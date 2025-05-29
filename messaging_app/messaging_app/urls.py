"""
URL configuration for messaging_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect


def api_info(request):
    """Root API endpoint with available endpoints."""
    return JsonResponse({
        'message': 'Welcome to Django Messaging API',
        'version': '1.0.0',
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
            'users': '/api/users/',
            'conversations': '/api/conversations/',
            'messages': '/api/messages/',
            'auth': '/api/auth/',
        },
        'documentation': 'Visit /api/ for browsable API documentation'
    })


def root_redirect(request):
    """Redirect root URL to API."""
    return redirect('/api/')


urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-info/', api_info, name='api-info'),
]