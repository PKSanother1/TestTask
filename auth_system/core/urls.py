from django.urls import path
from .views import (
    register,
    login,
    logout,
    refresh_access_token,
    update_profile,
    delete_user,
    products,
    create_product,
    update_product,
    delete_product,
    access_rules,
    update_access_rule,
)

urlpatterns = [
    path("register/", register),
    path("login/", login),
    path("logout/", logout),
    path("token/refresh/", refresh_access_token),

    path("profile/", update_profile),
    path("profile/delete/", delete_user),

    path("products/", products),
    path("products/create/", create_product),
    path("products/<int:product_id>/update/", update_product),
    path("products/<int:product_id>/delete/", delete_product),

    path("access-rules/", access_rules),
    path("access-rules/update/", update_access_rule),
]