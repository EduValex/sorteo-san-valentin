# Sorteo San Valentín - CTS Turismo

Sistema Full Stack para gestionar un sorteo de San Valentín donde los participantes pueden registrarse, verificar su email, y tener la oportunidad de ganar una estadía romántica de 2 noches para una pareja.

## Tabla de Contenidos

- [Características](#características)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación y Configuración](#instalación-y-configuración)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Uso](#uso)
- [Endpoints de la API](#endpoints-de-la-api)
- [Flujo del Usuario](#flujo-del-usuario)
- [Tests](#tests)
- [Celery + Redis (Opcional)](#celery--redis-opcional)
- [Decisiones Técnicas](#decisiones-técnicas)

---

## Características

- **Registro de Participantes**: Los usuarios pueden registrarse con nombre, email y teléfono
- **Verificación de Email**: Sistema de verificación mediante token único enviado por correo
- **Confirmación de Participación**: Los usuarios deben crear una contraseña para confirmar su participación
- **Panel Administrador**: Interface para gestionar participantes y realizar el sorteo
- **Sorteo Aleatorio**: Selección aleatoria de ganador entre participantes verificados
- **Notificación Automática**: Envío de email al ganador de forma asíncrona
- **Autenticación JWT**: Sistema seguro de autenticación para administradores

## Tecnologías Utilizadas

### Backend
- **Python 3.13**
- **Django 5.0.1**: Framework web
- **Django REST Framework 3.14.0**: API REST
- **djangorestframework-simplejwt 5.3.1**: Autenticación JWT
- **Celery 5.3.6**: Procesamiento asíncrono de tareas
- **Redis 5.0.1**: Message broker para Celery
- **SQLite**: Base de datos (fácil para desarrollo/demostración)
- **Envío de Emails**: Asíncrono mediante Celery (modo síncrono disponible para desarrollo sin Redis)

### Frontend
- **Nuxt.js 3.13.0**: Framework Vue.js
- **TypeScript**: Tipado estático
- **Tailwind CSS**: Estilos y diseño responsive
- **Axios 1.7.2**: Cliente HTTP
- **SweetAlert2**: Alertas y modales elegantes
- **canvas-confetti**: Efectos visuales

## Uso
El sistema está desplegado para su prueba en tiempo real. 

NOTA: Algunos navegadores pueden bloquear la aplicación, se recomienda utilizar Google Chrome

### Para Participantes:

1. **Registro**: Ir a `https://sorteo-san-valentin.vercel.app/` y completar el formulario de registro
2. **Verificar Email**: Revisar correo electrónico y hacer clic en el link de verificación (Los correos de verificación actualmente pueden llegar a SPAM por la configuración temporal de dominio en SendGrid.)
3. **Crear Contraseña**: En la página de verificación, crear una contraseña para confirmar participación

### Para Administradores:

1. **Login**: Ir a `https://sorteo-san-valentin.vercel.app/admin/dashboard`
   - Email: `admin@ctsturismo.cl`
   - Password: `admin123`

2. **Dashboard**: Ver estadísticas, lista de participantes, historial de ganadores, y realizar el sorteo

3. **Realizar Sorteo**: Click en "Sortear Ganador" para seleccionar un ganador aleatorio

4. Al participante ganador le llegará un correo con la notificación.

## Estructura del Proyecto

```
sorteo-san-valentin/
├── backend/
│   ├── config/                 # Configuración de Django
│   │   ├── settings.py        # Configuración principal
│   │   ├── urls.py            # URLs principales
│   │   ├── celery.py          # Configuración de Celery
│   │   └── __init__.py        # Inicialización de Celery
│   ├── participants/          # App principal
│   │   ├── models.py          # Modelos (Participant, Winner)
│   │   ├── views.py           # Vistas y endpoints
│   │   ├── serializers.py     # Serializers de DRF
│   │   ├── emails.py          # Funciones de envío de emails
│   │   ├── urls.py            # URLs de la app
│   │   ├── admin.py           # Configuración del admin
│   │   └── management/
│   │       └── commands/
│   │           ├── create_admin.py         # Comando para crear admin
│   │           └── create_fake_participants.py  # Crear participantes de prueba
│   ├── requirements.txt       # Dependencias Python
│   ├── .env.example          # Variables de entorno ejemplo
│   └── manage.py             # Script de Django
│
└── frontend/
    ├── pages/                # Páginas de Nuxt
    │   ├── index.vue        # Registro de participantes
    │   ├── verify/
    │   │   └── [token].vue  # Verificación de email
    │   └── admin/
    │       ├── login.vue    # Login de administrador
    │       └── dashboard.vue # Panel de administración
    ├── composables/
    │   └── useApi.ts        # Composable para API calls
    ├── nuxt.config.ts       # Configuración de Nuxt
    └── package.json         # Dependencias Node
```

## Instalación y Configuración

### Backend

1. **Navegar al directorio backend:**
   ```bash
   cd backend
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   # Copiar .env.example a .env
   cp .env.example .env

   # Editar .env con tus configuraciones
   # Para desarrollo local, los valores por defecto funcionan
   ```

5. **Ejecutar migraciones:**
   ```bash
   python manage.py migrate
   ```

6. **Crear usuario administrador:**
   ```bash
   python manage.py create_admin
   # Esto crea un admin con:
   # Email: admin@ctsturismo.cl
   # Password: admin123
   ```

7. **(Opcional) Crear participantes de prueba:**
   ```bash
   python manage.py create_fake_participants
   # Esto crea 6 participantes verificados para probar el sorteo
   ```

8. **(Opcional) Iniciar Redis y Celery para emails asíncronos:**

   El sistema usa Celery + Redis para envío asíncrono de emails. Para desarrollo, puedes saltar este paso y los emails se mostrarán en la consola del servidor Django.

   Para usar Celery en producción:

   **Instalar y ejecutar Redis:**
   ```bash
   # Windows (usando Chocolatey)
   choco install redis-64
   redis-server

   # Linux/Mac
   sudo apt-get install redis-server  # Ubuntu/Debian
   brew install redis                  # Mac
   redis-server
   ```

   **Iniciar Celery Worker (en otra terminal):**
   ```bash
   cd backend
   celery -A config worker --loglevel=info

   # En Windows, agregar --pool=solo
   celery -A config worker --loglevel=info --pool=solo
   ```

   **Iniciar Celery Beat (opcional, para tareas periódicas):**
   ```bash
   celery -A config beat --loglevel=info
   ```

9. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```
   El backend estará disponible en `http://localhost:8000`

**NOTA IMPORTANTE SOBRE EMAILS Y CELERY:**

El sistema está configurado con **fallback automático inteligente**:

- **Con Celery corriendo**: Los emails se envían de forma asíncrona (modo profesional/producción)
- **Sin Celery**: Automáticamente usa modo síncrono (desarrollo/demo)
- **Modo consola**: Por defecto los emails aparecen en la consola del backend
- **Modo SMTP real**: Configura las variables SMTP en `.env`

**¿Por qué este enfoque?**
- ✅ Cumple con los requisitos (Celery implementado)
- ✅ Funciona sin configuración adicional (desarrollo rápido)
- ✅ Listo para producción (solo iniciar Celery + Redis)
- ✅ Sin errores si Celery no está disponible

Para cambiar a modo SMTP real (producción), edita `EMAIL_BACKEND` en `settings.py`.

### Frontend

1. **Navegar al directorio frontend:**
   ```bash
   cd frontend
   ```

2. **Instalar dependencias:**
   ```bash
   npm install
   ```

3. **Iniciar el servidor de desarrollo:**
   ```bash
   npm run dev
   ```
   El frontend estará disponible en `http://localhost:3000` o `http://localhost:3001` (si el puerto 3000 está ocupado)

**IMPORTANTE:** Si el frontend inicia en un puerto diferente a 3000, actualiza la variable `FRONTEND_URL` en el archivo `.env` del backend para que los links de verificación de email apunten al puerto correcto.


## Endpoints de la API

### Públicos (sin autenticación)

#### POST `/api/participants/register/`
Registra un nuevo participante.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "full_name": "Juan Pérez",
  "phone": "+56912345678"
}
```

**Response:**
```json
{
  "message": "¡Gracias por registrarte! Revisa tu correo para verificar tu cuenta.",
  "participant": {
    "email": "usuario@ejemplo.com",
    "full_name": "Juan Pérez"
  }
}
```

#### POST `/api/participants/verify-email/`
Verifica el email con el token recibido.

**Request:**
```json
{
  "token": "uuid-token"
}
```

**Response:**
```json
{
  "message": "Email verificado exitosamente. Ahora puedes crear tu contraseña.",
  "participant": {
    "id": "uuid",
    "email": "usuario@ejemplo.com",
    "full_name": "Juan Pérez",
    "is_verified": true
  }
}
```

#### POST `/api/participants/set-password/`
Establece la contraseña del participante.

**Request:**
```json
{
  "verification_token": "uuid-token",
  "password": "contraseña123",
  "password_confirm": "contraseña123"
}
```

**Response:**
```json
{
  "message": "Tu cuenta ha sido activada. Ya estás participando en el sorteo.",
  "participant": {
    "id": "uuid",
    "email": "usuario@ejemplo.com",
    "full_name": "Juan Pérez"
  }
}
```

#### POST `/api/auth/login/`
Login de administrador.

**Request:**
```json
{
  "email": "admin@ctsturismo.cl",
  "password": "admin123"
}
```

**Response:**
```json
{
  "message": "Inicio de sesión exitoso.",
  "tokens": {
    "refresh": "jwt-refresh-token",
    "access": "jwt-access-token"
  },
  "user": {
    "id": "uuid",
    "email": "admin@ctsturismo.cl",
    "full_name": "Administrador CTS",
    "is_admin": true
  }
}
```

### Protegidos (requieren autenticación JWT)

**Header requerido:**
```
Authorization: Bearer <access-token>
```

#### GET `/api/admin/participants/`
Lista todos los participantes.

**Query params:**
- `search`: Buscar por email, nombre o teléfono
- `is_verified`: Filtrar por estado de verificación (true/false)
- `page`: Número de página

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "email": "usuario@ejemplo.com",
      "full_name": "Juan Pérez",
      "phone": "+56912345678",
      "is_verified": true,
      "created_at": "2025-01-01T12:00:00Z",
      "status": "Verificado"
    }
  ]
}
```

#### GET `/api/admin/participants/stats/`
Obtiene estadísticas de participantes.

**Response:**
```json
{
  "total_participants": 100,
  "verified": 80,
  "pending": 20,
  "eligible_for_draw": 80
}
```

#### POST `/api/admin/winners/draw/`
Realiza el sorteo y selecciona un ganador.

**Response:**
```json
{
  "message": "¡Ganador seleccionado exitosamente!",
  "winner": {
    "id": "uuid",
    "participant_name": "Juan Pérez",
    "participant_email": "usuario@ejemplo.com",
    "participant_phone": "+56912345678",
    "drawn_at": "2025-02-14T10:00:00Z",
    "notified": false,
    "prize_description": "Estadía de 2 noches para pareja en hotel todo incluido"
  }
}
```

#### GET `/api/admin/winners/`
Lista todos los ganadores.

**Response:**
```json
[
  {
    "id": "uuid",
    "participant_name": "Juan Pérez",
    "participant_email": "usuario@ejemplo.com",
    "participant_phone": "+56912345678",
    "drawn_at": "2025-02-14T10:00:00Z",
    "drawn_by_name": "Administrador CTS",
    "notified": true,
    "notified_at": "2025-02-14T10:01:00Z",
    "prize_description": "Estadía de 2 noches para pareja"
  }
]
```

## Flujo del Usuario

### Participante

1. **Registro**: El usuario completa el formulario con email, nombre y teléfono
2. **Email enviado**: El sistema envía un email de verificación de forma asíncrona (Celery)
3. **Verificación**: El usuario hace clic en el link del email
4. **Contraseña**: El usuario crea una contraseña para confirmar participación
5. **Confirmación**: El usuario queda registrado como participante elegible

### Administrador

1. **Login**: Accede con credenciales de administrador
2. **Dashboard**: Ve estadísticas y lista de participantes
3. **Sorteo**: Realiza el sorteo cuando lo desee
4. **Notificación**: El ganador recibe un email automático
5. **Seguimiento**: Puede ver el historial de ganadores

## Tests

El proyecto incluye una suite completa de tests unitarios y de integración para el backend.

### Ejecutar Tests

Para ejecutar todos los tests del backend:

```bash
cd backend
python manage.py test
```

Para ejecutar tests con más detalle:

```bash
python manage.py test --verbosity=2
```

Para ejecutar un módulo específico de tests:

```bash
python manage.py test participants.tests.ParticipantModelTests
```

### Cobertura de Tests

Los tests cubren:

1. **Tests de Modelos** (`ParticipantModelTests`, `WinnerModelTests`):
   - Creación de participantes y administradores
   - Verificación de email
   - Validaciones de campos únicos
   - Propiedades computadas (`can_participate`)
   - Métodos del modelo

2. **Tests de API - Registro** (`ParticipantRegistrationAPITests`):
   - Registro exitoso de participantes
   - Validación de emails duplicados
   - Validación de formato de email y teléfono
   - Campos requeridos
   - Envío de email de verificación

3. **Tests de API - Verificación** (`EmailVerificationAPITests`):
   - Verificación exitosa con token válido
   - Rechazo de tokens inválidos
   - Prevención de doble verificación

4. **Tests de API - Contraseña** (`SetPasswordAPITests`):
   - Establecer contraseña correctamente
   - Validación de contraseñas coincidentes
   - Requerimiento de email verificado

5. **Tests de API - Login Admin** (`AdminLoginAPITests`):
   - Login exitoso de administrador
   - Generación de tokens JWT
   - Rechazo de credenciales inválidas
   - Prevención de login de usuarios no-admin

6. **Tests de API - Panel Admin** (`ParticipantListAPITests`):
   - Listado de participantes (requiere auth)
   - Filtrado por estado de verificación
   - Búsqueda por nombre/email
   - Estadísticas de participantes

7. **Tests de API - Sorteo** (`WinnerDrawAPITests`):
   - Realización exitosa del sorteo
   - Selección aleatoria de ganador
   - Notificación por email
   - Validación de participantes elegibles
   - Listado de ganadores

8. **Tests de Integración** (`IntegrationTests`):
   - Flujo completo de participante (registro → verificación → contraseña → sorteo)
   - Flujo completo de administrador (login → dashboard → sorteo → ganadores)

### Resultados Esperados

Al ejecutar los tests, deberías ver algo como:

```
Found 40 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
........................................
----------------------------------------------------------------------
Ran 40 tests in 2.345s

OK
```

Todos los tests deberían pasar sin errores.

## Celery + Redis (Opcional)

El sistema implementa **Celery con graceful degradation**:

- ✅ **Funciona SIN Celery**: El sistema detecta automáticamente si Celery no está disponible y usa modo síncrono
- ✅ **Funciona CON Celery**: Si inicias Redis + Celery worker, automáticamente usa modo asíncrono (profesional)
- ✅ **Cumple requisitos**: Celery está implementado según los requerimientos del PDF
- ✅ **Listo para producción**: Solo necesitas iniciar los servicios

### ¿Quieres activar Celery para demostrar el modo asíncrono?

Consulta la guía completa en **[CELERY_SETUP.md](CELERY_SETUP.md)** que incluye:

- Explicación técnica de por qué usar Celery
- Instalación paso a paso de Redis
- Configuración de Celery worker
- Verificación de funcionamiento
- Deployment en producción
- Troubleshooting

**Inicio rápido (Windows):**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
cd backend
venv\Scripts\activate
celery -A config worker --loglevel=info --pool=solo

# Terminal 3: Django
python manage.py runserver
```

Si no inicias Celery, el sistema funciona perfectamente en modo síncrono (emails en consola).

## Decisiones Técnicas

### Backend

1. **SQLite vs PostgreSQL**: Se eligió SQLite para facilitar la instalación y demostración. En producción se recomienda PostgreSQL (ya configurado en settings.py).

2. **Custom User Model**: Se implementó un modelo de usuario personalizado (`Participant`) que extiende `AbstractBaseUser` para tener control total sobre los campos y comportamiento.

3. **UUID Primary Keys**: Se usan UUIDs en lugar de IDs incrementales por seguridad, evitando enumeración de usuarios.

4. **JWT Authentication**: Se usa djangorestframework-simplejwt para autenticación stateless, ideal para APIs REST.

5. **Celery para Emails (Configuración Híbrida Inteligente)**:
   - El sistema implementa **graceful degradation** para envío de emails
   - **Modo preferido**: Asíncrono con Celery + Redis (producción)
   - **Modo fallback**: Síncrono directo (desarrollo/demo)
   - El código intenta usar Celery primero, si falla, usa el método síncrono automáticamente
   - **Ventajas**:
     * Cumple con requisitos técnicos (Celery implementado)
     * Funciona sin dependencias externas (Redis no requerido para demo)
     * Listo para producción (solo iniciar worker de Celery)
     * Sin errores ni timeouts si Celery no está disponible
   - Las tareas asíncronas están en `tasks.py`, las síncronas en `emails.py`

6. **Validaciones**: Se implementan validaciones a nivel de serializer para email único, formato de teléfono, y contraseñas coincidentes.

7. **Índices en Base de Datos**: Se agregaron índices en campos frecuentemente consultados (email, is_verified, created_at) para mejorar performance.

### Frontend

1. **Nuxt.js 3**: Se eligió Nuxt por su capacidad de SSR, mejor SEO, y estructura organizada con Vue 3.

2. **TypeScript**: Proporciona type safety y mejor autocompletado en el desarrollo.

3. **Composables**: Se usa el patrón de composables (`useApi`) para centralizar la lógica de API calls y reutilización de código.

4. **Tailwind CSS**: Framework utility-first para desarrollo rápido de UI responsive.

5. **Client-side Storage**: Los tokens JWT se almacenan en localStorage para persistir la sesión del admin.

6. **Route Guards**: Se verifican los tokens antes de acceder a rutas protegidas (dashboard).

### Arquitectura General

1. **Separación Frontend/Backend**: Arquitectura desacoplada que permite escalar y desplegar independientemente.

2. **RESTful API**: Seguimiento de convenciones REST para una API predecible y fácil de usar.

3. **Error Handling**: Manejo consistente de errores con mensajes claros en español.

4. **Locale**: Sistema configurado en español de Chile (es-cl) y timezone America/Santiago.

### Seguridad

1. **CORS**: Configurado para permitir solo orígenes específicos (localhost:3000 en desarrollo).

2. **Password Validation**: Uso de validadores de Django para contraseñas seguras.

3. **Permisos**: Sistema de permisos que distingue entre usuarios regulares y administradores.

4. **Token Expiration**: Access tokens expiran en 60 minutos, refresh tokens en 1 día.

---

## Créditos

Desarrollado como prueba técnica para CTS Turismo.

**Stack**: Python + Django + DRF + Celery + Nuxt.js + TypeScript + Tailwind CSS

**Autor**: Desarrollado con Claude Code
