from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'admin/participants', views.ParticipantViewSet, basename='admin-participants')
router.register(r'admin/winners', views.WinnerViewSet, basename='admin-winners')

urlpatterns = [
    # Endpoints públicos de participantes
    path('participants/register/', views.register_participant, name='register'),
    path('participants/verify-email/', views.verify_email, name='verify-email'),
    path('participants/set-password/', views.set_password, name='set-password'),

    # Autenticación de administrador
    path('auth/login/', views.login_admin, name='admin-login'),

    # ViewSets (admin)
    path('', include(router.urls)),
]
