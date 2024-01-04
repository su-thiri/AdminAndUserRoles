from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)


from core.permissions import IsSystemAdmin
from .models import UserVerification
from .serializers import RegisterSerializer, SetNewPasswordSerializer

# from .permissions import IsNotAuthenticated


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [IsSystemAdmin]
    action_serializers = {
        "set_new_password": SetNewPasswordSerializer,
    }
    queryset = UserVerification.objects.all()

    def get_serializer_class(self):
        """
        Returns a specific serializer for certain acitons
        """
        if hasattr(self, "action_serializers"):
            return self.action_serializers.get(self.action, self.serializer_class)

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """
        Create a new user and user verification record
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            internal_registration = serializer.save()
            return Response(
                {
                    "message": "User created successfully.",
                    "data": {
                        "user_email": internal_registration.user.email,
                        "user_password": internal_registration._raw_password,
                        "user_role": internal_registration._registered_role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["post"],
        url_path="set-new-password",
        name=_("Set a new password for a user"),
    )
    def set_new_password(self, request, *args, **kwargs):
        """
        Let an admin to set new auto-generated password on unmodified account.
        Synonym: user and/or admin lost the password before the first login.
        """

        serializer = self.get_serializer(data=request.data, many=False)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RFQOSTObtainPairView(TokenObtainPairView):
    throttle_scope = "token_obtain_pair"
    throttle_classes = [ScopedRateThrottle]
    permission_classes = [AllowAny]


class RFQOSTokenBlacklistView(TokenBlacklistView):
    throttle_scope = "token_blacklist"
    throttle_classes = [ScopedRateThrottle]
    permission_classes = [AllowAny]


class RFQOSTokenRefreshView(TokenRefreshView):
    throttle_scope = "token_refresh"
    throttle_classes = [ScopedRateThrottle]
    permission_classes = [AllowAny]


class RFQOSTokenVerifyView(TokenVerifyView):
    throttle_scope = "token_verify"
    throttle_classes = [ScopedRateThrottle]
    permission_classes = [AllowAny]
