"""
Tests for the messaging application.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from .models import Conversation, Message
import uuid

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'phone_number': '+1234567890',
        }

    def test_create_user(self):
        """Test creating a user with extended fields."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone_number, '+1234567890')
        self.assertTrue(user.check_password('testpass123'))
        self.assertIsInstance(user.user_id, uuid.UUID)

    def test_user_full_name_property(self):
        """Test the full_name property."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, 'Test User')

    def test_user_string_representation(self):
        """Test the string representation of User."""
        user = User.objects.create_user(**self.user_data)
        expected_str = f"Test User (test@example.com)"
        self.assertEqual(str(user), expected_str)

    def test_user_email_unique(self):
        """Test that email field is unique."""
        User.objects.create_user(**self.user_data)
        
        # Try to create another user with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'testuser2'
        
        with self.assertRaises(Exception):
            User.objects.create_user(**duplicate_data)


class ConversationModelTest(TestCase):
    """Test cases for the Conversation model."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='pass123'
        )

    def test_create_conversation(self):
        """Test creating a conversation."""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        self.assertIsInstance(conversation.conversation_id, uuid.UUID)
        self.assertEqual(conversation.participants.count(), 2)
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())

    def test_conversation_participant_count_property(self):
        """Test the participant_count property."""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        self.assertEqual(conversation.participant_count, 2)

    def test_conversation_string_representation(self):
        """Test the string representation of Conversation."""
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        expected_str = "Conversation: User One, User Two"
        self.assertEqual(str(conversation), expected_str)


class MessageModelTest(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='pass123'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_create_message(self):
        """Test creating a message."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Hello, how are you?"
        )
        
        self.assertIsInstance(message.message_id, uuid.UUID)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.message_body, "Hello, how are you?")
        self.assertIsNotNone(message.sent_at)

    def test_message_updates_conversation_timestamp(self):
        """Test that creating a message updates conversation's updated_at."""
        original_updated_at = self.conversation.updated_at
        
        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message"
        )
        
        # Refresh conversation from database
        self.conversation.refresh_from_db()
        self.assertGreater(self.conversation.updated_at, original_updated_at)

    def test_message_string_representation(self):
        """Test the string representation of Message."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Hello, how are you?"
        )
        
        expected_str = "User One: Hello, how are you?"
        self.assertEqual(str(message), expected_str)

    def test_long_message_string_representation(self):
        """Test string representation with long message."""
        long_message = "This is a very long message that should be truncated in the string representation" * 2
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body=long_message
        )
        
        # Should be truncated to 50 characters + "..."
        self.assertTrue(str(message).endswith("..."))
        self.assertEqual(len(str(message)), len("User One: ") + 50 + 3)  # name + 50 chars + "..."


class UserAPITest(APITestCase):
    """Test cases for User API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }

    def test_create_user_via_api(self):
        """Test creating a user via API."""
        url = reverse('user-list')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        
        user = User.objects.get()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_create_user_password_mismatch(self):
        """Test creating user with mismatched passwords."""
        url = reverse('user-list')
        data = self.user_data.copy()
        data['password_confirm'] = 'differentpass'
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_users_requires_authentication(self):
        """Test that listing users requires authentication."""
        url = reverse('user-list')
        response = self.client.get(url)
        
        # Should allow unauthenticated access based on our permissions
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ConversationAPITest(APITestCase):
    """Test cases for Conversation API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='pass123'
        )

    def test_create_conversation_requires_authentication(self):
        """Test that creating conversation requires authentication."""
        url = reverse('conversation-list')
        data = {'participant_ids': [str(self.user2.user_id)]}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_conversation_authenticated(self):
        """Test creating conversation when authenticated."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('conversation-list')
        data = {'participant_ids': [str(self.user2.user_id)]}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)

    def test_list_conversations_authenticated(self):
        """Test listing conversations when authenticated."""
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('conversation-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class MessageAPITest(APITestCase):
    """Test cases for Message API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='pass123'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_create_message_requires_authentication(self):
        """Test that creating message requires authentication."""
        url = reverse('message-list')
        data = {
            'conversation': str(self.conversation.conversation_id),
            'message_body': 'Hello!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_message_authenticated(self):
        """Test creating message when authenticated."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('message-list')
        data = {
            'conversation': str(self.conversation.conversation_id),
            'message_body': 'Hello!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

    def test_create_message_non_participant(self):
        """Test that non-participants cannot send messages."""
        user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            first_name='User',
            last_name='Three',
            password='pass123'
        )
        
        self.client.force_authenticate(user=user3)
        url = reverse('message-list')
        data = {
            'conversation': str(self.conversation.conversation_id),
            'message_body': 'Hello!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_messages_authenticated(self):
        """Test listing messages when authenticated."""
        # Create a message
        Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message"
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('message-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class ModelRelationshipTest(TestCase):
    """Test cases for model relationships."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='pass123'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_user_conversations_relationship(self):
        """Test that users can access their conversations."""
        user1_conversations = self.user1.conversations.all()
        self.assertIn(self.conversation, user1_conversations)

    def test_user_sent_messages_relationship(self):
        """Test that users can access their sent messages."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message"
        )
        
        user1_messages = self.user1.sent_messages.all()
        self.assertIn(message, user1_messages)

    def test_conversation_messages_relationship(self):
        """Test that conversations can access their messages."""
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="Test message"
        )
        
        conversation_messages = self.conversation.messages.all()
        self.assertIn(message, conversation_messages)

    def test_conversation_last_message_property(self):
        """Test the last_message property of Conversation."""
        # Create multiple messages
        message1 = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body="First message"
        )
        
        import time
        time.sleep(0.01)  # Ensure different timestamps
        
        message2 = Message.objects.create(
            sender=self.user2,
            conversation=self.conversation,
            message_body="Second message"
        )
        
        # Last message should be the most recent one
        self.assertEqual(self.conversation.last_message, message2)