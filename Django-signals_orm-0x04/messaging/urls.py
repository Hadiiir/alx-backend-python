from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('thread/<int:message_id>/', views.message_thread, name='message_thread'),
    path('inbox/', views.inbox, name='inbox'),
    path('history/<int:message_id>/', views.message_history, name='message_history'),
]