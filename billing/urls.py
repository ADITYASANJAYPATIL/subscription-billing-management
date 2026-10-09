from django.urls import path

from .views import (
    InvoiceCreateView,
    InvoiceDetailView,
    InvoiceListView,
    PaymentDetailView,
    PaymentListView,
    PaymentSimulationView,
)

urlpatterns = [
    path(
        "payments/",
        PaymentListView.as_view(),
        name="payment-list",
    ),
    path(
        "payments/<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),
    path(
        "invoices/",
        InvoiceListView.as_view(),
        name="invoice-list",
    ),
    path(
        "invoices/<int:pk>/",
        InvoiceDetailView.as_view(),
        name="invoice-detail",
    ),
    path(
        "payments/simulate/",
        PaymentSimulationView.as_view(),
        name="payment-simulate",
    ),
    path(
        "invoices/create/",
        InvoiceCreateView.as_view(),
        name="invoice-create",
    ),
]
