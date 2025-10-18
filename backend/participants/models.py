from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class ParticipantManager(BaseUserManager):
    """Manager personalizado para el modelo Participant"""

    def create_user(self, email, full_name, phone, password=None):
        """Crea y retorna un participante regular"""
        if not email:
            raise ValueError('El email es obligatorio')

        email = self.normalize_email(email)
        participant = self.model(
            email=email,
            full_name=full_name,
            phone=phone
        )

        if password:
            participant.set_password(password)

        participant.save(using=self._db)
        return participant

    def create_superuser(self, email, full_name, phone, password=None):
        """Crea y retorna un administrador"""
        participant = self.create_user(
            email=email,
            full_name=full_name,
            phone=phone,
            password=password
        )
        participant.is_admin = True
        participant.is_staff = True
        participant.is_superuser = True
        participant.is_verified = True
        participant.save(using=self._db)
        return participant


class Participant(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Participante del Sorteo de San Valentín
    Maneja tanto participantes como administradores
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name='correo electrónico',
        max_length=255,
        unique=True,
        db_index=True
    )
    full_name = models.CharField('nombre completo', max_length=200)
    phone = models.CharField('teléfono', max_length=20)

    # Control de verificación
    is_verified = models.BooleanField('verificado', default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    verified_at = models.DateTimeField('verificado el', null=True, blank=True)

    # Permisos y roles
    is_active = models.BooleanField('activo', default=True)
    is_staff = models.BooleanField('staff', default=False)
    is_admin = models.BooleanField('administrador', default=False)

    # Fechas
    created_at = models.DateTimeField('creado el', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado el', auto_now=True)

    # Configuración del manager
    objects = ParticipantManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    class Meta:
        verbose_name = 'participante'
        verbose_name_plural = 'participantes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def verify_email(self):
        """Marca el email como verificado"""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'verified_at'])

    @property
    def can_participate(self):
        """Verifica si el participante puede estar en el sorteo"""
        return self.is_verified and self.is_active and not self.is_admin


class Winner(models.Model):
    """
    Modelo para registrar ganadores del sorteo
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='wins',
        verbose_name='participante ganador'
    )

    # Información del sorteo
    drawn_at = models.DateTimeField('sorteado el', auto_now_add=True)
    drawn_by = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        related_name='draws_made',
        verbose_name='sorteado por'
    )

    # Control de notificación
    notified = models.BooleanField('notificado', default=False)
    notified_at = models.DateTimeField('notificado el', null=True, blank=True)

    # Premio
    prize_description = models.TextField(
        'descripción del premio',
        default='Estadía de 2 noches todo pagado para pareja en hotel'
    )

    class Meta:
        verbose_name = 'ganador'
        verbose_name_plural = 'ganadores'
        ordering = ['-drawn_at']

    def __str__(self):
        return f"Ganador: {self.participant.full_name} - {self.drawn_at.strftime('%d/%m/%Y')}"

    def mark_as_notified(self):
        """Marca al ganador como notificado"""
        self.notified = True
        self.notified_at = timezone.now()
        self.save(update_fields=['notified', 'notified_at'])
