from django.db import transaction
from django.utils import timezone

from .models import Subscription, SubscriptionHistory


@transaction.atomic
def create_subscription(customer, plan):
    subscription = Subscription.objects.create(
        customer=customer,
        plan=plan,
        status=Subscription.Status.TRIAL,
        start_date=timezone.now(),
    )

    SubscriptionHistory.objects.create(
        subscription=subscription,
        previous_plan=None,
        new_plan=plan,
        action=SubscriptionHistory.Action.CREATED,
        details="Subscription created.",
    )

    return subscription


@transaction.atomic
def change_subscription_plan(subscription, target_plan, action):
    if subscription.status in [
        Subscription.Status.CANCELLED,
        Subscription.Status.EXPIRED,
    ]:
        raise ValueError(
            "Cancelled or expired subscriptions cannot be modified."
        )

    if not target_plan.is_active:
        raise ValueError(
            "Selected plan is not active."
        )

    if subscription.plan_id == target_plan.id:
        raise ValueError(
            "Selected plan is already the current plan."
        )

    current_plan = subscription.plan

    if action == SubscriptionHistory.Action.UPGRADED:
        if target_plan.price <= current_plan.price:
            raise ValueError(
                "Selected plan is not a valid upgrade."
            )

    elif action == SubscriptionHistory.Action.DOWNGRADED:
        if target_plan.price >= current_plan.price:
            raise ValueError(
                "Selected plan is not a valid downgrade."
            )

    else:
        raise ValueError(
            "Invalid subscription plan change action."
        )

    subscription.plan = target_plan
    subscription.save(update_fields=["plan", "updated_at"])

    SubscriptionHistory.objects.create(
        subscription=subscription,
        previous_plan=current_plan,
        new_plan=target_plan,
        action=action,
        details=f"Plan changed from {current_plan.name} to {target_plan.name}.",
    )

    return subscription

@transaction.atomic
def cancel_subscription(subscription):
    if subscription.status in [
        Subscription.Status.CANCELLED,
        Subscription.Status.EXPIRED,
    ]:
        raise ValueError(
            "Cancelled or expired subscriptions cannot be cancelled."
        )

    subscription.status = Subscription.Status.CANCELLED
    subscription.end_date = timezone.now()
    subscription.save(
        update_fields=["status", "end_date", "updated_at"]
    )

    SubscriptionHistory.objects.create(
        subscription=subscription,
        previous_plan=subscription.plan,
        new_plan=None,
        action=SubscriptionHistory.Action.CANCELLED,
        details="Subscription cancelled.",
    )

    return subscription
