from rest_framework.permissions import BasePermission


class UserPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'PUT', 'PATCH', 'OPTIONS', 'HEAD'):
        # Only gives access to users while restricting them
            return True
        return request.user


class IsAdminAuthenticated(BasePermission):
    def has_permission(self, request, view):
        # Only gives access to authenticated administrator users
        return bool(request.user and request.user.is_superuser)
