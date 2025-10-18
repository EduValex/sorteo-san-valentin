"""
Management command to create fake participants for testing
Usage: python manage.py create_fake_participants
"""
from django.core.management.base import BaseCommand
from participants.models import Participant


class Command(BaseCommand):
    help = 'Creates fake verified participants for testing the raffle'

    def handle(self, *args, **kwargs):
        fake_participants = [
            {
                'email': 'maria.gonzalez@gmail.com',
                'full_name': 'María González Pérez',
                'phone': '+56987654321',
                'password': 'password123'
            },
            {
                'email': 'carlos.rodriguez@outlook.com',
                'full_name': 'Carlos Rodríguez Silva',
                'phone': '+56912345678',
                'password': 'password123'
            },
            {
                'email': 'sofia.martinez@yahoo.com',
                'full_name': 'Sofía Martínez López',
                'phone': '+56923456789',
                'password': 'password123'
            },
            {
                'email': 'diego.fernandez@gmail.com',
                'full_name': 'Diego Fernández Castro',
                'phone': '+56934567890',
                'password': 'password123'
            },
            {
                'email': 'valentina.torres@hotmail.com',
                'full_name': 'Valentina Torres Ramírez',
                'phone': '+56945678901',
                'password': 'password123'
            },
            {
                'email': 'sebastian.morales@gmail.com',
                'full_name': 'Sebastián Morales Herrera',
                'phone': '+56956789012',
                'password': 'password123'
            },
        ]

        created_count = 0

        for participant_data in fake_participants:
            email = participant_data['email']

            # Check if participant already exists
            if Participant.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'Participant {email} already exists, skipping...')
                )
                continue

            # Create participant
            participant = Participant.objects.create_user(
                email=email,
                full_name=participant_data['full_name'],
                phone=participant_data['phone'],
                password=participant_data['password']
            )

            # Mark as verified
            participant.is_verified = True
            participant.save()

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created: {participant.full_name} ({email})')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal: {created_count} fake participants created successfully!'
            )
        )
