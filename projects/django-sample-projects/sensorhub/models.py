from django.db import models


class Sensor(models.Model):
    name = models.CharField(max_length=80, unique=True)
    location = models.CharField(max_length=120, blank=True)
    unit = models.CharField(max_length=12, default="")
    threshold = models.FloatField(null=True, blank=True, help_text="Alert when a reading exceeds this value")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Reading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="readings")
    value = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]
        indexes = [models.Index(fields=["sensor", "-recorded_at"])]

    @property
    def is_alert(self):
        t = self.sensor.threshold
        return t is not None and self.value > t

    def __str__(self):
        return f"{self.sensor.name}: {self.value}"
