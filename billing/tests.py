
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import CustomerProfile
from billing.models import Invoice, Payment
from plans.models import SubscriptionPlan
from subscriptions.models import Subscription, SubscriptionHistory


class BillingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer_group, _ = Group.objects.get_or_create(
            name="Customer"
        )
        self.admin_group, _ = Group.objects.get_or_create(
            name="Admin"
        )

        self.user1 = User.objects.create_user(
            username="billing_customer1",
            password="test-password-123",
        )
        self.user1.groups.add(self.customer_group)
        self.customer1 = CustomerProfile.objects.create(
            user=self.user1
        )

        self.user2 = User.objects.create_user(
            username="billing_customer2",
            password="test-password-123",
        )
        self.user2.groups.add(self.customer_group)
        self.customer2 = CustomerProfile.objects.create(
            user=self.user2
        )

        self.admin = User.objects.create_user(
            username="billing_admin",
            password="test-password-123",
        )
        self.admin.groups.add(self.admin_group)

        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.admin_token = Token.objects.create(user=self.admin)

        self.plan = SubscriptionPlan.objects.create(
            name="Billing Test Plan",
            description="Plan for billing API tests",
            price=Decimal("499.00"),
            billing_cycle=SubscriptionPlan.BillingCycle.MONTHLY,
            is_active=True,
        )

        self.subscription1 = Subscription.objects.create(
            customer=self.customer1,
            plan=self.plan,
            status=Subscription.Status.TRIAL,
            start_date="2026-10-01T00:00:00Z",
        )
        SubscriptionHistory.objects.create(
            subscription=self.subscription1,
            new_plan=self.plan,
            action=SubscriptionHistory.Action.CREATED,
            details="Test subscription created.",
        )

        self.subscription2 = Subscription.objects.create(
            customer=self.customer2,
            plan=self.plan,
            status=Subscription.Status.TRIAL,
            start_date="2026-10-01T00:00:00Z",
        )
        SubscriptionHistory.objects.create(
            subscription=self.subscription2,
            new_plan=self.plan,
            action=SubscriptionHistory.Action.CREATED,
            details="Test subscription created.",
        )

    def authenticate_as(self, token):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_successful_payment_uses_plan_price(self):
        self.authenticate_as(self.token1)

        response = self.client.post(
            "/api/payments/simulate/",
            {
                "subscription": self.subscription1.id,
                "status": Payment.Status.SUCCESS,
                "transaction_reference": "BILLING-TXN-001",
                "payment_method": "CARD",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Decimal(response.data["amount"]),
            self.plan.price,
        )
        self.assertEqual(
            response.data["customer"],
            self.customer1.id,
        )

    def test_failed_payment_is_recorded(self):
        self.authenticate_as(self.token1)

        response = self.client.post(
            "/api/payments/simulate/",
            {
                "subscription": self.subscription1.id,
                "status": Payment.Status.FAILED,
                "transaction_reference": "BILLING-TXN-002",
                "payment_method": "CARD",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "FAILED")

    def test_payment_cannot_use_another_customers_subscription(self):
        self.authenticate_as(self.token1)

        response = self.client.post(
            "/api/payments/simulate/",
            {
                "subscription": self.subscription2.id,
                "status": Payment.Status.SUCCESS,
                "transaction_reference": "BILLING-TXN-003",
                "payment_method": "CARD",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            Payment.objects.filter(
                transaction_reference="BILLING-TXN-003"
            ).exists()
        )

    def test_customer_only_sees_own_payments(self):
        Payment.objects.create(
            customer=self.customer2,
            subscription=self.subscription2,
            amount=self.plan.price,
            status=Payment.Status.SUCCESS,
            transaction_reference="BILLING-TXN-004",
            payment_method="CARD",
        )

        self.authenticate_as(self.token1)
        response = self.client.get("/api/payments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_invoice_amount_comes_from_plan_price(self):
        self.authenticate_as(self.token1)

        response = self.client.post(
            "/api/invoices/create/",
            {
                "subscription": self.subscription1.id,
                "amount": "1.00",
                "plan": 999999,
                "customer": self.customer2.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Decimal(response.data["amount"]),
            self.plan.price,
        )
        self.assertEqual(
            response.data["customer"],
            self.customer1.id,
        )
        self.assertEqual(response.data["plan"], self.plan.id)

    def test_customer_cannot_create_invoice_for_another_customer(self):
        self.authenticate_as(self.token1)

        response = self.client.post(
            "/api/invoices/create/",
            {"subscription": self.subscription2.id},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_customer_only_sees_own_invoices(self):
        Invoice.objects.create(
            invoice_number="BILLING-INV-001",
            customer=self.customer2,
            subscription=self.subscription2,
            plan=self.plan,
            amount=self.plan.price,
            due_date="2026-10-15T00:00:00Z",
        )

        self.authenticate_as(self.token1)
        response = self.client.get("/api/invoices/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_invoice_cannot_be_created_for_cancelled_subscription(self):
        self.subscription1.status = Subscription.Status.CANCELLED
        self.subscription1.save(update_fields=["status"])

        self.authenticate_as(self.token1)
        response = self.client.post(
            "/api/invoices/create/",
            {"subscription": self.subscription1.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_payment_requires_authentication(self):
        response = self.client.post(
            "/api/payments/simulate/",
            {
                "subscription": self.subscription1.id,
                "status": Payment.Status.SUCCESS,
                "transaction_reference": "BILLING-TXN-005",
                "payment_method": "CARD",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_admin_can_view_all_payments(self):
        Payment.objects.create(
            customer=self.customer2,
            subscription=self.subscription2,
            amount=self.plan.price,
            status=Payment.Status.SUCCESS,
            transaction_reference="BILLING-TXN-006",
            payment_method="CARD",
        )

        self.authenticate_as(self.admin_token)
        response = self.client.get("/api/payments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
