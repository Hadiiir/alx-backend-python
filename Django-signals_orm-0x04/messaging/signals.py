from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """Delete all related data when user is deleted"""
    # Delete messages where user is sender or receiver
    Message.objects.filter(
        models.Q(sender=instance) | models.Q(receiver=instance)
    ).delete()
    
    # Delete notifications for user
    Notification.objects.filter(user=instance).delete()
    
    # Delete message history edited by user
    MessageHistory.objects.filter(edited_by=instance).delete()

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    if instance.pk:  # Only for updates
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    content=old_message.content,
                    edited_by=instance.edited_by
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass
        