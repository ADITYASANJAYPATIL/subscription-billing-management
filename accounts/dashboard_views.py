from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CustomerProfile
from accounts.permissions import IsAdminRole, IsCustomerRole
from plans.models import SubscriptionPlan
from subscriptions.models import Subscription, SubscriptionHistory
from subscriptions.services import (
    cancel_subscription,
    change_subscription_plan,
)


@login_required
def admin_dashboard(request):
    if not IsAdminRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    return render(request, "admin/dashboard.html")


@login_required
def customer_dashboard(request):
    if not IsCustomerRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    return render(request, "customer/dashboard.html")


@login_required
def available_plans(request):
    if not IsCustomerRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    plans = SubscriptionPlan.objects.filter(
        is_active=True
    ).order_by("price", "name")

    return render(
        request,
        "customer/plans.html",
        {"plans": plans},
    )


@login_required
def customer_subscriptions(request):
    if not IsCustomerRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    customer = get_object_or_404(
        CustomerProfile,
        user=request.user,
    )

    subscriptions = (
        Subscription.objects
        .filter(customer=customer)
        .select_related("plan")
        .order_by("-created_at")
    )

    return render(
        request,
        "customer/subscriptions.html",
        {"subscriptions": subscriptions},
    )


@login_required
def customer_subscription_detail(request, pk):
    if not IsCustomerRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    customer = get_object_or_404(
        CustomerProfile,
        user=request.user,
    )

    subscription = get_object_or_404(
        Subscription.objects
        .select_related("plan")
        .prefetch_related(
            "history__previous_plan",
            "history__new_plan",
        ),
        pk=pk,
        customer=customer,
    )

    if request.method == "POST":
        action = request.POST.get("action", "")

        if subscription.status not in [
            Subscription.Status.TRIAL,
            Subscription.Status.ACTIVE,
        ]:
            messages.error(
                request,
                "This subscription can no longer be modified.",
            )
            return redirect(
                "accounts:customer_subscription_detail",
                pk=subscription.pk,
            )

        if action in ["upgrade", "downgrade"]:
            plan_id = request.POST.get("plan", "")

            try:
                target_plan = SubscriptionPlan.objects.get(
                    pk=plan_id,
                    is_active=True,
                )
            except (
                SubscriptionPlan.DoesNotExist,
                ValueError,
                TypeError,
            ):
                messages.error(
                    request,
                    "Please select a valid active plan.",
                )
                return redirect(
                    "accounts:customer_subscription_detail",
                    pk=subscription.pk,
                )

            history_action = (
                SubscriptionHistory.Action.UPGRADED
                if action == "upgrade"
                else SubscriptionHistory.Action.DOWNGRADED
            )

            try:
                change_subscription_plan(
                    subscription=subscription,
                    target_plan=target_plan,
                    action=history_action,
                )
                messages.success(
                    request,
                    f"Subscription {action} successful.",
                )
            except ValueError as exc:
                messages.error(request, str(exc))

        elif action == "cancel":
            try:
                cancel_subscription(subscription)
                messages.success(
                    request,
                    "Subscription cancelled successfully.",
                )
            except ValueError as exc:
                messages.error(request, str(exc))

        else:
            messages.error(
                request,
                "Invalid subscription action.",
            )

        return redirect(
            "accounts:customer_subscription_detail",
            pk=subscription.pk,
        )

    available_plans = SubscriptionPlan.objects.filter(
        is_active=True
    ).exclude(
        pk=subscription.plan_id
    ).order_by("price", "name")

    return render(
        request,
        "customer/subscription_detail.html",
        {
            "subscription": subscription,
            "history": subscription.history.all(),
            "available_plans": available_plans,
        },
    )