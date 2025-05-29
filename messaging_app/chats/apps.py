"""
App configuration for the chats application.
"""
from django.apps import AppConfig


class ChatsConfig(AppConfig):
    """
    Configuration for the chats app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chats'
    verbose_name = 'Messaging System'