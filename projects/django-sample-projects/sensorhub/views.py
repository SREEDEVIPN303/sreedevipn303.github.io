import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import Reading, Sensor


def _reading_json(r):
    return {"value": r.value, "recorded_at": r.recorded_at.isoformat(), "alert": r.is_alert}


@require_GET
def dashboard(request):
    return render(request, "sensorhub/dashboard.html")


@require_GET
def sensor_list(request):
    data = []
    for s in Sensor.objects.filter(active=True):
        latest = s.readings.first()
        data.append({
            "id": s.id,
            "name": s.name,
            "location": s.location,
            "unit": s.unit,
            "threshold": s.threshold,
            "latest": _reading_json(latest) if latest else None,
        })
    return JsonResponse({"sensors": data})


@csrf_exempt  # devices authenticate with an API key instead of a browser session
@require_http_methods(["GET", "POST"])
def sensor_readings(request, sensor_id):
    sensor = get_object_or_404(Sensor, pk=sensor_id, active=True)

    if request.method == "GET":
        try:
            limit = max(1, min(int(request.GET.get("limit", 30)), 200))
        except ValueError:
            return JsonResponse({"error": "limit must be an integer"}, status=400)
        rows = list(sensor.readings.select_related("sensor")[:limit])
        rows.reverse()  # oldest first for charting
        return JsonResponse({"sensor": sensor.name, "unit": sensor.unit,
                             "threshold": sensor.threshold,
                             "readings": [_reading_json(r) for r in rows]})

    # POST: a device pushes a new reading
    if request.headers.get("X-API-Key") != settings.DEVICE_API_KEY:
        return JsonResponse({"error": "invalid or missing API key"}, status=401)
    try:
        payload = json.loads(request.body or b"{}")
        value = float(payload["value"])
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"error": "JSON body with a numeric 'value' is required"}, status=400)

    reading = Reading.objects.create(sensor=sensor, value=value)
    return JsonResponse(_reading_json(reading), status=201)
