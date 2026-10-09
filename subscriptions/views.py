from rest_framework import generics, status
from rest_framework.response import Response

from accounts.permissions import IsAdminRole, IsCustomerRole
from accounts.models import CustomerProfile
from plans.models import SubscriptionPlan

from .serializers import SubscriptionSerializer
from .services import (
    create_subscription,
    change_subscription_plan,
    cancel_subscription,
)
from .models import Subscription, SubscriptionHistory


class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerRole()]

        if self.request.user.groups.filter(name="Admin").exists():
            return [IsAdminRole()]

        return [IsCustomerRole()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return (
                Subscription.objects
                .select_related("customer", "plan")
                .order_by("-created_at")
            )

        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return (
            customer.subscriptions
            .select_related("plan")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        plan = serializer.validated_data["plan"]

        subscription = create_subscription(
            customer=customer,
            plan=plan,
        )

        serializer.instance = subscription


class SubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return [IsAdminRole()]

        return [IsCustomerRole()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return (
                Subscription.objects
                .select_related("customer", "plan")
            )

        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return (
            customer.subscriptions
            .select_related("plan")
        )


class SubscriptionPlanChangeView(generics.GenericAPIView):
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        return [IsCustomerRole()]

    def get_queryset(self):
        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return customer.subscriptions.select_related("plan")

    def post(self, request, pk, action):
        subscription = self.get_queryset().filter(pk=pk).first()

        if subscription is None:
            return Response(
                {
                    "detail": "No Subscription matches the given query."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        plan_id = request.data.get("plan")

        if not plan_id:
            return Response(
                {
                    "plan": ["This field is required."]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_plan = SubscriptionPlan.objects.get(
                pk=plan_id
            )
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {
                    "plan": ["Selected plan does not exist."]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        history_action = (
            SubscriptionHistory.Action.UPGRADED
            if action == "upgrade"
            else SubscriptionHistory.Action.DOWNGRADED
        )

        try:
            subscription = change_subscription_plan(
                subscription=subscription,
                target_plan=target_plan,
                action=history_action,
            )
        except ValueError as exc:
            return Response(
                {
                    "plan": [str(exc)]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_200_OK,
        )

class SubscriptionCancelView(generics.GenericAPIView):
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        return [IsCustomerRole()]

    def get_queryset(self):
        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return customer.subscriptions.select_related("plan")

    def post(self, request, pk):
        subscription = self.get_queryset().filter(pk=pk).first()

        if subscription is None:
            return Response(
                {
                    "detail": "No Subscription matches the given query."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            subscription = cancel_subscription(subscription)
        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_200_OK,
        )