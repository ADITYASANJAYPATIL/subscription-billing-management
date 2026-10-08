from django.contrib import admin

from .models import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "billing_cycle",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("billing_cycle", "is_active")
    search_fields = ("name", "description")