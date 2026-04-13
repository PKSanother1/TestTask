from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    patronymic = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField()
    password_confirm = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    patronymic = serializers.CharField(required=False, allow_blank=True)


class AccessRuleUpdateSerializer(serializers.Serializer):
    role = serializers.CharField()
    resource = serializers.CharField()
    can_read = serializers.BooleanField(required=False)
    can_read_all = serializers.BooleanField(required=False)
    can_create = serializers.BooleanField(required=False)
    can_update = serializers.BooleanField(required=False)
    can_update_all = serializers.BooleanField(required=False)
    can_delete = serializers.BooleanField(required=False)
    can_delete_all = serializers.BooleanField(required=False)


class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)


class ProductUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)