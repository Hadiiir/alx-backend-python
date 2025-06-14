from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Message, MessageHistory, Notification

User = get_user_model()

@login_required
def inbox(request):
    """View using custom manager to show unread messages"""
    unread_messages = Message.unread.unread_for_user(request.user)
    return render(request, 'messaging/inbox.html', {
        'messages': unread_messages
    })

@login_required
@cache_page(60)  # 60 seconds cache
def conversation_view(request, user_id):
    """Cached view showing conversation between current user and another user"""
    conversation = Message.objects.filter(
        models.Q(sender=request.user, receiver_id=user_id) |
        models.Q(sender_id=user_id, receiver=request.user)
    ).select_related('sender', 'receiver').prefetch_related(
        'replies', 'replies__sender', 'replies__receiver'
    ).only(
        'id', 'content', 'timestamp', 'read', 'edited',
        'sender__username', 'receiver__username'
    ).order_by('timestamp')
    
    return render(request, 'messaging/conversation.html', {
        'messages': conversation,
        'other_user_id': user_id
    })

@login_required
def inbox(request):
    """View using custom manager to show unread messages"""
    unread_messages = Message.unread.for_user(request.user)
    return render(request, 'messaging/inbox.html', {
        'messages': unread_messages
    })

@login_required
def message_thread(request, message_id):
    """Recursive threaded message view with optimized queries"""
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('history', 'replies__sender', 'replies__receiver'),
        pk=message_id
    )
    
    # Mark as read when viewed
    if message.receiver == request.user and not message.read:
        message.read = True
        message.save()
    
    return render(request, 'messaging/thread.html', {
        'message': message,
        'replies': message.get_thread()
    })

@login_required
def delete_user(request):
    """View to handle user account deletion"""
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    return render(request, 'messaging/delete_user.html')