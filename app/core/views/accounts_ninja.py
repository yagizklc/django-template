from ninja import Router
from core.models.account import Account
from core.utils.auth_backend import JWTAuth
from ninja import ModelSchema

router = Router(auth=JWTAuth())


class AccountSchema(ModelSchema):
    class Meta:
        model = Account
        fields = "__all__"


@router.get("/me2", response=AccountSchema)
def user_info(request):
    print("request.user", request.user)
    return request.auth
