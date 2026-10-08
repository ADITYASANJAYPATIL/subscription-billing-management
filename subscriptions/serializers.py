from rest_framework import serializers

from plans.models import SubscriptionPlan
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id",
            "customer",
            "plan",
            "status",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer",
            "status",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]

    def validate_plan(self, plan):
        if not plan.is_active:
            raise serializers.ValidationError(
                "Selected plan is not active."
            )

        return plan
    