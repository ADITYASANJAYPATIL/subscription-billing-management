from rest_framework import generics

from accounts.permissions import IsCustomerRole
from accounts.models import CustomerProfile
from plans.models import SubscriptionPlan

from .serializers import SubscriptionSerializer
from .services import create_subscription


class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        return [IsCustomerRole()]

    def get_queryset(self):
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
        