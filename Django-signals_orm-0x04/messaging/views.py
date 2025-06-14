from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Message

User = get_user_model()

@login_required
@require_POST
def delete_user(request):
    """
    View for user account deletion.
    Requires POST request and user authentication.
    """
    user = request.user
    user.delete()
    messages.success(request, "Your account has been successfully deleted.")
    return redirect('home')

@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Signal handler to clean up related data when a user is deleted.
    Note: Most data will be deleted via CASCADE, but this can handle special cases.
    """
    # Additional cleanup can be added here if needed
    # For example, if you have any non-relational data or special cases
    pass

def thread_view(request, message_id):
    """
    View for displaying a threaded conversation.
    Shows the main message and all its replies in a hierarchical structure.
    """
    main_message = Message.objects.select_related(
        'sender', 'receiver', 'parent_message'
    ).prefetch_related(
        'replies__sender',
        'replies__receiver',
        'replies__replies'
    ).get(pk=message_id)
    
    # Get all messages in the thread (main message + all replies)
    all_messages = [main_message] + main_message.get_all_replies()
    
    # Mark messages as read when viewed
    if request.user == main_message.receiver:
        Message.objects.filter(
            pk__in=[msg.id for msg in all_messages],
            receiver=request.user,
            read=False
        ).update(read=True)
    
    return render(request, 'messaging/thread.html', {
        'main_message': main_message,
        'messages': all_messages
    })