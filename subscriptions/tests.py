
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import CustomerProfile
from plans.models import SubscriptionPlan
from subscriptions.models import Subscription, SubscriptionHistory


class SubscriptionAPITests(TestCase):
    def setUp(self):
        self.customer_group, _ = Group.objects.get_or_create(
            name="Customer"
        )
        self.admin_group, _ = Group.objects.get_or_create(
            name="Admin"
        )

        self.customer_user = User.objects.create_user(
            username="customer_test",
            password="test-password-123",
        )
        self.customer_user.groups.add(self.customer_group)

        self.customer = CustomerProfile.objects.create(
            user=self.customer_user
        )

        self.other_user = User.objects.create_user(
            username="other_customer",
            password="test-password-123",
        )
        self.other_user.groups.add(self.customer_group)

        self.other_customer = CustomerProfile.objects.create(
            user=self.other_user
        )

        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="test-password-123",
        )
        self.admin_user.groups.add(self.admin_group)

        self.client = APIClient()
        self.client.force_authenticate(user=self.customer_user)

        self.basic_plan = SubscriptionPlan.objects.create(
            name="Basic Test Plan",
            description="Basic test plan",
            price=Decimal("499.00"),
            billing_cycle=SubscriptionPlan.BillingCycle.MONTHLY,
            is_active=True,
        )

        self.premium_plan = SubscriptionPlan.objects.create(
            name="Premium Test Plan",
            description="Premium test plan",
            price=Decimal("999.00"),
            billing_cycle=SubscriptionPlan.BillingCycle.MONTHLY,
            is_active=True,
        )

        self.inactive_plan = SubscriptionPlan.objects.create(
            name="Inactive Test Plan",
            description="Inactive test plan",
            price=Decimal("1499.00"),
            billing_cycle=SubscriptionPlan.BillingCycle.MONTHLY,
            is_active=False,
        )

    def create_subscription(self, customer=None, plan=None, status=None):
        customer = customer or self.customer
        plan = plan or self.basic_plan

        return Subscription.objects.create(
            customer=customer,
            plan=plan,
            status=status or Subscription.Status.TRIAL,
            start_date=timezone.now(),
        )

    def test_customer_can_create_subscription(self):
        response = self.client.post(
            "/api/subscriptions/",
            {"plan": self.basic_plan.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["customer"], self.customer.id)
        self.assertEqual(response.data["plan"], self.basic_plan.id)
        self.assertEqual(response.data["status"], "TRIAL")

        subscription = Subscription.objects.get(
            id=response.data["id"]
        )
        self.assertTrue(
            subscription.history.filter(
                action=SubscriptionHistory.Action.CREATED
            ).exists()
        )

    def test_customer_cannot_subscribe_to_inactive_plan(self):
        response = self.client.post(
            "/api/subscriptions/",
            {"plan": self.inactive_plan.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Subscription.objects.count(), 0)

    def test_customer_can_only_view_own_subscriptions(self):
        own_subscription = self.create_subscription()
        other_subscription = self.create_subscription(
            customer=self.other_customer,
            plan=self.premium_plan,
        )

        list_response = self.client.get("/api/subscriptions/")

        self.assertEqual(list_response.status_code, 200)
        returned_ids = [
            item["id"] for item in list_response.data
        ]
        self.assertIn(own_subscription.id, returned_ids)
        self.assertNotIn(other_subscription.id, returned_ids)

        detail_response = self.client.get(
            f"/api/subscriptions/{other_subscription.id}/"
        )
        self.assertEqual(detail_response.status_code, 404)

    def test_customer_can_upgrade_subscription(self):
        subscription = self.create_subscription()

        response = self.client.post(
            f"/api/subscriptions/{subscription.id}/upgrade/",
            {"plan": self.premium_plan.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        subscription.refresh_from_db()
        self.assertEqual(subscription.plan_id, self.premium_plan.id)
        self.assertTrue(
            subscription.history.filter(
                action=SubscriptionHistory.Action.UPGRADED
            ).exists()
        )

    def test_customer_cannot_upgrade_to_lower_or_inactive_plan(self):
        subscription = self.create_subscription(
            plan=self.premium_plan
        )

        lower_plan_response = self.client.post(
            f"/api/subscriptions/{subscription.id}/upgrade/",
            {"plan": self.basic_plan.id},
            format="json",
        )
        self.assertEqual(lower_plan_response.status_code, 400)

        inactive_plan_response = self.client.post(
            f"/api/subscriptions/{subscription.id}/upgrade/",
            {"plan": self.inactive_plan.id},
            format="json",
        )
        self.assertEqual(inactive_plan_response.status_code, 400)

        subscription.refresh_from_db()
        self.assertEqual(subscription.plan_id, self.premium_plan.id)

    def test_customer_can_downgrade_subscription(self):
        subscription = self.create_subscription(
            plan=self.premium_plan
        )

        response = self.client.post(
            f"/api/subscriptions/{subscription.id}/downgrade/",
            {"plan": self.basic_plan.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        subscription.refresh_from_db()
        self.assertEqual(subscription.plan_id, self.basic_plan.id)
        self.assertTrue(
            subscription.history.filter(
                action=SubscriptionHistory.Action.DOWNGRADED
            ).exists()
        )

    def test_customer_can_cancel_subscription(self):
        subscription = self.create_subscription()

        response = self.client.post(
            f"/api/subscriptions/{subscription.id}/cancel/",
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        subscription.refresh_from_db()
        self.assertEqual(
            subscription.status,
            Subscription.Status.CANCELLED,
        )
        self.assertIsNotNone(subscription.end_date)
        self.assertTrue(
            subscription.history.filter(
                action=SubscriptionHistory.Action.CANCELLED
            ).exists()
        )

    def test_customer_cannot_cancel_subscription_twice(self):
        subscription = self.create_subscription(
            status=Subscription.Status.CANCELLED
        )

        response = self.client.post(
            f"/api/subscriptions/{subscription.id}/cancel/",
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_customer_cannot_modify_another_customers_subscription(self):
        other_subscription = self.create_subscription(
            customer=self.other_customer
        )

        response = self.client.post(
            f"/api/subscriptions/{other_subscription.id}/cancel/",
            format="json",
        )

        self.assertEqual(response.status_code, 404)

        other_subscription.refresh_from_db()
        self.assertEqual(
            other_subscription.status,
            Subscription.Status.TRIAL,
        )

    def test_unauthenticated_customer_cannot_list_subscriptions(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/subscriptions/")

        self.assertEqual(response.status_code, 401)
