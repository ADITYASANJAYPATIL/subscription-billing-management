from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminRole
from .models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer


class PlanListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionPlanSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminRole()]

        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return SubscriptionPlan.objects.all().order_by("name")

        return SubscriptionPlan.objects.filter(
            is_active=True
        ).order_by("name")


class PlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionPlanSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminRole()]

        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return SubscriptionPlan.objects.all()

        return SubscriptionPlan.objects.filter(
            is_active=True
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
