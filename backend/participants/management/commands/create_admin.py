"""
Management command to create an admin user
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from participants.models import Participant


class Command(BaseCommand):
    help = 'Creates an admin user for the raffle system'

    def handle(self, *args, **kwargs):
        email = 'admin@ctsturismo.cl'
        password = 'admin123'
        full_name = 'Administrador CTS'
        phone = '+56912345678'

        # Check if admin already exists
        if Participant.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user {email} already exists!')
            )
            return

        # Create admin user
        admin = Participant.objects.create_user(
            email=email,
            full_name=full_name,
            phone=phone,
            password=password
        )

        # Mark as admin, verified, and superuser
        admin.is_admin = True
        admin.is_verified = True
        admin.is_superuser = True
        admin.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nAdmin user created successfully!\n'
                f'  Email: {email}\n'
                f'  Password: {password}\n'
                f'  Full Name: {full_name}\n'
                f'\nUse these credentials to login to the admin panel.\n'
            )
        )
