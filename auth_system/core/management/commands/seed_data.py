from django.core.management.base import BaseCommand
from TestTask.auth_system.core.models import Role, BusinessElement, AccessRule, User, Product
from TestTask.auth_system.core.utils import hash_password


class Command(BaseCommand):
    help = "Seed initial roles, resources, rules and test users"

    def handle(self, *args, **kwargs):
        admin_role, _ = Role.objects.get_or_create(name="admin")
        user_role, _ = Role.objects.get_or_create(name="user")

        products_resource, _ = BusinessElement.objects.get_or_create(name="products")
        access_rules_resource, _ = BusinessElement.objects.get_or_create(name="access_rules")

        admin_user, _ = User.objects.get_or_create(
            email="admin@test.com",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "patronymic": "",
                "password": hash_password("admin123"),
                "role": admin_role,
                "is_active": True,
            }
        )

        regular_user, _ = User.objects.get_or_create(
            email="user@test.com",
            defaults={
                "first_name": "Regular",
                "last_name": "User",
                "patronymic": "",
                "password": hash_password("user123"),
                "role": user_role,
                "is_active": True,
            }
        )

        AccessRule.objects.update_or_create(
            role=admin_role,
            element=products_resource,
            defaults={
                "can_read": True,
                "can_read_all": True,
                "can_create": True,
                "can_update": True,
                "can_update_all": True,
                "can_delete": True,
                "can_delete_all": True,
            }
        )

        AccessRule.objects.update_or_create(
            role=admin_role,
            element=access_rules_resource,
            defaults={
                "can_read": True,
                "can_read_all": True,
                "can_create": True,
                "can_update": True,
                "can_update_all": True,
                "can_delete": True,
                "can_delete_all": True,
            }
        )

        AccessRule.objects.update_or_create(
            role=user_role,
            element=products_resource,
            defaults={
                "can_read": True,
                "can_read_all": False,
                "can_create": True,
                "can_update": True,
                "can_update_all": False,
                "can_delete": True,
                "can_delete_all": False,
            }
        )

        Product.objects.get_or_create(
            name="Admin product",
            defaults={
                "description": "Owned by admin",
                "owner": admin_user,
            }
        )

        Product.objects.get_or_create(
            name="User product",
            defaults={
                "description": "Owned by user",
                "owner": regular_user,
            }
        )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully"))