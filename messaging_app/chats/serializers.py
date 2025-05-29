"""
Serializers for the messaging application API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with essential fields for API responses.
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone_number', 'profile_picture', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users with password handling.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'password', 'password_confirm'
        ]

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        """Create user with encrypted password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with nested sender information.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation',
            'message_body', 'sent_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create message with sender from request user if not provided."""
        request = self.context.get('request')
        if request and not validated_data.get('sender_id'):
            validated_data['sender'] = request.user
        elif validated_data.get('sender_id'):
            validated_data['sender'] = User.objects.get(user_id=validated_data.pop('sender_id'))
        return super().create(validated_data)


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating messages.
    """
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']

    def create(self, validated_data):
        """Create message with sender from request context."""
        request = self.context.get('request')
        validated_data['sender'] = request.user
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested participants and messages.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)
    participant_count = serializers.ReadOnlyField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'messages', 'last_message', 'participant_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create conversation and add participants."""
        participant_ids = validated_data.pop('participant_ids', [])
        request = self.context.get('request')
        
        # Create the conversation
        conversation = Conversation.objects.create()
        
        # Add the requesting user as a participant
        if request and request.user:
            conversation.participants.add(request.user)
        
        # Add other participants
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.add(*participants)
        
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing conversations without full message history.
    """
    participants = UserSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)
    participant_count = serializers.ReadOnlyField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'last_message',
            'participant_count', 'created_at', 'updated_at'
        ]