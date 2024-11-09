from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http.request import HttpRequest
import jwt

from backend.settings import SECRET_KEY

from django.shortcuts import get_object_or_404
from ninja.security import HttpBearer
from django.contrib.auth import authenticate as django_authenticate
from core.models.account import Account



class JWTAuthenticationBackend(BaseBackend):
    """
    JWT Authentication Backend

    https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#writing-an-authentication-backend
    """

    def authenticate(
        self,
        request: HttpRequest,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        **kwargs,
    ) -> User | None:
        if not token:
            return None

        user_data = jwt.decode(token, SECRET_KEY, ["HS256"])
        if "user_id" not in user_data:
            return None

        user_id = user_data["user_id"]
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id: int) -> User | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class JWTAuth(HttpBearer):
    """ JWT Auth for Django-Ninja """
    def authenticate(self, request, token: str):
        user = django_authenticate(token=token)
        if not user:
            return None

        return get_object_or_404(Account, user=user)
