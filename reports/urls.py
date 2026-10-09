
from django.urls import path

from .views import (
    SubscriptionReportView,
    RevenueReportView,
)

urlpatterns = [
    path(
        "subscriptions/",
        SubscriptionReportView.as_view(),
        name="subscription-report",
    ),
    path(
        "revenue/",
        RevenueReportView.as_view(),
        name="revenue-report",
    ),
]
