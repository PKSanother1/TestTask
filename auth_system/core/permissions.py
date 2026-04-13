from .models import AccessRule


def get_rule(user, resource: str):
    if not user:
        return None

    return AccessRule.objects.filter(
        role=user.role,
        element__name=resource
    ).first()


def check_permission(user, resource: str, action: str) -> bool:
    rule = get_rule(user, resource)
    if not rule:
        return False

    field_name = f"can_{action}"
    return getattr(rule, field_name, False)


def check_object_permission(user, resource: str, action: str, owner_id: int | None = None) -> bool:
    rule = get_rule(user, resource)
    if not rule:
        return False

    if action == "read":
        if rule.can_read_all:
            return True
        if rule.can_read and owner_id == user.id:
            return True

    elif action == "update":
        if rule.can_update_all:
            return True
        if rule.can_update and owner_id == user.id:
            return True

    elif action == "delete":
        if rule.can_delete_all:
            return True
        if rule.can_delete and owner_id == user.id:
            return True

    elif action == "create":
        return rule.can_create

    return False