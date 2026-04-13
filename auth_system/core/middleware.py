from .auth import decode_token
from .models import User, BlacklistedToken


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = None

        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            if BlacklistedToken.objects.filter(token=token).exists():
                return self.get_response(request)

            try:
                payload = decode_token(token)

                if payload.get("type") != "access":
                    return self.get_response(request)

                user = User.objects.filter(
                    id=payload["user_id"],
                    is_active=True
                ).first()

                request.user = user
            except Exception:
                request.user = None

        return self.get_response(request)