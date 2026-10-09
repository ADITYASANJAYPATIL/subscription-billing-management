from django.urls import path

from . import views
from accounts.dashboard_views import (
    available_plans,
    customer_subscription_detail,
    customer_subscriptions,
)

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("plans/", available_plans, name="available_plans"),
    path(
        "subscriptions/",
        customer_subscriptions,
        name="customer_subscriptions",
    ),
    path(
        "subscriptions/<int:pk>/",
        customer_subscription_detail,
        name="customer_subscription_detail",
    ),
]