from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from app.core.utils.exception_handeling import handle_exceptions


@handle_exceptions
@method_decorator(csrf_exempt, name="dispatch")
class MeView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        
        return JsonResponse({"message": "Hello World"}, status=200)
