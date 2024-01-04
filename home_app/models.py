from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition

# from guardian.models import UserObjectPermissionBase
# from guardian.models import GroupObjectPermissionBase


class UserVerification(models.Model):
    """User Verification Table"""

    REGISTERED_ROLE = [
        ("sale_admin", "SALE ADMIN"),
        ("salesperson", "SALESPERSON"),
    ]

    VERIFICATION_STATUSES = [
        ("unverified", "unverified"),
        ("verified", "verified"),
        ("revoked", "revoked"),
        ("failed", "failed"),
    ]

    key = models.UUIDField(
        primary_key=True, max_length=32, default=uuid4, editable=False
    )
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="verification"
    )
    creator = models.ForeignKey("User", on_delete=models.DO_NOTHING)
    registered_role = models.CharField(
        max_length=11, choices=REGISTERED_ROLE, verbose_name="Registered Role"
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created Time")
    updated = models.DateTimeField(auto_now=True, verbose_name="Updated Time")
    status = FSMField(
        default="unverified",
        choices=VERIFICATION_STATUSES,
        verbose_name="Verification Status",
    )

    class Meta:
        ordering = ("-pk",)

    @transition(
        field=status,
        source="unverified",
        target="verified",
        permission=lambda instance, user: instance.user == user,
    )
    def trans_verified(self):
        pass

    @transition(
        field=status,
        source=["unverified", "verified"],  # type: ignore
        target="revoked",
        permission=lambda instance, user: instance.creator == user,
    )
    def trans_revoked(self):
        pass

    @transition(
        field=status,
        source="unverified",
        target="failed",
        permission=lambda instance, user: instance.creator == user,
    )
    def trans_failed(self):
        pass

    def make_verified(self):
        # as protected set to `False`
        # and allow transit from `unverified` to `verified`,
        self.trans_verified()
        self.save()

    def is_valid(self):
        """TODO: Check expiry time or something"""
        return True


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError(_("You must register with a valid email address."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_staff(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User Table"""

    email = models.EmailField(unique=True, verbose_name="User Email")
    is_active = models.BooleanField(
        default=False,
        verbose_name="User Active Status",
        help_text=_("Designates whether the user can log in."),
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Marked as Deleted",
        help_text=_("Designates whether the user marked as deleted."),
    )
    is_modified = models.BooleanField(
        default=False,
        verbose_name="Marked as Modified",
        help_text=_("Designates whether the user modified the account."),
    )
    username = None
    user_permissions = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def make_active(self):
        self.is_active = True
        self.save()

    class Meta:
        ordering = ("-pk",)

class UserInformation(models.Model):
    """User Information Table"""

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name="information")
    about = models.TextField(blank=True, verbose_name="About")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created Time")
    updated = models.DateTimeField(auto_now=True, verbose_name="Updated Time")

    class Meta:
        ordering = ("-pk",)
