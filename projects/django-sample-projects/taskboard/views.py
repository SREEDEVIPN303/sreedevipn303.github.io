import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Task


def _body(request):
    try:
        data = json.loads(request.body or b"{}")
        return data if isinstance(data, dict) else None
    except ValueError:
        return None


def _validate(data, partial=False):
    """Return (cleaned, errors). Only whitelisted fields are accepted."""
    cleaned, errors = {}, {}
    if "title" in data or not partial:
        title = str(data.get("title", "")).strip()
        if not title or len(title) > 120:
            errors["title"] = "Required, max 120 characters"
        else:
            cleaned["title"] = title
    if "description" in data:
        cleaned["description"] = str(data["description"])
    if "status" in data:
        if data["status"] not in Task.Status.values:
            errors["status"] = f"Must be one of {Task.Status.values}"
        else:
            cleaned["status"] = data["status"]
    if "priority" in data:
        if data["priority"] not in Task.Priority.values:
            errors["priority"] = f"Must be one of {Task.Priority.values}"
        else:
            cleaned["priority"] = data["priority"]
    return cleaned, errors


@ensure_csrf_cookie
def board(request):
    return render(request, "taskboard/board.html")


@require_http_methods(["GET", "POST"])
def task_collection(request):
    if request.method == "GET":
        qs = Task.objects.all()
        status = request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return JsonResponse({"tasks": [t.as_dict() for t in qs]})

    data = _body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    cleaned, errors = _validate(data)
    if errors:
        return JsonResponse({"errors": errors}, status=400)
    return JsonResponse(Task.objects.create(**cleaned).as_dict(), status=201)


@require_http_methods(["GET", "PATCH", "DELETE"])
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "GET":
        return JsonResponse(task.as_dict())
    if request.method == "DELETE":
        task.delete()
        return JsonResponse({}, status=204)

    data = _body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    cleaned, errors = _validate(data, partial=True)
    if errors:
        return JsonResponse({"errors": errors}, status=400)
    for k, v in cleaned.items():
        setattr(task, k, v)
    task.save()
    return JsonResponse(task.as_dict())
