from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.views.decorators.http import require_http_methods
from billing.models import Invoice, Payment
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

@login_required
def customer_payments(request):
    if not IsCustomerRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    customer = get_object_or_404(
        CustomerProfile,
        user=request.user,
    )

    payments = (
        Payment.objects
        .filter(customer=customer)
        .select_related("subscription", "subscription__plan")
        .order_by("-payment_date")
    )

    return render(
        request,
        "customer/payments.html",
        {"payments": payments},
    )


@login_required
def customer_invoices(request):
    if not IsCustomerRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    customer = get_object_or_404(
        CustomerProfile,
        user=request.user,
    )

    invoices = (
        Invoice.objects
        .filter(customer=customer)
        .select_related("subscription", "plan")
        .order_by("-issue_date")
    )

    return render(
        request,
        "customer/invoices.html",
        {"invoices": invoices},
    )

@login_required
@require_http_methods(["GET", "POST"])
def admin_customers(request):
    if not IsAdminRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        if not all([username, email, password]):
            messages.error(
                request,
                "Username, email and password are required.",
            )
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            try:
                customer_group = Group.objects.get(name="Customer")

                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    user.groups.add(customer_group)
                    CustomerProfile.objects.create(
                        user=user,
                        phone=phone,
                    )

                messages.success(request, "Customer created successfully.")
                return redirect("accounts:admin_customers")

            except Group.DoesNotExist:
                messages.error(
                    request,
                    "Customer role group is missing. Create it before adding customers.",
                )

    customers = (
        CustomerProfile.objects
        .select_related("user")
        .order_by("user__username")
    )

    return render(
        request,
        "admin/customers.html",
        {"customers": customers},
    )


@login_required
@require_http_methods(["GET", "POST"])
def admin_plans(request):
    if not IsAdminRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    if request.method == "POST":
        action = request.POST.get("action", "")
        plan_id = request.POST.get("plan_id", "")

        if action == "toggle":
            plan = get_object_or_404(
                SubscriptionPlan,
                pk=plan_id,
            )
            plan.is_active = not plan.is_active
            plan.save(update_fields=["is_active", "updated_at"])

            messages.success(
                request,
                f"{plan.name} status updated.",
            )
            return redirect("accounts:admin_plans")

        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        price_text = request.POST.get("price", "").strip()
        billing_cycle = request.POST.get("billing_cycle", "")

        from decimal import Decimal, InvalidOperation

        try:
            price = Decimal(price_text)
            if not price.is_finite() or price <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, "Enter a valid price greater than zero.")
            return redirect("accounts:admin_plans")

        if not name:
            messages.error(request, "Plan name is required.")
            return redirect("accounts:admin_plans")

        if billing_cycle not in SubscriptionPlan.BillingCycle.values:
            messages.error(request, "Select a valid billing cycle.")
            return redirect("accounts:admin_plans")

        if action == "create":
            SubscriptionPlan.objects.create(
                name=name,
                description=description,
                price=price,
                billing_cycle=billing_cycle,
                is_active=True,
            )
            messages.success(request, "Plan created successfully.")

        elif action == "update":
            plan = get_object_or_404(
                SubscriptionPlan,
                pk=plan_id,
            )
            plan.name = name
            plan.description = description
            plan.price = price
            plan.billing_cycle = billing_cycle
            plan.save(
                update_fields=[
                    "name",
                    "description",
                    "price",
                    "billing_cycle",
                    "updated_at",
                ]
            )
            messages.success(request, "Plan updated successfully.")

        else:
            messages.error(request, "Invalid plan action.")

        return redirect("accounts:admin_plans")

    plans = SubscriptionPlan.objects.all().order_by("name")
    edit_id = request.GET.get("edit")
    edit_plan = None

    if edit_id:
        edit_plan = get_object_or_404(
            SubscriptionPlan,
            pk=edit_id,
        )

    return render(
        request,
        "admin/plans.html",
        {
            "plans": plans,
            "edit_plan": edit_plan,
        },
    )


@login_required
def admin_subscriptions(request):
    if not IsAdminRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    subscriptions = (
        Subscription.objects
        .select_related("customer__user", "plan")
        .order_by("-created_at")
    )

    return render(
        request,
        "admin/subscriptions.html",
        {"subscriptions": subscriptions},
    )


@login_required
def admin_payments(request):
    if not IsAdminRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    payments = (
        Payment.objects
        .select_related(
            "customer__user",
            "subscription",
            "subscription__plan",
        )
        .order_by("-payment_date")
    )

    return render(
        request,
        "admin/payments.html",
        {"payments": payments},
    )


@login_required
def admin_invoices(request):
    if not IsAdminRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    invoices = (
        Invoice.objects
        .select_related(
            "customer__user",
            "subscription",
            "plan",
        )
        .order_by("-issue_date")
    )

    return render(
        request,
        "admin/invoices.html",
        {"invoices": invoices},
    )


@login_required
def admin_reports(request):
    if not IsAdminRole().has_permission(request, None):
        return render(request, "403.html", status=403)

    status_counts = (
        Subscription.objects
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    successful_payments = Payment.objects.filter(
        status=Payment.Status.SUCCESS
    )

    revenue_by_plan = (
        successful_payments
        .values("subscription__plan__name")
        .annotate(total_revenue=Sum("amount"))
        .order_by("subscription__plan__name")
    )

    monthly_revenue = (
        successful_payments
        .annotate(month=TruncMonth("payment_date"))
        .values("month")
        .annotate(total_revenue=Sum("amount"))
        .order_by("month")
    )

    return render(
        request,
        "admin/reports.html",
        {
            "status_counts": status_counts,
            "revenue_by_plan": revenue_by_plan,
            "monthly_revenue": monthly_revenue,
            "total_subscriptions": Subscription.objects.count(),
        },
    )
