import json

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Reading, Sensor


@override_settings(DEVICE_API_KEY="test-key")
class SensorApiTests(TestCase):
    def setUp(self):
        self.sensor = Sensor.objects.create(name="Temp", unit="°C", threshold=30)
        self.url = reverse("sensorhub:sensor-readings", args=[self.sensor.id])

    def post(self, body, key="test-key"):
        headers = {"HTTP_X_API_KEY": key} if key else {}
        return self.client.post(self.url, data=json.dumps(body), content_type="application/json", **headers)

    def test_device_can_post_reading(self):
        r = self.post({"value": 31.5})
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.json()["alert"])
        self.assertEqual(Reading.objects.count(), 1)

    def test_post_requires_api_key(self):
        self.assertEqual(self.post({"value": 20}, key=None).status_code, 401)
        self.assertEqual(self.post({"value": 20}, key="wrong").status_code, 401)

    def test_post_validates_payload(self):
        self.assertEqual(self.post({"value": "abc"}).status_code, 400)
        self.assertEqual(self.post({}).status_code, 400)

    def test_get_returns_oldest_first_and_respects_limit(self):
        for v in (1, 2, 3):
            Reading.objects.create(sensor=self.sensor, value=v)
        data = self.client.get(self.url, {"limit": 2}).json()
        self.assertEqual([r["value"] for r in data["readings"]], [2, 3])

    def test_bad_limit(self):
        self.assertEqual(self.client.get(self.url, {"limit": "x"}).status_code, 400)

    def test_sensor_list_and_dashboard(self):
        Reading.objects.create(sensor=self.sensor, value=10)
        data = self.client.get(reverse("sensorhub:sensor-list")).json()
        self.assertEqual(data["sensors"][0]["latest"]["value"], 10)
        self.assertEqual(self.client.get(reverse("sensorhub:dashboard")).status_code, 200)
