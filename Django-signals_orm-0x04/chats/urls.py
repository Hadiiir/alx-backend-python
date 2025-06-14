from django.urls import path
from .views import conversation_view, thread_view

urlpatterns = [
    path('conversation/<int:conversation_id>/', conversation_view, name='conversation'),
    path('thread/<int:message_id>/', thread_view, name='thread'),
]