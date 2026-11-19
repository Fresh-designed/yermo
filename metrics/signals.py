from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import ActivityEvent

Kind = ActivityEvent.Kind


@receiver(user_logged_in)
def record_login(sender, request, user, **kwargs):
    ActivityEvent.record(Kind.LOGIN, user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def record_register(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        ActivityEvent.record(Kind.REGISTER, instance)


@receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
def record_delete(sender, instance, **kwargs):
    # Sin FK al usuario: va a desaparecer y solo queda el nombre.
    ActivityEvent.objects.create(kind=Kind.DELETE, username=instance.get_username())
