from ninja import Router, Schema
from core.models.account import Account, AccountSchema
from core.utils.auth_backend import JWTAuth
from django.contrib.auth import authenticate, login as django_login
import jwt
from backend.settings import SECRET_KEY

router = Router(auth=JWTAuth())


@router.get("/me", response=AccountSchema)
def account_details(request):
    return request.auth


class LoginSchema(Schema):
    username: str
    password: str


@router.post("/login", auth=None)
def login(request, data: LoginSchema):
    user = authenticate(request, username=data.username, password=data.password)
    if not user:
        return {"error": "Invalid credentials"}
    django_login(request, user)

    token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")  #  type: ignore
    return {"token": token}


class RegisterRequest(Schema):
    username: str
    email: str
    password: str
    organization_id: int


@router.post("/register", response=AccountSchema, auth=None)
def register(request, data: RegisterRequest):
    account = Account.manager.create_account(
        username=data.username,
        email=data.email,
        password=data.password,
        organization_id=data.organization_id,
    )
    return account
