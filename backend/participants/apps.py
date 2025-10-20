from django.apps import AppConfig
from django.db import connection

class ParticipantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'participants'

    def ready(self):
        """
        Limpia automáticamente la tabla de participantes al iniciar la app.
        Se ejecuta tanto en desarrollo como en producción (Render).
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM participants_participant;')
            print("✅ Todos los participantes fueron eliminados automáticamente.")
        except Exception as e:
            print(f"⚠️ No se pudo limpiar la tabla de participantes: {e}")
