from ninja import NinjaAPI
from core.views.accounts_ninja import router as core_router

api = NinjaAPI()


@api.get("/me")
def user_info(request):
    print(request.auth)
    return {"message": "Hello, world!"}


api.add_router("/core", core_router)
