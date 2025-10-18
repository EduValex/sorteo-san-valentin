from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Participant, Winner


class ParticipantRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para el registro de nuevos participantes"""

    class Meta:
        model = Participant
        fields = ['email', 'full_name', 'phone']

    def validate_email(self, value):
        """Valida que el email no esté duplicado"""
        if Participant.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Este correo electrónico ya está registrado en el sorteo."
            )
        return value

    def validate_phone(self, value):
        """Valida formato básico de teléfono"""
        if not value.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise serializers.ValidationError(
                "El teléfono debe contener solo números, espacios, + o -"
            )
        return value


class SetPasswordSerializer(serializers.Serializer):
    """Serializer para establecer contraseña después de verificación"""

    verification_token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        """Valida la contraseña usando los validadores de Django"""
        validate_password(value)
        return value

    def validate(self, attrs):
        """Valida que las contraseñas coincidan"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs


class ParticipantSerializer(serializers.ModelSerializer):
    """Serializer completo para participantes"""

    can_participate = serializers.ReadOnlyField()

    class Meta:
        model = Participant
        fields = [
            'id', 'email', 'full_name', 'phone',
            'is_verified', 'verified_at', 'created_at',
            'can_participate'
        ]
        read_only_fields = ['id', 'is_verified', 'verified_at', 'created_at']


class ParticipantListSerializer(serializers.ModelSerializer):
    """Serializer para listado de participantes (admin)"""

    status = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ['id', 'email', 'full_name', 'phone', 'is_verified', 'created_at', 'status']
        read_only_fields = fields

    def get_status(self, obj):
        """Retorna el estado del participante"""
        if not obj.is_verified:
            return 'Pendiente de verificación'
        return 'Verificado'


class WinnerSerializer(serializers.ModelSerializer):
    """Serializer para ganadores"""

    participant_name = serializers.CharField(source='participant.full_name', read_only=True)
    participant_email = serializers.CharField(source='participant.email', read_only=True)
    participant_phone = serializers.CharField(source='participant.phone', read_only=True)
    drawn_by_name = serializers.CharField(source='drawn_by.full_name', read_only=True)

    class Meta:
        model = Winner
        fields = [
            'id', 'participant', 'participant_name', 'participant_email', 'participant_phone',
            'drawn_at', 'drawn_by', 'drawn_by_name',
            'notified', 'notified_at', 'prize_description'
        ]
        read_only_fields = ['id', 'drawn_at', 'notified', 'notified_at']


class LoginSerializer(serializers.Serializer):
    """Serializer para login de administrador"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer para verificar email con token"""

    token = serializers.UUIDField()
