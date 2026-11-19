from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from surveys.stats import survey_summary

from .charts import build_flow_chart
from .models import ActivityEvent

User = get_user_model()

Kind = ActivityEvent.Kind
RANGES = (7, 14, 30)
DEFAULT_RANGE = 14


def admin_required(view):
    """Sin sesión lleva al login; con sesión de usuario ordinario responde 403."""

    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


def _daily_flow(days):
    """Una fila por día, también los días sin actividad."""
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    rows = (
        ActivityEvent.objects.filter(created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            active=Count("username", filter=Q(kind=Kind.VISIT), distinct=True),
            logins=Count("id", filter=Q(kind=Kind.LOGIN)),
            registers=Count("id", filter=Q(kind=Kind.REGISTER)),
            deletes=Count("id", filter=Q(kind=Kind.DELETE)),
        )
    )
    by_day = {row["day"]: row for row in rows}
    empty = {"active": 0, "logins": 0, "registers": 0, "deletes": 0}
    return [
        {"day": day, **{key: by_day.get(day, empty)[key] for key in empty}}
        for day in (start + timedelta(days=offset) for offset in range(days))
    ]


@admin_required
def dashboard(request):
    try:
        days = int(request.GET.get("dias", DEFAULT_RANGE))
    except ValueError:
        days = DEFAULT_RANGE
    if days not in RANGES:
        days = DEFAULT_RANGE

    flow = _daily_flow(days)
    query = request.GET.get("q", "").strip()
    users = User.objects.annotate(enrollment_total=Count("enrollments")).order_by("-date_joined")
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    page = Paginator(users, 15).get_page(request.GET.get("pagina"))

    context = {
        "total_users": User.objects.count(),
        "admin_users": User.objects.filter(is_staff=True).count(),
        "ordinary_users": User.objects.filter(is_staff=False).count(),
        "period_registers": sum(row["registers"] for row in flow),
        "period_logins": sum(row["logins"] for row in flow),
        "period_deletes": sum(row["deletes"] for row in flow),
        "all_deletes": ActivityEvent.objects.filter(kind=Kind.DELETE).count(),
        "today_active": flow[-1]["active"],
        "days": days,
        "ranges": RANGES,
        "flow": flow,
        "chart": build_flow_chart(flow),
        "page": page,
        "query": query,
        "recent_deletes": ActivityEvent.objects.filter(kind=Kind.DELETE)[:8],
        "survey": survey_summary(),
    }
    return render(request, "metrics/dashboard.html", context)


@admin_required
def delete_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)

    if target.pk == request.user.pk:
        messages.error(request, "No puedes eliminar tu propia cuenta desde aquí.")
        return redirect("metrics:dashboard")

    if request.method == "POST":
        username = target.username
        target.delete()
        messages.success(request, f"Se eliminó la cuenta de {username}.")
        return redirect("metrics:dashboard")

    return render(request, "metrics/confirm_delete.html", {"target": target})
