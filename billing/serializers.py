from rest_framework import serializers

from .models import Invoice, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "customer",
            "subscription",
            "amount",
            "payment_date",
            "status",
            "transaction_reference",
            "payment_method",
        ]
        read_only_fields = [
            "id",
            "customer",
            "amount",
            "payment_date",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "customer",
            "subscription",
            "plan",
            "amount",
            "issue_date",
            "due_date",
            "status",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "customer",
            "plan",
            "amount",
            "issue_date",
            "due_date",
            "status",
        ]
