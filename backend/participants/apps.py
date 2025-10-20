from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)

class ParticipantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'participants'

    def ready(self):
        # Solo limpiar en producción, no en dev
        if os.getenv('DEBUG', 'True') == 'False':
            try:
                from participants.models import Participant, Winner

                # Borrar primero los ganadores para evitar errores de FK
                Winner.objects.all().delete()
                Participant.objects.all().delete()

                logger.info("Se limpiaron las tablas Participant y Winner correctamente.")
            except Exception as e:
                logger.warning(f"No se pudo limpiar la tabla de participantes: {e}")
