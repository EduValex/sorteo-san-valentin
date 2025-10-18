from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Participant, Winner


@admin.register(Participant)
class ParticipantAdmin(BaseUserAdmin):
    """Admin interface for Participant model"""

    list_display = ['email', 'full_name', 'phone', 'is_verified', 'is_admin', 'created_at']
    list_filter = ['is_verified', 'is_admin', 'is_active', 'created_at']
    search_fields = ['email', 'full_name', 'phone']
    ordering = ['-created_at']

    fieldsets = (
        ('Información Personal', {
            'fields': ('email', 'full_name', 'phone')
        }),
        ('Estado de Cuenta', {
            'fields': ('is_verified', 'verified_at', 'verification_token')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_admin', 'is_superuser')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'verified_at', 'verification_token']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'password1', 'password2', 'is_admin'),
        }),
    )


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    """Admin interface for Winner model"""

    list_display = ['get_participant_name', 'get_participant_email', 'drawn_at', 'notified', 'get_drawn_by']
    list_filter = ['notified', 'drawn_at']
    search_fields = ['participant__email', 'participant__full_name']
    ordering = ['-drawn_at']

    fieldsets = (
        ('Ganador', {
            'fields': ('participant', 'prize_description')
        }),
        ('Información del Sorteo', {
            'fields': ('drawn_at', 'drawn_by')
        }),
        ('Notificación', {
            'fields': ('notified', 'notified_at')
        }),
    )

    readonly_fields = ['drawn_at', 'notified_at']

    def get_participant_name(self, obj):
        return obj.participant.full_name
    get_participant_name.short_description = 'Nombre'

    def get_participant_email(self, obj):
        return obj.participant.email
    get_participant_email.short_description = 'Email'

    def get_drawn_by(self, obj):
        return obj.drawn_by.full_name if obj.drawn_by else '-'
    get_drawn_by.short_description = 'Sorteado por'
