"""
API views for the messaging application.
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

# Try to import django_filters, if not available, use basic filtering
try:
    from django_filters.rest_framework import DjangoFilterBackend
    HAS_DJANGO_FILTERS = True
except ImportError:
    HAS_DJANGO_FILTERS = False
    DjangoFilterBackend = None

from .models import Conversation, Message
from .serializers import (
    UserSerializer, UserCreateSerializer, ConversationSerializer,
    ConversationListSerializer, MessageSerializer, MessageCreateSerializer
)
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination, ConversationPagination

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    Provides CRUD operations for User model.
    """
    queryset = User.objects.all()
    
    # Set up filter backends conditionally
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if HAS_DJANGO_FILTERS and DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username', 'email']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        """Allow unauthenticated access for user creation and list view."""
        if self.action in ['create', 'list']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by name or email."""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'detail': 'Query parameter "q" is required.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        )
        
        # Exclude current user if authenticated
        if request.user.is_authenticated:
            users = users.exclude(user_id=request.user.user_id)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides CRUD operations for Conversation model.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_class = ConversationFilter
    pagination_class = ConversationPagination
    
    # Set up filter backends conditionally
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if HAS_DJANGO_FILTERS and DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
        filterset_fields = ['participants', 'created_at']
    
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return conversations where the current user is a participant."""
        return self.request.user.conversations.all().prefetch_related('participants', 'messages__sender').distinct()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        """Create a new conversation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return full conversation data
        response_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'detail': 'user_id is required.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response({'detail': f'User {user.full_name} added to conversation.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, 
                          status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'detail': 'user_id is required.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            return Response({'detail': f'User {user.full_name} removed from conversation.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, 
                          status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a conversation."""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides CRUD operations for Message model.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_class = MessageFilter
    pagination_class = MessagePagination
    
    # Set up filter backends conditionally
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if HAS_DJANGO_FILTERS and DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
        filterset_fields = ['conversation', 'sender', 'sent_at']
    
    search_fields = ['message_body', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        """Return messages from conversations where the current user is a participant."""
        queryset = Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').order_by('-timestamp').distinct()
        
        # Filter by conversation if provided in URL
        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk:
            queryset = queryset.filter(conversation__conversation_id=conversation_pk)
            
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        """Create a new message."""
        # Handle nested route case
        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk:
            request.data['conversation'] = conversation_pk
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify user is participant in the conversation
        conversation_id = request.data.get('conversation')
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {'detail': 'You are not a participant in this conversation.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except Conversation.DoesNotExist:
            return Response(
                {'detail': 'Conversation not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        message = serializer.save()
        response_serializer = MessageSerializer(message, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    pagination_class = MessagePagination 
    permission_classes = [IsParticipantOfConversation]

    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """Get messages filtered by conversation."""
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response(
                {'detail': 'conversation_id parameter is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(
            conversation__conversation_id=conversation_id
        ).order_by('sent_at')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)