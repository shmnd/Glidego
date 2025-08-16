from rest_framework.permissions import BasePermission

def has_permission(permission, app_label):
    """
    Factory function to create a permission class for a specific permission and app_label.
    """
    class HasPermission(BasePermission):
        def has_permission(self, request, view):
            # Ensure the user is authenticated
            if not request.user or not request.user.is_authenticated:
                return False

            # Construct the permission codename (e.g., 'Hotel.view_branch')
            permission_codename = f"{app_label}.{permission}"

            # Check if the user has the specific permission
            return request.user.has_perm(permission_codename)

    # Set a meaningful name for the class to aid debugging
    HasPermission.__name__ = f"HasPermission_{app_label}_{permission}"
    return HasPermission