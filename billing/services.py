from datetime import timedelta

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

    # A successful payment must have a paid invoice.
    if status == Payment.Status.SUCCESS:
        invoice = (
            Invoice.objects
            .filter(
                customer=customer,
                subscription=subscription,
                plan=subscription.plan,
                status=Invoice.Status.PENDING,
            )
            .order_by("-issue_date")
            .first()
        )

        if invoice is None:
            invoice = create_invoice(subscription)

        invoice.status = Invoice.Status.PAID
        invoice.save(update_fields=["status"])

    return payment


@transaction.atomic
def create_invoice(subscription):
    plan = subscription.plan
    issue_date = timezone.now()
    due_date = issue_date + timedelta(days=7)

    invoice = Invoice.objects.create(
        invoice_number=(
            f"INV-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
        ),
        customer=subscription.customer,
        subscription=subscription,
        plan=plan,
        amount=plan.price,
        due_date=due_date,
        status=Invoice.Status.PENDING,
    )

    return invoice
