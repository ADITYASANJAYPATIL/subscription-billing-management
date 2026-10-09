from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework.test import APIClient

from plans.models import SubscriptionPlan


class SubscriptionPlanAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer_group, _ = Group.objects.get_or_create(
            name="Customer"
        )
        self.admin_group, _ = Group.objects.get_or_create(
            name="Admin"
        )

        self.customer_user = User.objects.create_user(
            username="plans_customer",
            password="test-password-123",
        )
        self.customer_user.groups.add(self.customer_group)

        self.admin_user = User.objects.create_user(
            username="plans_admin",
            password="test-password-123",
        )
        self.admin_user.groups.add(self.admin_group)

        self.active_plan = SubscriptionPlan.objects.create(
            name="Basic Test Plan",
            description="Active plan for testing",
            price=Decimal("499.00"),
            billing_cycle=SubscriptionPlan.BillingCycle.MONTHLY,
            is_active=True,
        )

        self.inactive_plan = SubscriptionPlan.objects.create(
            name="Inactive Test Plan",
            description="Inactive plan for testing",
            price=Decimal("999.00"),
            billing_cycle=SubscriptionPlan.BillingCycle.MONTHLY,
            is_active=False,
        )

    def test_customer_can_list_only_active_plans(self):
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get("/api/plans/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.active_plan.id)

    def test_admin_can_list_active_and_inactive_plans(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get("/api/plans/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_user_cannot_list_plans(self):
        response = self.client.get("/api/plans/")

        self.assertEqual(response.status_code, 401)

    def test_admin_can_create_plan(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            "/api/plans/",
            {
                "name": "Premium Test Plan",
                "description": "Premium plan",
                "price": "1499.00",
                "billing_cycle": "MONTHLY",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            SubscriptionPlan.objects.filter(
                name="Premium Test Plan"
            ).exists()
        )

    def test_customer_cannot_create_plan(self):
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            "/api/plans/",
            {
                "name": "Unauthorized Plan",
                "description": "Should not be created",
                "price": "299.00",
                "billing_cycle": "MONTHLY",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            SubscriptionPlan.objects.filter(
                name="Unauthorized Plan"
            ).exists()
        )

    def test_customer_cannot_view_inactive_plan_detail(self):
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(
            f"/api/plans/{self.inactive_plan.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_update_plan(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(
            f"/api/plans/{self.active_plan.id}/",
            {"price": "599.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.active_plan.refresh_from_db()
        self.assertEqual(self.active_plan.price, Decimal("599.00"))

    def test_customer_cannot_update_plan(self):
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.patch(
            f"/api/plans/{self.active_plan.id}/",
            {"price": "1.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

        self.active_plan.refresh_from_db()
        self.assertEqual(self.active_plan.price, Decimal("499.00"))

    def test_admin_delete_deactivates_plan_instead_of_removing_it(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(
            f"/api/plans/{self.active_plan.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.active_plan.refresh_from_db()
        self.assertFalse(self.active_plan.is_active)
        self.assertTrue(
            SubscriptionPlan.objects.filter(
                id=self.active_plan.id
            ).exists()
        )

    def test_customer_cannot_delete_plan(self):
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.delete(
            f"/api/plans/{self.active_plan.id}/"
        )

        self.assertEqual(response.status_code, 403)

        self.active_plan.refresh_from_db()
        self.assertTrue(self.active_plan.is_active)
