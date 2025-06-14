from django.urls import path
from .views import delete_user, thread_view

urlpatterns = [
    path('delete/', delete_user, name='delete_user'),
    path('thread/<int:message_id>/', thread_view, name='thread_view'),
]