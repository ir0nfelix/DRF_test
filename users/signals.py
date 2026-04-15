from django.dispatch import receiver
from djoser.signals import user_registered

@receiver(user_registered)
def djoser_user_registered_handler(sender, user, request, **kwargs):
    user.is_superuser = True
    user.is_staff = True
    user.save(update_fields=['is_superuser', 'is_staff'])
