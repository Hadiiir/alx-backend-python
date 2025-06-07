import django_filters
from .models import Message, Conversation
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class MessageFilter(django_filters.FilterSet):
    sender = django_filters.ModelChoiceFilter(
        field_name='sender',
        queryset=User.objects.all()
    )
    conversation = django_filters.ModelChoiceFilter(
        field_name='conversation',
        queryset=Conversation.objects.all()
    )
    after = django_filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='gte'
    )
    before = django_filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='lte'
    )

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'after', 'before']

class ConversationFilter(django_filters.FilterSet):
    participant = django_filters.ModelChoiceFilter(
        field_name='participants',
        queryset=User.objects.all()
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = Conversation
        fields = ['participant', 'created_after', 'created_before']