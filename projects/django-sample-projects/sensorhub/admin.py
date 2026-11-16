from django.contrib import admin
from .models import Reading, Sensor


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "unit", "threshold", "active")


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("sensor", "value", "recorded_at")
    list_filter = ("sensor",)
