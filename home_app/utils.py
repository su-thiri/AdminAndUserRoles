from django.contrib.auth.models import Group
from home_app.models import User, UserVerification
from django.utils.crypto import get_random_string
from rest_framework.request import Request


class InternalRegistration:
    def __init__(self, request: Request, validated_data={}):
        self.request: Request = request # TODO: sending email or something
        self.validated_data = validated_data
        self._registered_role = self.validated_data.pop("registered_role", None)

    def __create_user(self):
        self._user = User.objects.create(**self.validated_data)

    def __set_password(self):
        self._raw_password = get_random_string(length=16)
        self._user.set_password(raw_password=self._raw_password)
        self._user.save()

    def __set_group(self):
        self._user.groups.add(Group.objects.get(name=self._registered_role))

    def register_user(self):
        self.__create_user()
        self.__set_password()
        self.__set_group()
        self.user = self._user

    def make_verification(self):
        self.user_verification = UserVerification.objects.create(
            user=self.user,
            creator=self.request.user,
            registered_role=self._registered_role,
        )

    def decide_status(self):
        # self.user_verification.make_verified()
        self.user.make_active()

    @classmethod
    def init_from_verification(cls, request: Request, user_verification: UserVerification):
        instance = cls(request=request)
        instance._user = user_verification.user
        instance.__set_password()
        return instance
