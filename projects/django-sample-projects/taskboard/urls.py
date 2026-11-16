from django.urls import path

from . import views

app_name = "taskboard"
urlpatterns = [
    path("", views.board, name="board"),
    path("api/tasks/", views.task_collection, name="task-collection"),
    path("api/tasks/<int:task_id>/", views.task_detail, name="task-detail"),
]
