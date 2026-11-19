from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from surveys.models import SurveyResponse

from .models import Course, Enrollment, Video, WatchedVideo, progress_percent

# Valor de «?tipo=» en el catálogo → tipo de curso.
KIND_FILTERS = {"video": Course.Kind.VIDEO, "escrito": Course.Kind.WRITTEN}


@login_required
def home(request):
    return redirect("courses:my_courses")


def _published_courses():
    return Course.objects.filter(is_published=True)


@login_required
def catalog(request):
    kind = request.GET.get("tipo", "")
    courses = _published_courses()
    if kind in KIND_FILTERS:
        courses = courses.filter(kind=KIND_FILTERS[kind])
    else:
        kind = ""
    courses = courses.annotate(
        video_total=Count("videos"),
        enrolled=Exists(Enrollment.objects.filter(user=request.user, course=OuterRef("pk"))),
    )
    return render(request, "courses/catalog.html", {"courses": courses, "kind": kind})


@login_required
def my_courses(request):
    enrollments = (
        Enrollment.objects.filter(user=request.user, course__is_published=True)
        .select_related("course")
        .annotate(
            video_total=Count("course__videos", distinct=True),
            video_watched=Count(
                "course__videos",
                filter=Q(course__videos__watched_by__user=request.user),
                distinct=True,
            ),
        )
    )
    for enrollment in enrollments:
        enrollment.percent = progress_percent(enrollment.video_watched, enrollment.video_total)
    return render(
        request,
        "courses/my_courses.html",
        {
            "enrollments": enrollments,
            "survey_pending": not SurveyResponse.objects.filter(user=request.user).exists(),
        },
    )


@login_required
def detail(request, slug, video_id=None):
    course = get_object_or_404(_published_courses(), slug=slug)
    enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    videos = list(
        course.videos.annotate(
            watched=Exists(WatchedVideo.objects.filter(user=request.user, video=OuterRef("pk")))
        )
    )
    watched_count = sum(video.watched for video in videos)

    current = None
    if enrolled and videos:
        if video_id is not None:
            current = next((v for v in videos if v.pk == video_id), None)
            if current is None:
                return redirect(course)
        else:
            # Sin lección elegida, abre la primera pendiente.
            current = next((v for v in videos if not v.watched), videos[0])
    elif video_id is not None:
        messages.warning(request, "Suscríbete al curso para ver sus lecciones.")
        return redirect(course)

    next_video = None
    if current is not None:
        following = videos[videos.index(current) + 1 :]
        next_video = following[0] if following else None

    return render(
        request,
        "courses/detail.html",
        {
            "course": course,
            "enrolled": enrolled,
            "videos": videos,
            "current": current,
            "next_video": next_video,
            "watched_count": watched_count,
            "lesson_total": len(videos),
            "percent": progress_percent(watched_count, len(videos)),
            "post_total": course.posts.count(),
        },
    )


@login_required
@require_POST
def enroll(request, slug):
    course = get_object_or_404(_published_courses(), slug=slug)
    _, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        messages.success(request, f"Te suscribiste a «{course.title}».")
    return redirect(course)


@login_required
@require_POST
def unenroll(request, slug):
    course = get_object_or_404(Course, slug=slug)
    Enrollment.objects.filter(user=request.user, course=course).delete()
    messages.info(request, f"Cancelaste tu suscripción a «{course.title}». Tu avance se conserva.")
    return redirect("courses:my_courses")


@login_required
@require_POST
def set_watched(request, video_id):
    """Marca o desmarca una lección como completada. Solo para quien está suscrito al curso."""
    video = get_object_or_404(Video.objects.select_related("course"), pk=video_id)
    if not Enrollment.objects.filter(user=request.user, course=video.course).exists():
        messages.warning(request, "Suscríbete al curso para registrar tu avance.")
        return redirect(video.course)

    if request.POST.get("watched", "1") == "1":
        WatchedVideo.objects.get_or_create(user=request.user, video=video)
    else:
        WatchedVideo.objects.filter(user=request.user, video=video).delete()

    next_id = request.POST.get("next_video")
    if next_id and next_id.isdigit() and video.course.videos.filter(pk=next_id).exists():
        return redirect("courses:watch", slug=video.course.slug, video_id=int(next_id))
    return redirect("courses:watch", slug=video.course.slug, video_id=video.pk)
