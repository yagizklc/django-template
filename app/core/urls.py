from django.urls import path
from app.core.views import accounts

urlpatterns = [
    path("me/", accounts.MeView.as_view(), name="me"),
]
