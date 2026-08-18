from django.urls import path

from . import views

app_name = "roadmap"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("goals/", views.goal_list, name="goal_list"),
    path("goals/new/", views.goal_create, name="goal_create"),
    path("goals/<int:pk>/", views.goal_detail, name="goal_detail"),
    path("goals/<int:pk>/edit/", views.goal_update, name="goal_update"),
    path("goals/<int:pk>/delete/", views.goal_delete, name="goal_delete"),

    path("goals/<int:goal_pk>/roadmaps/new/", views.roadmap_create, name="roadmap_create"),
    path("roadmaps/<int:pk>/edit/", views.roadmap_update, name="roadmap_update"),
    path("roadmaps/<int:pk>/delete/", views.roadmap_delete, name="roadmap_delete"),
    path("roadmaps/<int:pk>/move/<str:direction>/", views.roadmap_move, name="roadmap_move"),

    path("tasks/", views.task_list, name="task_list"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/edit/", views.task_update, name="task_update"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("tasks/<int:pk>/complete/", views.task_complete, name="task_complete"),

    path("reflections/", views.reflection_list, name="reflection_list"),
    path("reflections/new/", views.reflection_create, name="reflection_create"),
    path("reflections/<int:pk>/edit/", views.reflection_update, name="reflection_update"),
    path("reflections/<int:pk>/delete/", views.reflection_delete, name="reflection_delete"),
]
