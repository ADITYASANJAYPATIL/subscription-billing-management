from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Create the application roles."

    def handle(self, *args, **options):
        customer_group, customer_created = Group.objects.get_or_create(
            name="Customer"
        )

        admin_group, admin_created = Group.objects.get_or_create(
            name="Admin"
        )

        if customer_created:
            self.stdout.write(
                self.style.SUCCESS("Created Customer role.")
            )
        else:
            self.stdout.write("Customer role already exists.")

        if admin_created:
            self.stdout.write(
                self.style.SUCCESS("Created Admin role.")
            )
        else:
            self.stdout.write("Admin role already exists.")

        self.stdout.write(
            self.style.SUCCESS("Role setup completed.")
        )