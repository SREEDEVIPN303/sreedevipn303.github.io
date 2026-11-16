import random

from django.core.management.base import BaseCommand

from sensorhub.models import Reading, Sensor


class Command(BaseCommand):
    help = "Create demo sensors with a short history of readings"

    def handle(self, *args, **opts):
        specs = [
            ("Server Room Temp", "Rack A", "°C", 30.0, 26.0, 1.2),
            ("Warehouse Humidity", "Bay 2", "%", 70.0, 55.0, 3.0),
            ("Pump Vibration", "Plant 1", "mm/s", 6.0, 3.5, 0.8),
        ]
        for name, loc, unit, thr, base, step in specs:
            sensor, _ = Sensor.objects.get_or_create(
                name=name, defaults={"location": loc, "unit": unit, "threshold": thr})
            if sensor.readings.exists():
                continue
            v = base
            for _ in range(40):
                v = max(0, v + random.uniform(-step, step))
                Reading.objects.create(sensor=sensor, value=round(v, 2))
        self.stdout.write(self.style.SUCCESS("Demo sensors ready"))
