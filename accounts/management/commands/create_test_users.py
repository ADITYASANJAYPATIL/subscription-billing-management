from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create development test users for Admin and Customer roles."

    def handle(self, *args, **options):
        admin_group = Group.objects.get(name="Admin")
        customer_group = Group.objects.get(name="Customer")

        admin_user, admin_created = User.objects.get_or_create(
            username="admin_test",
            defaults={
                "email": "admin_test@example.com",
                "first_name": "Admin",
            },
        )

        if admin_created:
            admin_user.set_password("AdminTest@123")
            admin_user.save()

        admin_user.groups.add(admin_group)

        customer_user, customer_created = User.objects.get_or_create(
            username="customer_test",
            defaults={
                "email": "customer_test@example.com",
                "first_name": "Customer",
            },
        )

        if customer_created:
            customer_user.set_password("CustomerTest@123")
            customer_user.save()

        customer_user.groups.add(customer_group)

        self.stdout.write(
            self.style.SUCCESS(
                "Development test users created/configured successfully."
            )
        )