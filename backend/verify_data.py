import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from participants.models import Participant

print('=== PARTICIPANTES ACTUALES ===')
participants = Participant.objects.filter(is_admin=False)
print(f'Total participantes: {participants.count()}')
print(f'Verificados: {participants.filter(is_verified=True).count()}')
print(f'No verificados: {participants.filter(is_verified=False).count()}')
print('')

print('Detalle:')
for p in participants:
    status = 'VERIFICADO' if p.is_verified else 'NO VERIFICADO'
    print(f'  - {p.full_name} ({p.email}): {status}')
