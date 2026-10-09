
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from billing.models import Payment
from subscriptions.models import Subscription


class SubscriptionReportView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request, *args, **kwargs):
        status_counts = (
            Subscription.objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        return Response({
            "total_subscriptions": Subscription.objects.count(),
            "subscriptions_by_status": list(status_counts),
        })


class RevenueReportView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request, *args, **kwargs):
        successful_payments = Payment.objects.filter(
            status=Payment.Status.SUCCESS
        )

        revenue_by_plan = (
            successful_payments
            .values("subscription__plan__id", "subscription__plan__name")
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

        return Response({
            "revenue_by_plan": list(revenue_by_plan),
            "monthly_revenue": list(monthly_revenue),
        })
