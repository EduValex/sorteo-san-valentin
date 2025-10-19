import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from participants.models import Winner

print('=== LIMPIANDO HISTORIAL DE GANADORES ===')
count = Winner.objects.count()
Winner.objects.all().delete()
print(f'Eliminados {count} ganadores del historial')
print('Historial limpio! Listo para probar desde cero.')
