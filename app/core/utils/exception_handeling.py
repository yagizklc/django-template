import json
from functools import wraps
from typing import  List,  Type
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.http import Http404
from django.core.exceptions import ValidationError
from django.views import View



def handle_exceptions(view_class: Type[View]) -> Type[View]:
    """
    Class decorator to handle exceptions and return a JSON response for all view methods.
    """
    original_dispatch = view_class.dispatch

    @wraps(original_dispatch)
    def new_dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            return original_dispatch(self, request, *args, **kwargs)
        except (AssertionError, ValueError, json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Http404 as e:
            return JsonResponse({"error": str(e)}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    view_class.dispatch = new_dispatch
    return view_class

