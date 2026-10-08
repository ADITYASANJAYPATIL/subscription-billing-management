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
