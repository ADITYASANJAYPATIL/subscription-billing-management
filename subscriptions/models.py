from django.db import models

from accounts.models import CustomerProfile
from plans.models import SubscriptionPlan


class Subscription(models.Model):

    class Status(models.TextChoices):
        TRIAL = "TRIAL", "Trial"
        ACTIVE = "ACTIVE", "Active"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.PROTECT,
        related_name="subscriptions"
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TRIAL
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} - {self.plan} - {self.status}"


class SubscriptionHistory(models.Model):

    class Action(models.TextChoices):
        CREATED = "CREATED", "Created"
        UPGRADED = "UPGRADED", "Upgraded"
        DOWNGRADED = "DOWNGRADED", "Downgraded"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="history"
    )
    previous_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="previous_subscription_history",
        null=True,
        blank=True
    )
    new_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="new_subscription_history",
        null=True,
        blank=True
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices
    )
    details = models.TextField(
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.subscription} - {self.action}"