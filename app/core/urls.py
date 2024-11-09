from django.urls import path
from core.views import accounts
from ninja import NinjaAPI

api = NinjaAPI(csrf=True)


urlpatterns = [
    path("login/", accounts.LoginView.as_view(), name="login"),
    path("register/", accounts.RegisterView.as_view(), name="register"),
]
