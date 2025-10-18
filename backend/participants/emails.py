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

        subject = 'Verifica tu email - Sorteo San Valentin'
        message = f"""
Hola {participant.full_name}!

Gracias por registrarte en el Sorteo de San Valentin de CTS Turismo.

Para completar tu registro y participar en el sorteo de una estadia romantica
de 2 noches para pareja, por favor verifica tu correo haciendo clic en el
siguiente enlace:

{verification_link}

Una vez verificado tu correo, podras crear tu contrasena y confirmar tu
participacion.

Mucha suerte!

---
CTS Turismo
Sorteo San Valentin 2025
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.email],
            fail_silently=False,
        )

        print(f"[OK] Email de verificacion enviado a: {participant.email}")
        return True

    except Participant.DoesNotExist:
        print(f"[ERROR] Participante {participant_id} no encontrado")
        return False
    except Exception as e:
        print(f"[ERROR] Error enviando email: {str(e)}")
        return False


def send_winner_notification_sync(winner_id):
    """
    Envía notificación al ganador de forma síncrona (sin Celery)
    """
    try:
        winner = Winner.objects.get(id=winner_id)
        participant = winner.participant

        subject = 'FELICITACIONES! Eres el ganador del Sorteo San Valentin'
        message = f"""
FELICITACIONES {participant.full_name}!

Has ganado el Sorteo de San Valentin de CTS Turismo!

Tu premio:
- Estadia de 2 noches todo incluido para pareja
- Hotel seleccionado para una experiencia romantica inolvidable

Proximos pasos:
Nos pondremos en contacto contigo en las proximas 24-48 horas al telefono
{participant.phone} para coordinar los detalles de tu premio.

Disfruta de tu premio y feliz San Valentin!

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

        print(f"[OK] Email de ganador enviado a: {participant.email}")
        return True

    except Winner.DoesNotExist:
        print(f"[ERROR] Ganador {winner_id} no encontrado")
        return False
    except Exception as e:
        print(f"[ERROR] Error enviando email: {str(e)}")
        return False
