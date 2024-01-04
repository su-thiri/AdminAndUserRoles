from rest_framework.permissions import BasePermission
# from guardian.decorators import permission_required_or_403
# from django.contrib.auth.models import Group
# from django.http import HttpResponse

class IsSystemAdmin(BasePermission):
    """
    Allows access only to admins.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.is_superuser
        )


class IsSystemUser(BasePermission):
    """
    Allows access only to users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_staff
            and not request.user.is_superuser
        )

# @permission_required_or_403('can_access', (Group, 'name', 'group_name'))
# def edit_group(request, group_name):
#      return HttpResponse('some form')