from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from . import views

urlpatterns = [
    # authentication
    path("register", views.register_view),
    path("login", views.login_view),
    # user endpoinst
    path("user/<int:userId>", views.UserDetailAPIView.as_view()),
    # company endpoints
    path("user/<int:userId>/company", views.CompanyAPIView.as_view()),
    path("user/<int:userId>/company-detail", views.CompanyDetailView.as_view()),
    # services endpoints
    path(
        "user/<int:userId>/company-service",
        views.ServiceAPIView.as_view(),
    ),
    path(
        "user/<int:userId>/displayed-service", views.displayed_services
    ),  # display the services that the user need to display
    path(
        "user/<int:userId>/company-service/<int:serviceId>",
        views.ServiceDetailAPIView.as_view(),
    ),
    # slot reservation endpoints
    path(
        "user/<int:userId>/company-service/<int:serviceId>/slot",
        views.QueueSlotAPIView.as_view(),
    ),
    path(
        "user/<int:userId>/company-service/<int:serviceId>/slot/<int:slotId>",
        views.QueueSlotDetailView.as_view(),
    ),
    # action endpoints, serve,cancel of a current (called ) queue
    path(
        "user/<int:userId>/company-service/<int:serviceId>/slot/<int:slotId>/action",
        views.action,
    ),
    # get queue count for a particular service of today date endpoint
    path(
        "user/<int:userId>/company-service/<int:serviceId>/queue-count",
        views.get_service_count,
    ),
    # get number of personnage waiting for a given serviceendpoint
    path(
        "user/<int:userId>/company-service/<int:serviceId>/waiting-count",
        views.get_waiting_count,
    ),
    # get current queue endpoint
    path(
        "user/<int:userId>/company-service/<int:serviceId>/current-next-queue",
        views.get_current_and_next_queue,
    ),
    # documentation
    path("schema", SpectacularAPIView.as_view()),
    path("docs", SpectacularSwaggerView.as_view(url_name="schema")),
    path("redoc", SpectacularRedocView.as_view(url_name="schema")),
]
