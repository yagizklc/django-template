from typing import Any, Dict, List
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from core.utils.exception_handler import handle_exceptions
from django.contrib.auth.models import User


@handle_exceptions
@method_decorator(csrf_exempt, name="dispatch")
class InviteTokenView(View):
    email_manager = EmailManager()

    @get_auth
    def get(self, request: HttpRequest, auth: Authentication) -> JsonResponse:
        """List all invitations created by the user"""

        invite_tokens = InviteToken.objects.filter(created_by=auth)
        response = [
            self._format_invitation(invite_token) for invite_token in invite_tokens
        ]
        return JsonResponse(data=response, status=200, safe=False)

    def _format_invitation(self, invite_token: InviteToken) -> Dict[str, Any]:
        status = "expired"
        if User.objects.filter(email=invite_token.email).exists():
            status = "accepted"
        elif invite_token.is_valid():
            status = "pending"

        return {
            "email": invite_token.email,
            "same_org": invite_token.to_my_organization,
            "status": status,
        }

    @get_auth
    def post(self, request: HttpRequest, auth: Authentication) -> JsonResponse:
        data: Dict[str, Any] = json.loads(request.body)
        created_by = auth

        email = data.get("email")
        assert email, "Email is required"

        email_context = {}

        session_uuid = data.get("session_uuid")
        existing_user = User.objects.filter(email=email).first()
        assert (
            not existing_user or session_uuid
        ), "Session UUID is required for existing users"

        if existing_user:
            assert session_uuid, "Session UUID is required for existing users"
            session = get_object_or_404(UploadSession, uuid=session_uuid)
            session.share(
                by=created_by.user,
                to=existing_user,
                description=data.get("description", "Empty description"),
            )
            email_context = {
                "session_name": session.name,
                "session_url": f"{LOGIN_REDIRECT_URL}/sessions/{session_uuid}/",
                "invited_by_name": created_by.user.get_full_name(),
                "invited_by_email": created_by.user.email,
                "invite_token": "",
            }
        else:
            to_my_organization = data.get("to_my_organization", False)
            if not to_my_organization:
                assert session_uuid, "Session UUID is required for non-org invites"
                get_object_or_404(UploadSession, uuid=session_uuid)

            invite_token = InviteToken().create_token(
                email=email,
                duration_days=data.get("duration_days", 7),
                to_my_organization=to_my_organization,
                created_by=created_by,
                options=session_uuid if session_uuid else "",
            )
            email_context = {
                "session_name": created_by.organization.name,
                "session_url": f"{AREAL__SERVER_URL}/api/v1/register/?invite_token={invite_token.token}",
                "invited_by_email": created_by.user.email,
                "invited_by_name": created_by.user.get_full_name(),
                "invite_token": invite_token.token,
            }

        self.email_manager.send_email(
            to=[email],
            subject="Areal Invitation",
            template_name="dev-invitation3",
            body=email_context,
        )

        return JsonResponse({"message": email_context}, status=201)


@handle_exceptions
@method_decorator(csrf_exempt, name="dispatch")
class AccessToSessionView(View):
    """Manages access to sessions"""

    def get(self, request: HttpRequest) -> JsonResponse:
        """list all users who have access to a session"""

        session_id = request.GET.get("session_id")
        assert session_id, "Session ID is required"

        session = get_object_or_404(UploadSession, uuid=session_id)
        access = self.__format_user(
            [
                auth.user
                for auth in Authentication.objects.filter(
                    organization=session.organization
                )
            ],
            same_org=True,
        )
        access_via_share = self.__format_user(
            users=[  # type: ignore
                auth.shared_to
                for auth in SharedSession.objects.filter(upload_session=session)
            ],
            same_org=False,
        )
        access.extend(access_via_share)
        return JsonResponse(access, status=200, safe=False)

    def __format_user(self, users: List[User], same_org: bool) -> List[Dict[str, str]]:
        return [
            {
                "id": user.id,  # type: ignore
                "username": user.username,
                "fullname": user.get_full_name(),
                "email": user.email,
                "same_org": same_org,
            }
            for user in users
            if user.is_active
        ]
