from django.views.decorators.cache import cache_page
from django.shortcuts import render
from .models import Message
from django.contrib.auth.decorators import login_required

@login_required
@cache_page(60)
def conversation_view(request, user_id):
    # Get conversation between current user and the other user
    messages = Message.objects.filter(
        models.Q(sender=request.user, receiver_id=user_id) |
        models.Q(sender_id=user_id, receiver=request.user)
    ).select_related('sender', 'receiver').order_by('timestamp')
    
    return render(request, 'chats/conversation.html', {
        'messages': messages,
        'other_user_id': user_id
    })