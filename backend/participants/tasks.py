from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Participant, Winner


@shared_task
def send_verification_email(participant_id):
    """
    Tarea asíncrona para enviar email de verificación
    """
    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return f"Participant {participant_id} not found"

    # Construir URL de verificación
    verification_url = f"{settings.FRONTEND_URL}/verify/{participant.verification_token}"

    # Asunto del correo
    subject = 'Verifica tu correo - Sorteo San Valentín CTS Turismo'

    # Mensaje en texto plano
    message = f"""
    ¡Hola {participant.full_name}!

    Gracias por registrarte en el Sorteo de San Valentín de CTS Turismo.

    Para completar tu inscripción y participar por una estadía de 2 noches todo pagado
    para una pareja, necesitas verificar tu correo electrónico.

    Haz clic en el siguiente enlace para verificar tu cuenta:
    {verification_url}

    Una vez verificado, podrás crear tu contraseña y confirmar tu participación.

    ¡Mucha suerte!

    Equipo de CTS Turismo
    """

    # Enviar correo
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.email],
            fail_silently=False,
        )
        return f"Verification email sent to {participant.email}"
    except Exception as e:
        return f"Error sending email to {participant.email}: {str(e)}"


@shared_task
def send_winner_notification(winner_id):
    """
    Tarea asíncrona para notificar al ganador del sorteo
    """
    try:
        winner = Winner.objects.get(id=winner_id)
    except Winner.DoesNotExist:
        return f"Winner {winner_id} not found"

    participant = winner.participant

    # Asunto del correo
    subject = '🎉 ¡FELICITACIONES! Ganaste el Sorteo de San Valentín - CTS Turismo'

    # Mensaje en texto plano
    message = f"""
    ¡Hola {participant.full_name}!

    ¡FELICITACIONES! 🎉🎊

    Tenemos el placer de informarte que has sido seleccionado/a como GANADOR/A
    del Sorteo de San Valentín de CTS Turismo.

    Premio ganado:
    {winner.prize_description}

    Pronto nos pondremos en contacto contigo al teléfono {participant.phone}
    para coordinar los detalles de tu premio.

    ¡Que disfrutes mucho tu estadía romántica!

    Equipo de CTS Turismo
    www.ctsturismo.cl
    """

    # Enviar correo
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.email],
            fail_silently=False,
        )

        # Marcar como notificado
        winner.mark_as_notified()

        return f"Winner notification sent to {participant.email}"
    except Exception as e:
        return f"Error sending winner notification to {participant.email}: {str(e)}"
