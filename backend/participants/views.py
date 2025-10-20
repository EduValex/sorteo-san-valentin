from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q
import random

from .models import Participant, Winner
from .serializers import (
    ParticipantRegistrationSerializer,
    SetPasswordSerializer,
    ParticipantSerializer,
    ParticipantListSerializer,
    WinnerSerializer,
    LoginSerializer,
    VerifyEmailSerializer
)
# Importar tareas asíncronas de Celery (si las tienes)
from .tasks import send_verification_email, send_winner_notification
# Importar versiones síncronas como fallback
from .emails import send_verification_email_sync, send_winner_notification_sync


class IsAdmin(IsAdminUser):
    """Permiso personalizado para administradores"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


# ======================
# Endpoints públicos
# ======================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_participant(request):
    serializer = ParticipantRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        participant = serializer.save()
        send_verification_email_sync(participant.id)  # fallback síncrono
        return Response({
            'message': '¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.',
            'participant': {
                'email': participant.email,
                'full_name': participant.full_name
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    serializer = VerifyEmailSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        try:
            participant = Participant.objects.get(verification_token=token, is_verified=False)
        except Participant.DoesNotExist:
            return Response({'error': 'Token de verificación inválido o ya utilizado.'}, status=status.HTTP_400_BAD_REQUEST)

        participant.verify_email()
        return Response({
            'message': 'Email verificado exitosamente. Ahora puedes crear tu contraseña.',
            'participant': ParticipantSerializer(participant).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def set_password(request):
    serializer = SetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['verification_token']
        password = serializer.validated_data['password']
        try:
            participant = Participant.objects.get(verification_token=token, is_verified=True)
        except Participant.DoesNotExist:
            return Response({'error': 'Token inválido o email no verificado.'}, status=status.HTTP_400_BAD_REQUEST)

        participant.set_password(password)
        participant.save()
        return Response({
            'message': 'Tu cuenta ha sido activada. Ya estás participando en el sorteo.',
            'participant': ParticipantSerializer(participant).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ======================
# Login administrador
# ======================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_admin(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            participant = Participant.objects.get(email=email)
        except Participant.DoesNotExist:
            return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not participant.check_password(password):
            return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not participant.is_admin:
            return Response({'error': 'No tienes permisos de administrador.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(participant)
        return Response({
            'message': 'Inicio de sesión exitoso.',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': {
                'id': str(participant.id),
                'email': participant.email,
                'full_name': participant.full_name,
                'is_admin': participant.is_admin
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ======================
# ViewSets (admin)
# ======================

class ParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Participant.objects.filter(is_admin=False)
    serializer_class = ParticipantListSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'full_name', 'phone']
    ordering_fields = ['created_at', 'full_name', 'is_verified']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        is_verified = self.request.query_params.get('is_verified', None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = self.get_queryset().count()
        verified = self.get_queryset().filter(is_verified=True).count()
        pending = total - verified
        return Response({
            'total_participants': total,
            'verified': verified,
            'pending': pending,
            'eligible_for_draw': verified
        })


class WinnerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Winner.objects.all()
    serializer_class = WinnerSerializer
    permission_classes = [IsAdmin]
    ordering = ['-drawn_at']

    @action(detail=False, methods=['post'])
    def draw(self, request):
        eligible_participants = Participant.objects.filter(is_verified=True, is_active=True, is_admin=False)
        if not eligible_participants.exists():
            return Response({'error': 'No hay participantes elegibles para el sorteo.'}, status=status.HTTP_400_BAD_REQUEST)

        winner_participant = random.choice(list(eligible_participants))
        winner = Winner.objects.create(participant=winner_participant, drawn_by=request.user)

        try:
            send_winner_notification_sync(winner.id)
        except Exception as e:
            print(f"Error enviando notificación: {str(e)}")

        return Response({'message': '¡Ganador seleccionado exitosamente!', 'winner': WinnerSerializer(winner).data}, status=status.HTTP_201_CREATED)


# ======================
# Test SendGrid
# ======================

@api_view(['GET'])
@permission_classes([AllowAny])
def test_sendgrid(request):
    try:
        send_mail(
            subject='Prueba SendGrid Django',
            message='Este es un correo de prueba desde Render usando SendGrid.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        return Response({'message': 'Correo enviado correctamente!'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def clean_database(request):
    """Limpia participantes y ganadores"""
    Winner.objects.all().delete()
    Participant.objects.all().delete()
    return Response({"status": "ok", "message": "Tablas Participant y Winner limpiadas"})