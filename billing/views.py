from rest_framework import generics, status
from rest_framework.response import Response

from accounts.models import CustomerProfile
from accounts.permissions import IsAdminRole, IsCustomerRole

from .models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer
from .services import create_invoice, create_payment


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return [IsAdminRole()]

        return [IsCustomerRole()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return (
                Payment.objects
                .select_related("customer", "subscription")
                .order_by("-payment_date")
            )

        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return (
            Payment.objects
            .filter(customer=customer)
            .select_related("subscription")
            .order_by("-payment_date")
        )


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return [IsAdminRole()]

        return [IsCustomerRole()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return Payment.objects.select_related(
                "customer",
                "subscription",
            )

        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return Payment.objects.filter(
            customer=customer
        ).select_related(
            "subscription"
        )


class PaymentSimulationView(generics.GenericAPIView):
    serializer_class = PaymentSerializer

    def get_permissions(self):
        return [IsCustomerRole()]

    def get_queryset(self):
        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return customer.subscriptions.select_related("plan")

    def post(self, request):
        subscription_id = request.data.get("subscription")
        payment_status = request.data.get("status")
        transaction_reference = request.data.get(
            "transaction_reference"
        )
        payment_method = request.data.get("payment_method")

        if not subscription_id:
            return Response(
                {
                    "subscription": [
                        "This field is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment_status not in [
            Payment.Status.SUCCESS,
            Payment.Status.FAILED,
        ]:
            return Response(
                {
                    "status": [
                        "Status must be SUCCESS or FAILED."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not transaction_reference:
            return Response(
                {
                    "transaction_reference": [
                        "This field is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not payment_method:
            return Response(
                {
                    "payment_method": [
                        "This field is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = self.get_queryset().filter(
            pk=subscription_id
        ).first()

        if subscription is None:
            return Response(
                {
                    "detail": "No Subscription matches the given query."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if subscription.status in [
            subscription.Status.CANCELLED,
            subscription.Status.EXPIRED,
        ]:
            return Response(
                {
                    "detail": (
                        "Payments cannot be recorded for "
                        "cancelled or expired subscriptions."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = CustomerProfile.objects.get(
            user=request.user
        )

        payment = create_payment(
            customer=customer,
            subscription=subscription,
            status=payment_status,
            transaction_reference=transaction_reference,
            payment_method=payment_method,
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer

    def get_permissions(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return [IsAdminRole()]

        return [IsCustomerRole()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return (
                Invoice.objects
                .select_related(
                    "customer",
                    "subscription",
                    "plan",
                )
                .order_by("-issue_date")
            )

        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return (
            Invoice.objects
            .filter(customer=customer)
            .select_related(
                "subscription",
                "plan",
            )
            .order_by("-issue_date")
        )


class InvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer

    def get_permissions(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return [IsAdminRole()]

        return [IsCustomerRole()]

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return Invoice.objects.select_related(
                "customer",
                "subscription",
                "plan",
            )

        customer = CustomerProfile.objects.get(
            user=self.request.user
        )

        return Invoice.objects.filter(
            customer=customer
        ).select_related(
            "subscription",
            "plan",
        )


class InvoiceCreateView(generics.CreateAPIView):
    serializer_class = InvoiceSerializer

    def get_permissions(self):
        return [IsCustomerRole()]

    def create(self, request, *args, **kwargs):
        subscription_id = request.data.get("subscription")

        if not subscription_id:
            return Response(
                {
                    "subscription": [
                        "This field is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = CustomerProfile.objects.get(
            user=request.user
        )

        subscription = (
            customer.subscriptions
            .filter(pk=subscription_id)
            .select_related("plan")
            .first()
        )

        if subscription is None:
            return Response(
                {
                    "detail": "No Subscription matches the given query."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if subscription.status in [
            subscription.Status.CANCELLED,
            subscription.Status.EXPIRED,
        ]:
            return Response(
                {
                    "detail": (
                        "Invoices cannot be generated for "
                        "cancelled or expired subscriptions."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice = create_invoice(subscription)

        return Response(
            InvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED,
        )