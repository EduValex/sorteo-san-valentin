import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from participants.models import Participant, Winner

# Mostrar estado actual
print('=== ESTADO ACTUAL ===')
print(f'Total participantes: {Participant.objects.count()}')
print(f'Admin: {Participant.objects.filter(is_admin=True).count()}')
print(f'Participantes regulares: {Participant.objects.filter(is_admin=False).count()}')
print(f'Total ganadores: {Winner.objects.count()}')
print('')

# Limpiar datos
print('=== LIMPIANDO BASE DE DATOS ===')

# Eliminar ganadores
winners_count = Winner.objects.count()
Winner.objects.all().delete()
print(f'Eliminados {winners_count} ganadores')

# Eliminar participantes (excepto admin)
participants_count = Participant.objects.filter(is_admin=False).count()
Participant.objects.filter(is_admin=False).delete()
print(f'Eliminados {participants_count} participantes (admin mantenido)')
print('')
print('Base de datos limpia!')
