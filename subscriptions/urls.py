from django.urls import path

from .views import (
    SubscriptionCancelView,
    SubscriptionDetailView,
    SubscriptionListCreateView,
    SubscriptionPlanChangeView,
)

urlpatterns = [
    path(
        "",
        SubscriptionListCreateView.as_view(),
        name="subscription-list-create",
    ),
    path(
        "<int:pk>/",
        SubscriptionDetailView.as_view(),
        name="subscription-detail",
    ),
    path(
        "<int:pk>/upgrade/",
        SubscriptionPlanChangeView.as_view(),
        {"action": "upgrade"},
        name="subscription-upgrade",
    ),
    path(
        "<int:pk>/downgrade/",
        SubscriptionPlanChangeView.as_view(),
        {"action": "downgrade"},
        name="subscription-downgrade",
    ),
    path(
        "<int:pk>/cancel/",
        SubscriptionCancelView.as_view(),
        name="subscription-cancel",
    ),
]
