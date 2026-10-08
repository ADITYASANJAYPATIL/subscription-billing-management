from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access only to users in the Admin group.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Admin").exists()
        )


class IsCustomerRole(BasePermission):
    """
    Allows access only to users in the Customer group.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Customer").exists()
        )

class IsOwnerOrAdmin(BasePermission):
    """
    Allows access to the object owner or an Admin.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name="Admin").exists():
            return True

        customer_profile = getattr(
            request.user,
            "customer_profile",
            None
        )

        if customer_profile is None:
            return False

        return obj.customer == customer_profile
    