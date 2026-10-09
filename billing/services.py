from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Invoice, Payment


@transaction.atomic
def create_payment(
    customer,
    subscription,
    status,
    transaction_reference,
    payment_method,
):
    amount = subscription.plan.price

    payment = Payment.objects.create(
        customer=customer,
        subscription=subscription,
        amount=amount,
        status=status,
        transaction_reference=transaction_reference,
        payment_method=payment_method,
    )

    return payment


@transaction.atomic
def create_invoice(subscription):
    plan = subscription.plan
    issue_date = timezone.now()
    due_date = issue_date + timedelta(days=7)

    invoice = Invoice.objects.create(
        invoice_number=f"INV-{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
        customer=subscription.customer,
        subscription=subscription,
        plan=plan,
        amount=plan.price,
        issue_date=issue_date,
        due_date=due_date,
        status=Invoice.Status.PENDING,
    )

    return invoice
