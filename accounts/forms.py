import hmac

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o correo",
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "Usuario, correo o contraseña incorrectos.",
        "inactive": "Esta cuenta está desactivada.",
    }


class RegisterForm(UserCreationForm):
    """Registro público. Sin el código correcto, la cuenta siempre es ordinaria."""

    admin_code = forms.CharField(
        label="Código de administrador (opcional)",
        required=False,
        strip=True,
        widget=forms.PasswordInput(attrs={"autocomplete": "off"}),
        help_text="Déjalo vacío para crear una cuenta ordinaria.",
    )

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {"username": "Usuario", "email": "Correo"}
        help_texts = {"username": ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["autofocus"] = True
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Repite la contraseña"
        self.fields["password1"].help_text = "Mínimo 8 caracteres, y no solo números."
        self.fields["password2"].help_text = ""

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya hay una cuenta con ese correo.")
        return email

    def clean_admin_code(self):
        code = self.cleaned_data["admin_code"]
        if not code:
            return ""
        expected = settings.ADMIN_REGISTRATION_CODE
        if not expected or not hmac.compare_digest(code.encode(), expected.encode()):
            raise forms.ValidationError("El código de administrador no es válido.")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("admin_code"):
            # is_superuser da acceso completo a /admin/, donde se cargan los cursos.
            user.is_staff = True
            user.is_superuser = True
        if commit:
            user.save()
        return user
