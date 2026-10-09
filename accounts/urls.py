from django.urls import path

from . import views
from accounts.dashboard_views import (
    admin_customers,
    admin_plans,
    admin_invoices,
    admin_payments,
    admin_reports,
    admin_subscriptions,
    available_plans,
    customer_invoices,
    customer_payments,
    customer_subscription_detail,
    customer_subscriptions,
)

app_name = "accounts"

urlpatterns = [
    path(
    "admin/subscriptions/",
    admin_subscriptions,
    name="admin_subscriptions",
    ),
    path(
        "admin/payments/",
        admin_payments,
        name="admin_payments",
    ),
    path(
        "admin/invoices/",
        admin_invoices,
        name="admin_invoices",
    ),
    path(
        "admin/reports/",
        admin_reports,
        name="admin_reports",
    ),
    path(
        "admin/customers/",
        admin_customers,
        name="admin_customers",
    ),
    path(
        "admin/plans/",
        admin_plans,
        name="admin_plans",
    ),
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
    path("payments/", customer_payments, name="customer_payments"),
    path("invoices/", customer_invoices, name="customer_invoices"),
]