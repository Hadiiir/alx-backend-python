from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.contrib.auth import get_user_model

User = get_user_model()

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
                MessageHistory.objects.create(message=instance, content=old_message.content)
                instance.edited = True
        except Message.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    # Messages where user is sender or receiver will be deleted due to CASCADE
    # Notifications related to user will be deleted due to CASCADE
    # No need for explicit deletion if using CASCADE
    pass