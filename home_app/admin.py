from django.contrib import admin
from .models import User


class UserGroupInline(admin.TabularInline):
    model = User.groups.through


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("email",)
    list_display_links = ("email",)
    fields = (
        ("email",),
        ("first_name", "last_name"),
        ("is_staff", "is_active", "is_superuser"),
        ("date_joined", "last_login"),
    )
    inlines = [
        UserGroupInline,
    ]
    search_fields = ["email"]
    readonly_fields = ("date_joined", "last_login")


admin.site.register(User, UserAdmin)
