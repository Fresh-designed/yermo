from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from courses.models import Course

from .forms import PostForm
from .models import Post

PAGE_SIZE = 10


@login_required
def feed(request):
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        author=request.user,
        photo_too_large=getattr(request, "upload_too_large", False),
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tu publicación ya está en el blog.")
        return redirect("blog:feed")

    published = Course.objects.filter(is_published=True)
    # Sin la columna de la foto: cada imagen se pide aparte, en `photo`.
    posts = (
        Post.objects.defer("image")
        .select_related("author")
        .prefetch_related(Prefetch("courses", queryset=published))
    )
    course = None
    if request.GET.get("curso"):
        course = get_object_or_404(published, slug=request.GET["curso"])
        posts = posts.filter(courses=course)

    return render(
        request,
        "blog/feed.html",
        {
            "form": form,
            "page": Paginator(posts, PAGE_SIZE).get_page(request.GET.get("pagina")),
            "course": course,
        },
    )


@login_required
def photo(request, post_id):
    post = get_object_or_404(Post.objects.only("image"), pk=post_id)
    if post.image is None:
        raise Http404
    response = HttpResponse(bytes(post.image), content_type="image/jpeg")
    # Una publicación no se edita, así que su foto nunca cambia.
    response["Cache-Control"] = "private, max-age=31536000, immutable"
    return response


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post.objects.defer("image"), pk=post_id)
    if post.author_id != request.user.pk and not request.user.is_staff:
        raise PermissionDenied
    post.delete()
    messages.success(request, "Se eliminó la publicación.")
    return redirect("blog:feed")
