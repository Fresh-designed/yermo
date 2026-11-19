from datetime import timedelta

from django import forms
from django.utils import timezone

from courses.models import Course

from .images import MAX_UPLOAD_BYTES, InvalidImage, normalize_image
from .models import Post

MAX_TAGS = 5
DAILY_POST_LIMIT = 30
TOO_LARGE = f"La foto pesa más de {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."


class PostForm(forms.ModelForm):
    photo = forms.FileField(
        label="Foto (opcional)",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
    )

    class Meta:
        model = Post
        fields = ("body", "courses")
        labels = {"body": "Mensaje"}
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Comparte un avance, una duda o un consejo…"}
            ),
            "courses": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, author, photo_too_large=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author
        # Lo marca `SizeLimitUploadHandler` cuando descarta el archivo a media subida.
        self.photo_too_large = photo_too_large
        self.fields["courses"].queryset = Course.objects.filter(is_published=True)

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if self.photo_too_large or (photo and photo.size > MAX_UPLOAD_BYTES):
            raise forms.ValidationError(TOO_LARGE)
        if not photo:
            return None
        try:
            return normalize_image(photo)
        except InvalidImage as error:
            raise forms.ValidationError(str(error))

    def clean_courses(self):
        courses = self.cleaned_data["courses"]
        if len(courses) > MAX_TAGS:
            raise forms.ValidationError(f"Puedes etiquetar {MAX_TAGS} cursos como máximo.")
        return courses

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        if not cleaned["body"].strip() and not cleaned["photo"]:
            raise forms.ValidationError("Escribe un mensaje o añade una foto.")
        since = timezone.now() - timedelta(days=1)
        if Post.objects.filter(author=self.author, created_at__gte=since).count() >= DAILY_POST_LIMIT:
            raise forms.ValidationError(
                f"Llegaste al límite de {DAILY_POST_LIMIT} publicaciones por día. Vuelve mañana."
            )
        return cleaned

    def save(self):
        post = super().save(commit=False)
        post.author = self.author
        if self.cleaned_data["photo"]:
            post.image, post.image_width, post.image_height = self.cleaned_data["photo"]
        post.save()
        self.save_m2m()
        return post
