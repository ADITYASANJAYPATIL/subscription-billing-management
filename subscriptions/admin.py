from django.contrib import admin

from .models import Subscription, SubscriptionHistory


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "plan",
        "status",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("status", "plan")
    search_fields = (
        "customer__user__username",
        "customer__user__email",
        "plan__name",
    )


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subscription",
        "previous_plan",
        "new_plan",
        "action",
        "created_at",
    )
    list_filter = ("action",)
    search_fields = (
        "subscription__customer__user__username",
        "subscription__customer__user__email",
    )