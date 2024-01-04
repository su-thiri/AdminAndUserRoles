from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserInformation
from guardian.shortcuts import assign_perm


@receiver(post_save, sender=User)
def create_user_infromation_post(sender, instance, created, **kwargs):
    has_information_attr = hasattr(instance, "information")
    is_superuser = instance.is_superuser and instance.is_staff

    if created:
        if not has_information_attr and not is_superuser:
            user_info = UserInformation.objects.create(
                user=instance,
                about="",
            )
            assign_perm("home_app.change_user", instance, instance)
            assign_perm("home_app.change_userinformation", instance, user_info)
