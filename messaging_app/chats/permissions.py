from rest_framework.permissions import BasePermission

class IsParticipantOfConversation(BasePermission):
    """
    Allows access only to participants of the conversation for all operations:
    - View (GET)
    - Create (POST)
    - Update (PUT/PATCH)
    - Delete (DELETE)
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated for any action
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow GET, POST, PUT, PATCH, DELETE if the user is a participant
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user in obj.conversation.participants.all()
        return False
