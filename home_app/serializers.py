# from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserVerification, User
from .utils import InternalRegistration


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(label="First Name")
    last_name = serializers.CharField(label="Last Name")
    email = serializers.EmailField(
        # if user is not active, then validation will pass
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Already registered. Please login or verify.",
            )
        ]
    )
    # Sale Admin or Salesperson choice
    registered_role = serializers.ChoiceField(
        initial="salesperson",
        choices=UserVerification.REGISTERED_ROLE,
        label="Registered Role",
    )

    class Meta:
        model = UserVerification
        fields = [
            "first_name",
            "last_name",
            "email",
            "registered_role",
        ]

    def validate(self, data):
        # None if valid otherwise raises ValidationError
        # settings.AUTH_PASSWORD_VALIDATORS
        # validate_password(data["password"], user=None)
        return data

    def create(self, validated_data):
        request: Request = self.context.get("request")  # type: ignore
        # LOGGING:
        print(f"Signup requested: {request.META.get('REMOTE_ADDR', 'Unknown IP')}")

        try:
            internal_registration = InternalRegistration(
                request=request, validated_data=validated_data
            )
            internal_registration.register_user()
            internal_registration.make_verification()
            internal_registration.decide_status()

            return internal_registration

        except Exception as e:
            raise serializers.ValidationError(e)


class SetNewPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        # if user is not active, then validation will pass
        validators=[
            UniqueValidator(
                queryset=User.objects.filter(is_modified=True),
                message="Already registered. Please login or verify.",
            )
        ]
    )

    class Meta:
        model = UserVerification
        fields = [
            "email",
        ]

    def validate(self, data):
        request: Request = self.context.get("request")  # type: ignore
        # LOGGING:
        print(
            f"Forgot password requested: {request.META.get('REMOTE_ADDR', 'Unknown IP')}"
        )

        user_verification = get_object_or_404(
            UserVerification, user__email=data["email"], user__is_modified=False
        )
        if user_verification.is_valid():
            internal_registration = InternalRegistration.init_from_verification(
                request=request, user_verification=user_verification
            )
            data["new_password"] = internal_registration._raw_password
            data["registered_role"] = user_verification.registered_role
            return data

        raise ValidationError({"detail": "The verification is expired."})


class RFQOSTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)

        # Add custom claims
        token["user_email"] = user.email
        token["user_groups"] = [i.name for i in user.groups.all()]

        return token
