from django.utils import timezone

from .models import ActivityEvent

SESSION_KEY = "metrics_last_visit"


class DailyVisitMiddleware:
    """Anota una visita por usuario y día; así cuenta también quien ya tenía sesión abierta."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            today = timezone.localdate().isoformat()
            if request.session.get(SESSION_KEY) != today:
                request.session[SESSION_KEY] = today
                ActivityEvent.record(ActivityEvent.Kind.VISIT, user)
        return response
