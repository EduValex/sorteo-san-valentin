import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from participants.models import Participant, Winner
from participants.emails import send_winner_notification_sync
import random

print('=== PRUEBA DE SORTEO ===')

# Obtener participantes elegibles
eligible_participants = Participant.objects.filter(
    is_verified=True,
    is_active=True,
    is_admin=False
)

print(f'Participantes elegibles: {eligible_participants.count()}')
for p in eligible_participants:
    print(f'  - {p.full_name} ({p.email})')

print('')

# Obtener admin
admin = Participant.objects.filter(is_admin=True).first()
print(f'Admin: {admin.full_name}')

print('')
print('Realizando sorteo...')

# Seleccionar ganador aleatorio
winner_participant = random.choice(list(eligible_participants))
print(f'Ganador seleccionado: {winner_participant.full_name}')

# Crear registro de ganador
try:
    winner = Winner.objects.create(
        participant=winner_participant,
        drawn_by=admin
    )
    print(f'Registro de ganador creado con ID: {winner.id}')

    # Intentar enviar email
    print('Intentando enviar email...')
    result = send_winner_notification_sync(winner.id)

    if result:
        print('Email enviado exitosamente!')
    else:
        print('Error al enviar email')

except Exception as e:
    print(f'ERROR: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()
