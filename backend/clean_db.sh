#!/bin/bash

# Asegúrate de estar en la carpeta del manage.py
cd "$(dirname "$0")"

echo "Limpiando tablas Participant y Winner..."
python manage.py shell -c "from participants.models import Participant, Winner; Winner.objects.all().delete(); Participant.objects.all().delete()"
echo "Limpieza completada ✅"
