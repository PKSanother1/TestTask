from rest_framework.permissions import BasePermission
from .permissions import check_permission, check_object_permission


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None and request.user.role.name == "admin"


class CanReadProducts(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None and check_permission(request.user, "products", "read")


class CanCreateProducts(BasePermission):
    def has_permission(self, request, view):
        return request.user is not None and check_permission(request.user, "products", "create")


class CanUpdateProductObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user is None:
            return False
        return check_object_permission(
            request.user,
            "products",
            "update",
            owner_id=obj.owner_id
        )


class CanDeleteProductObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user is None:
            return False
        return check_object_permission(
            request.user,
            "products",
            "delete",
            owner_id=obj.owner_id
        )


class CanReadProductObject(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user is None:
            return False
        return check_object_permission(
            request.user,
            "products",
            "read",
            owner_id=obj.owner_id
        )