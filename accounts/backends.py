from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class UsernameOrEmailBackend(ModelBackend):
    """Permite entrar con el nombre de usuario o con el correo."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None
        user = User.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username)
        ).first()
        if user is None:
            # Igual que ModelBackend: gasta el mismo tiempo que una contraseña real.
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
