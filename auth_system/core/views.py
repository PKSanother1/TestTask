from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import User, Role, BusinessElement, AccessRule, RefreshToken, BlacklistedToken, Product
from .utils import hash_password, check_password
from .auth import create_access_token, create_refresh_token, decode_token
from .permissions import check_permission, check_object_permission, get_rule
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    UpdateProfileSerializer,
    AccessRuleUpdateSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
)


@extend_schema(request=RegisterSerializer, summary="Регистрация пользователя")
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if data["password"] != data["password_confirm"]:
        return Response({"error": "password mismatch"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data["email"]).exists():
        return Response({"error": "email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    role, _ = Role.objects.get_or_create(name="user")

    User.objects.create(
        first_name=data["first_name"],
        last_name=data["last_name"],
        patronymic=data.get("patronymic"),
        email=data["email"],
        password=hash_password(data["password"]),
        role=role,
    )

    return Response({"message": "user created"}, status=status.HTTP_201_CREATED)


@extend_schema(request=LoginSerializer, summary="Логин пользователя")
@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = User.objects.filter(email=data["email"]).first()

    if not user or not check_password(data["password"], user.password):
        return Response({"error": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({"error": "user disabled"}, status=status.HTTP_403_FORBIDDEN)

    access_token = create_access_token(user.id)
    refresh_token, expires_at = create_refresh_token(user.id)

    RefreshToken.objects.create(
        user=user,
        token=refresh_token,
        expires_at=expires_at,
        is_revoked=False,
    )

    return Response(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        status=status.HTTP_200_OK
    )


@extend_schema(request=RefreshTokenSerializer, summary="Обновить access token")
@api_view(["POST"])
def refresh_access_token(request):
    serializer = RefreshTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    refresh_token = serializer.validated_data["refresh_token"]

    stored_token = RefreshToken.objects.filter(
        token=refresh_token,
        is_revoked=False
    ).first()

    if not stored_token:
        return Response({"error": "invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        payload = decode_token(refresh_token)
    except Exception:
        return Response({"error": "invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    if payload.get("type") != "refresh":
        return Response({"error": "invalid token type"}, status=status.HTTP_401_UNAUTHORIZED)

    if not stored_token.user.is_active:
        return Response({"error": "user disabled"}, status=status.HTTP_403_FORBIDDEN)

    access_token = create_access_token(stored_token.user.id)

    return Response({"access_token": access_token}, status=status.HTTP_200_OK)


@extend_schema(request=RefreshTokenSerializer, summary="Logout пользователя")
@api_view(["POST"])
def logout(request):
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]
        BlacklistedToken.objects.get_or_create(token=access_token)

    refresh_token = request.data.get("refresh_token")
    if refresh_token:
        stored_token = RefreshToken.objects.filter(token=refresh_token).first()
        if stored_token:
            stored_token.is_revoked = True
            stored_token.save()

    return Response({"message": "logout successful"}, status=status.HTTP_200_OK)


@extend_schema(request=UpdateProfileSerializer, summary="Обновление профиля")
@api_view(["PUT"])
def update_profile(request):
    user = request.user
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = UpdateProfileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.patronymic = data.get("patronymic", user.patronymic)
    user.save()

    return Response({"message": "updated"}, status=status.HTTP_200_OK)


@extend_schema(summary="Мягкое удаление пользователя")
@api_view(["DELETE"])
def delete_user(request):
    user = request.user
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    user.is_active = False
    user.save()

    return Response({"message": "user deactivated"}, status=status.HTTP_200_OK)


@extend_schema(summary="Список продуктов")
@api_view(["GET"])
def products(request):
    user = request.user

    if not user or not hasattr(user, "role"):
        return Response(
            {"error": "Unauthorized"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    rule = get_rule(user, "products")
    if not rule:
        return Response(
            {"error": "Forbidden"},
            status=status.HTTP_403_FORBIDDEN
        )

    if rule.can_read_all:
        qs = Product.objects.all()
    elif rule.can_read:
        qs = Product.objects.filter(owner=user)
    else:
        return Response(
            {"error": "Forbidden"},
            status=status.HTTP_403_FORBIDDEN
        )

    data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "owner_id": p.owner_id,
        }
        for p in qs
    ]

    return Response(data, status=status.HTTP_200_OK)


@extend_schema(request=ProductCreateSerializer, summary="Создать продукт")
@api_view(["POST"])
def create_product(request):
    user = request.user
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_permission(user, "products", "create"):
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProductCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    product = Product.objects.create(
        name=data["name"],
        description=data.get("description", ""),
        owner=user,
    )

    return Response(
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "owner_id": product.owner_id,
        },
        status=status.HTTP_201_CREATED
    )


@extend_schema(request=ProductUpdateSerializer, summary="Обновить продукт")
@api_view(["PUT"])
def update_product(request, product_id: int):
    user = request.user
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({"error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    if not check_object_permission(user, "products", "update", owner_id=product.owner_id):
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProductUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.save()

    return Response({"message": "product updated"}, status=status.HTTP_200_OK)


@extend_schema(summary="Удалить продукт")
@api_view(["DELETE"])
def delete_product(request, product_id: int):
    user = request.user
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({"error": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    if not check_object_permission(user, "products", "delete", owner_id=product.owner_id):
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    product.delete()
    return Response({"message": "product deleted"}, status=status.HTTP_200_OK)


@extend_schema(summary="Получить правила доступа (только admin)")
@api_view(["GET"])
def access_rules(request):
    user = request.user
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if user.role.name != "admin":
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    rules = AccessRule.objects.select_related("role", "element").all()

    result = [
        {
            "role": rule.role.name,
            "resource": rule.element.name,
            "can_read": rule.can_read,
            "can_read_all": rule.can_read_all,
            "can_create": rule.can_create,
            "can_update": rule.can_update,
            "can_update_all": rule.can_update_all,
            "can_delete": rule.can_delete,
            "can_delete_all": rule.can_delete_all,
        }
        for rule in rules
    ]

    return Response(result, status=status.HTTP_200_OK)


@extend_schema(request=AccessRuleUpdateSerializer, summary="Обновить правило доступа (только admin)")
@api_view(["POST"])
def update_access_rule(request):
    user = request.user
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if user.role.name != "admin":
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    serializer = AccessRuleUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    role = Role.objects.filter(name=data["role"]).first()
    if not role:
        return Response({"error": "role not found"}, status=status.HTTP_400_BAD_REQUEST)

    resource = BusinessElement.objects.filter(name=data["resource"]).first()
    if not resource:
        return Response({"error": "resource not found"}, status=status.HTTP_400_BAD_REQUEST)

    rule, _ = AccessRule.objects.get_or_create(role=role, element=resource)

    for field in [
        "can_read",
        "can_read_all",
        "can_create",
        "can_update",
        "can_update_all",
        "can_delete",
        "can_delete_all",
    ]:
        if field in data:
            setattr(rule, field, data[field])

    rule.save()

    return Response({"message": "rule updated"}, status=status.HTTP_200_OK)