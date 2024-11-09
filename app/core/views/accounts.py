import json
from dataclasses import dataclass
from typing import TypedDict

from django.shortcuts import get_object_or_404
import jwt
import logfire
from backend.settings import SECRET_KEY
from core.models.account import Account
from core.utils.exception_handeling import good
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.http import HttpRequest, JsonResponse
from django.views import View


class UserData(TypedDict):
    id: str
    email: str
    organization: str


@dataclass
class LoginRequest:
    username: str
    password: str

    @classmethod
    def from_request(cls, request_body: bytes) -> "LoginRequest":
        data = json.loads(request_body)
        if not all(field in data for field in ["username", "password"]):
            raise ValidationError("Missing required fields: username, password")
        return cls(username=data["username"], password=data["password"])


@dataclass
class RegisterRequest:
    username: str
    password: str
    email: str
    organization_id: int

    @classmethod
    def from_request(cls, request_body: bytes) -> "RegisterRequest":
        data = json.loads(request_body)
        required_fields = ["username", "password", "email", "organization_id"]
        if not all(field in data for field in required_fields):
            raise ValidationError(
                f"Missing required fields: {', '.join(required_fields)}"
            )
        return cls(
            username=data["username"],
            password=data["password"],
            email=data["email"],
            organization_id=data["organization_id"],
        )


@good
class LoginView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        """Return user information based on JWT token."""
        authorization = request.headers.get("Authorization", "")
        if not authorization or len(authorization.split()) != 2:
            raise ValidationError("Invalid Authorization header")

        # authenticate using token
        # checkout utils/auth_backend.py for implementation
        token = authorization.split()[1]
        user = authenticate(token=token)
        if not user:
            raise ValidationError("Invalid token")

        account = get_object_or_404(Account, user=user)
        user_data: UserData = {
            "id": user.username,
            "email": user.email,
            "organization": account.organization.name,
        }

        logfire.info("User {user} accessed their account", user=user)

        return JsonResponse(user_data)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Authenticate user and return JWT token."""
        login_data = LoginRequest.from_request(request.body)

        # authenticate using username and password
        user = authenticate(username=login_data.username, password=login_data.password)
        if not user:
            raise ValidationError("Invalid credentials")

        token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")  #  type: ignore
        return JsonResponse({"token": token}, status=201)


@good
class RegisterView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        """Create new user account."""
        register_data = RegisterRequest.from_request(request.body)

        account = Account.manager.create_account(
            username=register_data.username,
            email=register_data.email,
            password=register_data.password,
            organization_id=register_data.organization_id,
        )

        return JsonResponse(
            {"message": f"Account created with ID: {account.id}"}, status=201
        )
