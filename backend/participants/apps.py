from django.apps import AppConfig
import logging
import os
from django.db import connection, transaction

logger = logging.getLogger(__name__)

class ParticipantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'participants'

    def ready(self):
        # Solo limpiar en producción, no en dev
        if os.getenv('DEBUG', 'True') == 'False':
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        # Deshabilita temporalmente las restricciones FK
                        cursor.execute("SET session_replication_role = 'replica';")
                        
                        # Borra todo
                        cursor.execute("DELETE FROM participants_winner;")
                        cursor.execute("DELETE FROM participants_participant;")
                        
                        # Reactiva las restricciones FK
                        cursor.execute("SET session_replication_role = 'origin';")

                logger.info("Se limpiaron las tablas Participant y Winner correctamente (modo forzado).")
            except Exception as e:
                logger.warning(f"No se pudo limpiar las tablas: {e}")
