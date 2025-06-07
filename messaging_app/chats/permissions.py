from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # For conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For message objects
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False
    
    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated