
from decimal import Decimal

from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from accounts.models import CustomerProfile
from billing.models import Payment
from plans.models import SubscriptionPlan
from subscriptions.models import Subscription


class ReportAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        customer_group, _ = Group.objects.get_or_create(name="Customer")

        cls.admin = User.objects.create_user(
            username="report_admin",
            password="test-password-123",
        )
        cls.admin.groups.add(admin_group)

        cls.customer_user = User.objects.create_user(
            username="report_customer",
            password="test-password-123",
        )
        cls.customer_user.groups.add(customer_group)

        cls.customer = CustomerProfile.objects.create(
            user=cls.customer_user
        )

        cls.plan = SubscriptionPlan.objects.create(
            name="Report Test Plan",
            description="Plan for report tests",
            price=Decimal("499.00"),
            billing_cycle=SubscriptionPlan.BillingCycle.MONTHLY,
            is_active=True,
        )

        cls.subscription = Subscription.objects.create(
            customer=cls.customer,
            plan=cls.plan,
            status=Subscription.Status.ACTIVE,
            start_date=__import__(
                "django.utils.timezone", fromlist=["now"]
            ).now(),
        )

        Payment.objects.create(
            customer=cls.customer,
            subscription=cls.subscription,
            amount=Decimal("499.00"),
            status=Payment.Status.SUCCESS,
            transaction_reference="REPORT-TEST-SUCCESS",
            payment_method="CARD",
        )

        Payment.objects.create(
            customer=cls.customer,
            subscription=cls.subscription,
            amount=Decimal("499.00"),
            status=Payment.Status.FAILED,
            transaction_reference="REPORT-TEST-FAILED",
            payment_method="CARD",
        )

    def authenticate_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_customer_cannot_access_subscription_report(self):
        self.authenticate_as(self.customer_user)

        response = self.client.get("/api/reports/subscriptions/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_subscription_report(self):
        self.authenticate_as(self.admin)

        response = self.client.get("/api/reports/subscriptions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_subscriptions"], 1)

    def test_customer_cannot_access_revenue_report(self):
        self.authenticate_as(self.customer_user)

        response = self.client.get("/api/reports/revenue/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_revenue_report_counts_only_successful_payments(self):
        self.authenticate_as(self.admin)

        response = self.client.get("/api/reports/revenue/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["revenue_by_plan"][0]["total_revenue"],
            Decimal("499.00"),
        )

    def test_unauthenticated_user_cannot_access_reports(self):
        response = self.client.get("/api/reports/subscriptions/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
