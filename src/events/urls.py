from django.urls import path

from .views import EventListView, EventRegisterView

urlpatterns = [
    path("events/", EventListView.as_view(), name="events-list"),
    path(
        "events/<uuid:event_id>/register/",
        EventRegisterView.as_view(),
        name="event-register",
    ),
]
