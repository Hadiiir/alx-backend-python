from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, MessageHistory

@login_required
def message_thread(request, message_id):
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('history', 'replies'),
        pk=message_id
    )
    
    # Get full thread with optimized queries
    thread = {
        'message': message,
        'replies': message.get_thread(),
        'history': message.history.all().select_related('edited_by')
    }
    
    return render(request, 'messaging/thread.html', thread)

@login_required
def inbox(request):
    unread_messages = Message.unread.for_user(request.user)
    return render(request, 'messaging/inbox.html', {'messages': unread_messages})

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    history = message.history.all().select_related('edited_by').only(
        'content',
        'edited_at',
        'edited_by__username'
    )
    return render(request, 'messaging/history.html', {
        'message': message,
        'history': history
    })