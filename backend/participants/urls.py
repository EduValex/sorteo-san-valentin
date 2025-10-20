from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register_participant,
    verify_email,
    set_password,
    login_admin,
    test_sendgrid,
    clean_database,
    ParticipantViewSet,
    WinnerViewSet
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'admin/participants', ParticipantViewSet, basename='admin-participants')
router.register(r'admin/winners', WinnerViewSet, basename='admin-winners')

urlpatterns = [
    # Endpoints públicos de participantes
    path('participants/register/', register_participant, name='register'),
    path('participants/verify-email/', verify_email, name='verify-email'),
    path('participants/set-password/', set_password, name='set-password'),

    # Endpoint para limpiar base de datos (solo admin)
    path('clean-database/', clean_database, name='clean-database'),

    # Autenticación de administrador
    path('auth/login/', login_admin, name='admin-login'),

    # Test SendGrid
    path('test-sendgrid/', test_sendgrid, name='test-sendgrid'),

    # ViewSets (admin)
    path('', include(router.urls)),
]
