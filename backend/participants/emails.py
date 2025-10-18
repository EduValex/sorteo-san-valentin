"""
Funciones para envío de emails (sin Celery - modo síncrono)
"""
from django.core.mail import send_mail
from django.conf import settings
from .models import Participant, Winner


def send_verification_email_sync(participant_id):
    """
    Envía email de verificación de forma síncrona (sin Celery)
    """
    try:
        participant = Participant.objects.get(id=participant_id)

        verification_link = f"{settings.FRONTEND_URL}/verify/{participant.verification_token}"

        subject = '🎉 Verifica tu email - Sorteo San Valentín'
        message = f"""
¡Hola {participant.full_name}!

Gracias por registrarte en el Sorteo de San Valentín de CTS Turismo.

Para completar tu registro y participar en el sorteo de una estadía romántica
de 2 noches para pareja, por favor verifica tu correo haciendo clic en el
siguiente enlace:

{verification_link}

Una vez verificado tu correo, podrás crear tu contraseña y confirmar tu
participación.

¡Mucha suerte!

---
CTS Turismo
Sorteo San Valentín 2025
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.email],
            fail_silently=False,
        )

        print(f"✓ Email de verificación enviado a: {participant.email}")
        return True

    except Participant.DoesNotExist:
        print(f"✗ Participante {participant_id} no encontrado")
        return False
    except Exception as e:
        print(f"✗ Error enviando email: {str(e)}")
        return False


def send_winner_notification_sync(winner_id):
    """
    Envía notificación al ganador de forma síncrona (sin Celery)
    """
    try:
        winner = Winner.objects.get(id=winner_id)
        participant = winner.participant

        subject = '🏆 ¡FELICITACIONES! Eres el ganador del Sorteo San Valentín'
        message = f"""
¡FELICITACIONES {participant.full_name}!

🎉 ¡Has ganado el Sorteo de San Valentín de CTS Turismo! 🎉

Tu premio:
🏨 Estadía de 2 noches todo incluido para pareja
💑 Hotel seleccionado para una experiencia romántica inolvidable

Próximos pasos:
Nos pondremos en contacto contigo en las próximas 24-48 horas al teléfono
{participant.phone} para coordinar los detalles de tu premio.

¡Disfruta de tu premio y feliz San Valentín!

---
CTS Turismo
Equipo de Sorteos
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.email],
            fail_silently=False,
        )

        # Marcar como notificado
        winner.notified = True
        winner.save()

        print(f"✓ Email de ganador enviado a: {participant.email}")
        return True

    except Winner.DoesNotExist:
        print(f"✗ Ganador {winner_id} no encontrado")
        return False
    except Exception as e:
        print(f"✗ Error enviando email: {str(e)}")
        return False
