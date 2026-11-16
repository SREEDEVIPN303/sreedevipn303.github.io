import json

from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskApiTests(TestCase):
    def setUp(self):
        self.list_url = reverse("taskboard:task-collection")

    def send(self, method, url, body=None):
        return getattr(self.client, method)(url, data=json.dumps(body or {}), content_type="application/json")

    def test_create_and_list(self):
        r = self.send("post", self.list_url, {"title": "Write tests", "priority": "high"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["status"], "todo")
        self.assertEqual(len(self.client.get(self.list_url).json()["tasks"]), 1)

    def test_create_validation(self):
        self.assertEqual(self.send("post", self.list_url, {"title": "  "}).status_code, 400)
        self.assertEqual(self.send("post", self.list_url, {"title": "x", "priority": "urgent"}).status_code, 400)
        self.assertEqual(self.client.post(self.list_url, "not json", content_type="application/json").status_code, 400)

    def test_move_and_delete(self):
        t = Task.objects.create(title="Ship it")
        url = reverse("taskboard:task-detail", args=[t.id])
        r = self.send("patch", url, {"status": "doing"})
        self.assertEqual(r.json()["status"], "doing")
        self.assertEqual(self.send("patch", url, {"status": "bogus"}).status_code, 400)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(Task.objects.exists())

    def test_filter_by_status_and_404(self):
        Task.objects.create(title="a", status="done")
        Task.objects.create(title="b")
        data = self.client.get(self.list_url, {"status": "done"}).json()
        self.assertEqual([t["title"] for t in data["tasks"]], ["a"])
        self.assertEqual(self.client.get(reverse("taskboard:task-detail", args=[999])).status_code, 404)

    def test_board_page(self):
        self.assertEqual(self.client.get(reverse("taskboard:board")).status_code, 200)
