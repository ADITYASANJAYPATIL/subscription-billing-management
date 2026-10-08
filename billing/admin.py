from django.contrib import admin

from .models import Invoice, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "subscription",
        "amount",
        "status",
        "transaction_reference",
        "payment_date",
    )
    list_filter = ("status", "payment_method")
    search_fields = (
        "customer__user__username",
        "customer__user__email",
        "transaction_reference",
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "invoice_number",
        "customer",
        "subscription",
        "plan",
        "amount",
        "status",
        "issue_date",
        "due_date",
    )
    list_filter = ("status", "plan")
    search_fields = (
        "invoice_number",
        "customer__user__username",
        "customer__user__email",
    )