"""
Tests para la aplicación de participantes del Sorteo San Valentín
"""
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from .models import Participant, Winner


class ParticipantModelTests(TestCase):
    """Tests para el modelo Participant"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.participant_data = {
            'email': 'test@example.com',
            'full_name': 'Juan Pérez',
            'phone': '+56912345678'
        }

    def test_create_participant(self):
        """Test: crear un participante correctamente"""
        participant = Participant.objects.create_user(**self.participant_data)

        self.assertEqual(participant.email, self.participant_data['email'])
        self.assertEqual(participant.full_name, self.participant_data['full_name'])
        self.assertEqual(participant.phone, self.participant_data['phone'])
        self.assertFalse(participant.is_verified)
        self.assertFalse(participant.is_admin)
        self.assertTrue(participant.is_active)
        self.assertIsNotNone(participant.verification_token)

    def test_create_superuser(self):
        """Test: crear un superusuario/administrador"""
        admin = Participant.objects.create_superuser(
            email='admin@ctsturismo.cl',
            full_name='Admin CTS',
            phone='+56900000000',
            password='admin123'
        )

        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_verified)

    def test_participant_str_method(self):
        """Test: método __str__ del participante"""
        participant = Participant.objects.create_user(**self.participant_data)
        expected_str = f"{self.participant_data['full_name']} ({self.participant_data['email']})"
        self.assertEqual(str(participant), expected_str)

    def test_verify_email_method(self):
        """Test: método verify_email marca correctamente el participante como verificado"""
        participant = Participant.objects.create_user(**self.participant_data)
        self.assertFalse(participant.is_verified)
        self.assertIsNone(participant.verified_at)

        participant.verify_email()

        self.assertTrue(participant.is_verified)
        self.assertIsNotNone(participant.verified_at)

    def test_can_participate_property(self):
        """Test: propiedad can_participate retorna correctamente"""
        # Participante sin verificar
        participant = Participant.objects.create_user(**self.participant_data)
        self.assertFalse(participant.can_participate)

        # Participante verificado
        participant.verify_email()
        self.assertTrue(participant.can_participate)

        # Participante inactivo
        participant.is_active = False
        participant.save()
        self.assertFalse(participant.can_participate)

        # Admin no puede participar
        admin = Participant.objects.create_superuser(
            email='admin@test.com',
            full_name='Admin',
            phone='+56900000000',
            password='test123'
        )
        self.assertFalse(admin.can_participate)

    def test_email_unique_constraint(self):
        """Test: el email debe ser único"""
        Participant.objects.create_user(**self.participant_data)

        with self.assertRaises(Exception):
            Participant.objects.create_user(**self.participant_data)

    def test_uuid_primary_key(self):
        """Test: el ID es un UUID válido"""
        participant = Participant.objects.create_user(**self.participant_data)
        self.assertIsInstance(participant.id, uuid.UUID)


class WinnerModelTests(TestCase):
    """Tests para el modelo Winner"""

    def setUp(self):
        """Configuración inicial"""
        self.participant = Participant.objects.create_user(
            email='winner@example.com',
            full_name='Ganador Prueba',
            phone='+56912345678'
        )
        self.participant.verify_email()

        self.admin = Participant.objects.create_superuser(
            email='admin@ctsturismo.cl',
            full_name='Admin CTS',
            phone='+56900000000',
            password='admin123'
        )

    def test_create_winner(self):
        """Test: crear un ganador correctamente"""
        winner = Winner.objects.create(
            participant=self.participant,
            drawn_by=self.admin
        )

        self.assertEqual(winner.participant, self.participant)
        self.assertEqual(winner.drawn_by, self.admin)
        self.assertFalse(winner.notified)
        self.assertIsNone(winner.notified_at)
        self.assertIsNotNone(winner.prize_description)
        self.assertIsNotNone(winner.drawn_at)

    def test_mark_as_notified_method(self):
        """Test: método mark_as_notified funciona correctamente"""
        winner = Winner.objects.create(
            participant=self.participant,
            drawn_by=self.admin
        )

        self.assertFalse(winner.notified)
        self.assertIsNone(winner.notified_at)

        winner.mark_as_notified()

        self.assertTrue(winner.notified)
        self.assertIsNotNone(winner.notified_at)

    def test_winner_str_method(self):
        """Test: método __str__ del ganador"""
        winner = Winner.objects.create(
            participant=self.participant,
            drawn_by=self.admin
        )

        self.assertIn(self.participant.full_name, str(winner))


class ParticipantRegistrationAPITests(APITestCase):
    """Tests para el endpoint de registro de participantes"""

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_data = {
            'email': 'nuevo@example.com',
            'full_name': 'Nuevo Participante',
            'phone': '+56912345678'
        }

    def test_register_participant_success(self):
        """Test: registro exitoso de participante"""
        response = self.client.post(self.register_url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('participant', response.data)
        self.assertEqual(response.data['participant']['email'], self.valid_data['email'])

        # Verificar que se creó en la BD
        self.assertTrue(Participant.objects.filter(email=self.valid_data['email']).exists())

        # Verificar que se envió el email (en test mode)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.valid_data['full_name'], mail.outbox[0].body)

    def test_register_duplicate_email(self):
        """Test: no se permite registro con email duplicado"""
        # Crear primer participante
        Participant.objects.create_user(**self.valid_data)

        # Intentar registrar con mismo email
        response = self.client.post(self.register_url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_invalid_email(self):
        """Test: validación de formato de email"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'email-invalido'

        response = self.client.post(self.register_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_phone(self):
        """Test: validación de formato de teléfono"""
        invalid_data = self.valid_data.copy()
        invalid_data['phone'] = 'abc123xyz'

        response = self.client.post(self.register_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)

    def test_register_missing_fields(self):
        """Test: campos requeridos"""
        response = self.client.post(self.register_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('full_name', response.data)
        self.assertIn('phone', response.data)


class EmailVerificationAPITests(APITestCase):
    """Tests para verificación de email"""

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.verify_url = reverse('verify-email')

        self.participant = Participant.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            phone='+56912345678'
        )
        self.token = self.participant.verification_token

    def test_verify_email_success(self):
        """Test: verificación exitosa de email"""
        response = self.client.post(
            self.verify_url,
            {'token': str(self.token)},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('participant', response.data)

        # Verificar que se actualizó en BD
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.is_verified)
        self.assertIsNotNone(self.participant.verified_at)

    def test_verify_email_invalid_token(self):
        """Test: token inválido"""
        invalid_token = uuid.uuid4()
        response = self.client.post(
            self.verify_url,
            {'token': str(invalid_token)},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_verify_email_already_verified(self):
        """Test: no se puede verificar dos veces con el mismo token"""
        # Primera verificación
        self.client.post(
            self.verify_url,
            {'token': str(self.token)},
            format='json'
        )

        # Segunda verificación con mismo token
        response = self.client.post(
            self.verify_url,
            {'token': str(self.token)},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SetPasswordAPITests(APITestCase):
    """Tests para establecer contraseña"""

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.set_password_url = reverse('set-password')

        self.participant = Participant.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            phone='+56912345678'
        )
        self.participant.verify_email()
        self.token = self.participant.verification_token

    def test_set_password_success(self):
        """Test: establecer contraseña exitosamente"""
        response = self.client.post(
            self.set_password_url,
            {
                'verification_token': str(self.token),
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # Verificar que se guardó la contraseña
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.check_password('SecurePass123!'))

    def test_set_password_mismatch(self):
        """Test: contraseñas no coinciden"""
        response = self.client.post(
            self.set_password_url,
            {
                'verification_token': str(self.token),
                'password': 'SecurePass123!',
                'password_confirm': 'DifferentPass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_set_password_not_verified(self):
        """Test: no se puede establecer contraseña si no está verificado"""
        unverified = Participant.objects.create_user(
            email='unverified@example.com',
            full_name='Unverified User',
            phone='+56900000000'
        )

        response = self.client.post(
            self.set_password_url,
            {
                'verification_token': str(unverified.verification_token),
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminLoginAPITests(APITestCase):
    """Tests para login de administrador"""

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.login_url = reverse('admin-login')

        self.admin = Participant.objects.create_superuser(
            email='admin@ctsturismo.cl',
            full_name='Admin CTS',
            phone='+56900000000',
            password='admin123'
        )

    def test_admin_login_success(self):
        """Test: login exitoso de administrador"""
        response = self.client.post(
            self.login_url,
            {
                'email': 'admin@ctsturismo.cl',
                'password': 'admin123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)
        self.assertTrue(response.data['user']['is_admin'])

    def test_admin_login_invalid_credentials(self):
        """Test: credenciales incorrectas"""
        response = self.client.post(
            self.login_url,
            {
                'email': 'admin@ctsturismo.cl',
                'password': 'wrongpassword'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_cannot_login(self):
        """Test: usuario regular no puede hacer login como admin"""
        regular_user = Participant.objects.create_user(
            email='user@example.com',
            full_name='Regular User',
            phone='+56912345678',
            password='userpass123'
        )

        response = self.client.post(
            self.login_url,
            {
                'email': 'user@example.com',
                'password': 'userpass123'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ParticipantListAPITests(APITestCase):
    """Tests para listado de participantes (admin)"""

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.participants_url = reverse('admin-participants-list')

        # Crear admin
        self.admin = Participant.objects.create_superuser(
            email='admin@ctsturismo.cl',
            full_name='Admin CTS',
            phone='+56900000000',
            password='admin123'
        )

        # Crear participantes de prueba
        for i in range(5):
            participant = Participant.objects.create_user(
                email=f'participant{i}@example.com',
                full_name=f'Participante {i}',
                phone=f'+5691234567{i}'
            )
            if i % 2 == 0:  # Verificar solo algunos
                participant.verify_email()

    def test_list_participants_requires_authentication(self):
        """Test: requiere autenticación"""
        response = self.client.get(self.participants_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_participants_requires_admin(self):
        """Test: requiere permisos de admin"""
        # Crear usuario regular
        regular_user = Participant.objects.create_user(
            email='user@example.com',
            full_name='Regular User',
            phone='+56900000000',
            password='userpass123'
        )

        # Autenticar como usuario regular
        refresh = RefreshToken.for_user(regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(self.participants_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_participants_as_admin(self):
        """Test: admin puede listar participantes"""
        # Autenticar como admin
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(self.participants_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 5)

    def test_filter_participants_by_verified(self):
        """Test: filtrar participantes por estado de verificación"""
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Filtrar solo verificados
        response = self.client.get(f'{self.participants_url}?is_verified=true')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verified_count = len([p for p in response.data['results']])
        self.assertEqual(verified_count, 3)  # 3 participantes verificados (índices 0, 2, 4)

    def test_search_participants(self):
        """Test: buscar participantes por nombre/email"""
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(f'{self.participants_url}?search=Participante 0')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_participants_stats(self):
        """Test: obtener estadísticas de participantes"""
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        stats_url = reverse('admin-participants-stats')
        response = self.client.get(stats_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_participants', response.data)
        self.assertIn('verified', response.data)
        self.assertIn('pending', response.data)
        self.assertIn('eligible_for_draw', response.data)

        self.assertEqual(response.data['total_participants'], 5)
        self.assertEqual(response.data['verified'], 3)
        self.assertEqual(response.data['pending'], 2)


class WinnerDrawAPITests(APITestCase):
    """Tests para el sorteo de ganador"""

    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.draw_url = reverse('admin-winners-draw')

        # Crear admin
        self.admin = Participant.objects.create_superuser(
            email='admin@ctsturismo.cl',
            full_name='Admin CTS',
            phone='+56900000000',
            password='admin123'
        )

        # Crear participantes verificados
        for i in range(3):
            participant = Participant.objects.create_user(
                email=f'participant{i}@example.com',
                full_name=f'Participante {i}',
                phone=f'+5691234567{i}'
            )
            participant.verify_email()

    def test_draw_requires_authentication(self):
        """Test: sorteo requiere autenticación"""
        response = self.client.post(self.draw_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_draw_requires_admin(self):
        """Test: sorteo requiere permisos de admin"""
        regular_user = Participant.objects.create_user(
            email='user@example.com',
            full_name='Regular User',
            phone='+56900000000',
            password='userpass123'
        )

        refresh = RefreshToken.for_user(regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.post(self.draw_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_draw_winner_success(self):
        """Test: sorteo exitoso de ganador"""
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.post(self.draw_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('winner', response.data)

        # Verificar que se creó el ganador
        self.assertEqual(Winner.objects.count(), 1)
        winner = Winner.objects.first()
        self.assertIsNotNone(winner.participant)
        self.assertEqual(winner.drawn_by, self.admin)

        # Verificar que se envió email (en test mode)
        self.assertEqual(len(mail.outbox), 1)

    def test_draw_no_eligible_participants(self):
        """Test: error si no hay participantes elegibles"""
        # Eliminar todos los participantes
        Participant.objects.filter(is_admin=False).delete()

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.post(self.draw_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_list_winners(self):
        """Test: listar ganadores"""
        # Crear un ganador
        participant = Participant.objects.filter(is_admin=False).first()
        Winner.objects.create(
            participant=participant,
            drawn_by=self.admin
        )

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        winners_url = reverse('admin-winners-list')
        response = self.client.get(winners_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIn('participant_name', response.data['results'][0])
        self.assertIn('participant_email', response.data['results'][0])


class IntegrationTests(APITestCase):
    """Tests de integración para el flujo completo"""

    def test_complete_participant_flow(self):
        """Test: flujo completo de participante desde registro hasta sorteo"""

        # 1. Registro
        register_url = reverse('register')
        register_data = {
            'email': 'flujo@example.com',
            'full_name': 'Usuario Flujo Completo',
            'phone': '+56912345678'
        }

        response = self.client.post(register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Obtener participante
        participant = Participant.objects.get(email=register_data['email'])
        self.assertFalse(participant.is_verified)

        # 2. Verificar email
        verify_url = reverse('verify-email')
        response = self.client.post(
            verify_url,
            {'token': str(participant.verification_token)},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Establecer contraseña
        set_password_url = reverse('set-password')
        response = self.client.post(
            set_password_url,
            {
                'verification_token': str(participant.verification_token),
                'password': 'MiPassword123!',
                'password_confirm': 'MiPassword123!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que el participante está listo
        participant.refresh_from_db()
        self.assertTrue(participant.is_verified)
        self.assertTrue(participant.can_participate)
        self.assertTrue(participant.check_password('MiPassword123!'))

        # 4. Admin realiza sorteo
        admin = Participant.objects.create_superuser(
            email='admin@ctsturismo.cl',
            full_name='Admin CTS',
            phone='+56900000000',
            password='admin123'
        )

        refresh = RefreshToken.for_user(admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        draw_url = reverse('admin-winners-draw')
        response = self.client.post(draw_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar ganador
        winner = Winner.objects.first()
        self.assertIsNotNone(winner)
        self.assertEqual(winner.participant, participant)

    def test_admin_dashboard_flow(self):
        """Test: flujo completo de administrador"""

        # Crear admin
        admin = Participant.objects.create_superuser(
            email='admin@ctsturismo.cl',
            full_name='Admin CTS',
            phone='+56900000000',
            password='admin123'
        )

        # 1. Login de admin
        login_url = reverse('admin-login')
        response = self.client.post(
            login_url,
            {'email': 'admin@ctsturismo.cl', 'password': 'admin123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['tokens']['access']

        # Configurar autenticación
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 2. Ver estadísticas
        stats_url = reverse('admin-participants-stats')
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Listar participantes
        participants_url = reverse('admin-participants-list')
        response = self.client.get(participants_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. Crear participante verificado para sorteo
        participant = Participant.objects.create_user(
            email='test@example.com',
            full_name='Test Participant',
            phone='+56912345678'
        )
        participant.verify_email()

        # 5. Realizar sorteo
        draw_url = reverse('admin-winners-draw')
        response = self.client.post(draw_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 6. Ver ganadores
        winners_url = reverse('admin-winners-list')
        response = self.client.get(winners_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
