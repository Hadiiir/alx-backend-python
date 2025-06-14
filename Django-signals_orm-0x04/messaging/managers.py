from django.db import models

class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)

    def unread_for_user(self, user):
        """Optimized query for unread messages for specific user"""
        return self.get_queryset().filter(receiver=user).select_related(
            'sender', 'receiver'
        ).only(
            'id',
            'content',
            'timestamp',
            'sender__username',
            'receiver__username'
        ).order_by('-timestamp')