from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class User(AbstractUser):
    """Usuario de Yermo. Es administrador quien tiene `is_staff` activo."""

    email = models.EmailField("correo", unique=True)

    class Meta(AbstractUser.Meta):
        constraints = [
            models.UniqueConstraint(Lower("email"), name="unique_lower_email"),
            models.UniqueConstraint(Lower("username"), name="unique_lower_username"),
        ]

    @property
    def role_label(self):
        return "Administrador" if self.is_staff else "Ordinario"
