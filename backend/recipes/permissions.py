from rest_framework.permissions import BasePermission, SAFE_METHODS


class CustomPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('PATCH', 'DELETE'):
            return obj.author == request.user
        if (request.method in ('PATCH', 'DELETE')
                and request.user.is_authenticated):
            return request.user.is_admin
        if request.method in SAFE_METHODS:
            return True
