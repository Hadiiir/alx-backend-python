"""
Models for the messaging application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    """
    Extended User model with additional fields for messaging functionality.
    """
    user_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the user"
    )
    email = models.EmailField(
        unique=True,
        help_text="User's email address"
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="User's phone number"
    )
    first_name = models.CharField(
        max_length=30,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=30,
        help_text="User's last name"
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="User's date of birth"
    )
    profile_picture = models.URLField(
        blank=True, 
        null=True,
        help_text="URL to user's profile picture"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when user was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when user was last updated"
    )

    # Override username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()


class Conversation(models.Model):
    """
    Model representing a conversation between multiple users.
    """
    conversation_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the conversation"
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text="Users participating in this conversation"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when conversation was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when conversation was last updated"
    )

    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']

    def __str__(self):
        participant_names = ", ".join([user.full_name for user in self.participants.all()[:3]])
        if self.participants.count() > 3:
            participant_names += f" and {self.participants.count() - 3} others"
        return f"Conversation: {participant_names}"

    @property
    def last_message(self):
        """Return the most recent message in this conversation."""
        return self.messages.order_by('-created_at').first()

    @property
    def participant_count(self):
        """Return the number of participants in this conversation."""
        return self.participants.count()


class Message(models.Model):
    """
    Model representing a message within a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the message"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent this message"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Conversation this message belongs to"
    )
    message_body = models.TextField(
        help_text="Content of the message"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when message was sent"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when message was last updated"
    )

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']

    def __str__(self):
        preview = self.message_body[:50] + "..." if len(self.message_body) > 50 else self.message_body
        return f"{self.sender.full_name}: {preview}"

    def save(self, *args, **kwargs):
        """Override save to update conversation's updated_at timestamp."""
        super().save(*args, **kwargs)
        # Update the conversation's updated_at field
        self.conversation.updated_at = timezone.now()
        self.conversation.save(update_fields=['updated_at'])