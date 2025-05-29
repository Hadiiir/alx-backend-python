"""
Admin configuration for the messaging application.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for the custom User model.
    """
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'date_of_birth', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['user_id', 'created_at', 'updated_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin interface for the Conversation model.
    """
    list_display = ['conversation_id', 'participant_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    readonly_fields = ['conversation_id', 'created_at', 'updated_at']
    filter_horizontal = ['participants']
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for the Message model.
    """
    list_display = ['message_id', 'sender', 'conversation', 'message_preview', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['sender__email', 'sender__first_name', 'message_body']
    readonly_fields = ['message_id', 'created_at', 'updated_at']
    raw_id_fields = ['sender', 'conversation']
    
    def message_preview(self, obj):
        return obj.message_body[:50] + "..." if len(obj.message_body) > 50 else obj.message_body
    message_preview.short_description = 'Message Preview'