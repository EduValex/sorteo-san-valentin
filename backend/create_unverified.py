import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from participants.models import Participant
import uuid

# Crear participantes NO verificados
unverified_data = [
    {
        'full_name': 'Pedro Sanchez Rojas',
        'email': 'pedro.sanchez@gmail.com',
        'phone': '+56912345678',
    },
    {
        'full_name': 'Laura Diaz Munoz',
        'email': 'laura.diaz@outlook.com',
        'phone': '+56987654321',
    },
    {
        'full_name': 'Roberto Nunez Vargas',
        'email': 'roberto.nunez@yahoo.com',
        'phone': '+56911223344',
    },
]

print('=== CREANDO PARTICIPANTES NO VERIFICADOS ===')
for data in unverified_data:
    participant = Participant.objects.create(
        email=data['email'],
        full_name=data['full_name'],
        phone=data['phone'],
        is_verified=False,  # IMPORTANTE: NO VERIFICADOS
        verification_token=str(uuid.uuid4()),
    )
    print(f'Creado NO VERIFICADO: {participant.full_name} ({participant.email})')

print('')
print('=== RESUMEN FINAL ===')
all_participants = Participant.objects.filter(is_admin=False)
print(f'Total participantes: {all_participants.count()}')
print(f'Verificados: {all_participants.filter(is_verified=True).count()}')
print(f'NO verificados: {all_participants.filter(is_verified=False).count()}')
