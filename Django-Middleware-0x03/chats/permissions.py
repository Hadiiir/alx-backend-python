from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to interact with it.
    """

    def has_object_permission(self, request, view, obj):
        # Read, update and delete permissions are only allowed to participants
        if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            return request.user in obj.participants.all()
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated