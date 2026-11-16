from django.urls import path

from . import views

app_name = "sensorhub"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/sensors/", views.sensor_list, name="sensor-list"),
    path("api/sensors/<int:sensor_id>/readings/", views.sensor_readings, name="sensor-readings"),
]
