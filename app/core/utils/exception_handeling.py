import json
from functools import wraps
from typing import Any, Dict, Type
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.http import Http404
from django.core.exceptions import ValidationError
from django.views import View
from django.contrib.auth import authenticate
from core.models.account import Account
from django.shortcuts import get_object_or_404


def good(view_class: Type[View]) -> Type[View]:
    """
    Class decorator to handle exceptions and return a JSON response for all view methods.
    """
    original_dispatch = view_class.dispatch
    assert issubclass(view_class, View), "Class must be a subclass of View."

    @wraps(original_dispatch)
    def new_dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
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

            data: Dict[str, Any] = json.loads(request.body)

            return original_dispatch(
                self, request, *args, **kwargs, account=account, data=data
            )
        except (AssertionError, ValueError, json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Http404 as e:
            return JsonResponse({"error": str(e)}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    view_class.dispatch = new_dispatch
    return view_class
