# Configuración de Celery + Redis para Producción

Este documento explica cómo activar el modo asíncrono completo con Celery y Redis.

## ¿Por qué Celery?

**Celery** es un sistema de cola de tareas distribuido que permite ejecutar operaciones pesadas en segundo plano sin bloquear las respuestas HTTP.

### Beneficios en este proyecto:

1. **Performance**: El usuario recibe respuesta inmediata al registrarse o sortear
2. **Escalabilidad**: Puede manejar miles de emails simultáneos
3. **Confiabilidad**: Si falla un email, se puede reintentar automáticamente
4. **Producción**: Es el estándar de la industria para aplicaciones Django

## Estado Actual del Proyecto

El proyecto implementa un **sistema híbrido inteligente**:

```python
# En views.py
try:
    # Intenta usar Celery (modo asíncrono)
    send_verification_email.delay(str(participant.id))
except Exception:
    # Si falla, usa modo síncrono
    send_verification_email_sync(participant.id)
```

**Ventajas de este enfoque:**
- ✅ Cumple con los requisitos técnicos (Celery implementado)
- ✅ Funciona sin configuración (para demos y desarrollo)
- ✅ Listo para producción (solo necesitas iniciar los servicios)
- ✅ Sin errores si Redis no está disponible

## Instalación y Configuración

### Opción 1: Desarrollo Local con Redis

#### Windows

1. **Instalar Redis:**
   ```powershell
   # Con Chocolatey
   choco install redis-64

   # O descargar desde:
   # https://github.com/microsoftarchive/redis/releases
   ```

2. **Iniciar Redis:**
   ```bash
   redis-server
   ```

3. **Iniciar Celery Worker (en otra terminal):**
   ```bash
   cd backend
   venv\Scripts\activate
   celery -A config worker --loglevel=info --pool=solo
   ```

4. **Iniciar Celery Beat (opcional, para tareas programadas):**
   ```bash
   celery -A config beat --loglevel=info
   ```

#### Linux/Mac

1. **Instalar Redis:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server

   # macOS
   brew install redis
   ```

2. **Iniciar Redis:**
   ```bash
   redis-server
   ```

3. **Iniciar Celery Worker:**
   ```bash
   cd backend
   source venv/bin/activate
   celery -A config worker --loglevel=info
   ```

4. **Iniciar Celery Beat (opcional):**
   ```bash
   celery -A config beat --loglevel=info
   ```

### Opción 2: Producción con Docker

Crear un `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build: ./backend
    command: celery -A config worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis

  celery_beat:
    build: ./backend
    command: celery -A config beat --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
```

Luego ejecutar:
```bash
docker-compose up -d
```

## Verificar que Celery está Funcionando

### 1. Ver logs del worker:
Deberías ver algo como:
```
[tasks]
  . participants.tasks.send_verification_email
  . participants.tasks.send_winner_notification

[2025-10-18 05:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379//
[2025-10-18 05:00:00,000: INFO/MainProcess] celery@hostname ready.
```

### 2. Probar una tarea:
```bash
cd backend
python manage.py shell
```

```python
from participants.tasks import send_verification_email
from participants.models import Participant

# Crear un participante de prueba
participant = Participant.objects.first()

# Enviar tarea a Celery
result = send_verification_email.delay(str(participant.id))

# Ver resultado
print(result.status)  # 'SUCCESS' cuando termine
print(result.result)  # El resultado de la tarea
```

### 3. Monitorear con Flower (opcional):
```bash
pip install flower
celery -A config flower

# Abrir http://localhost:5555
```

## Configuración de Variables de Entorno

En tu archivo `.env`:

```bash
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (para envío real)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

## Monitoreo y Logging

### Ver tareas en ejecución:
```bash
celery -A config inspect active
```

### Ver tareas programadas:
```bash
celery -A config inspect scheduled
```

### Ver estadísticas:
```bash
celery -A config inspect stats
```

## Deployment en Producción

### Railway / Render / Heroku

1. **Agregar Redis como addon/servicio**
2. **Configurar variables de entorno** con la URL de Redis
3. **Agregar worker process** en Procfile:

```
web: gunicorn config.wsgi
worker: celery -A config worker --loglevel=info
beat: celery -A config beat --loglevel=info
```

### AWS / DigitalOcean / VPS

1. **Instalar Redis** en el servidor
2. **Usar systemd** para manejar los procesos:

Crear `/etc/systemd/system/celery.service`:
```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/celery -A config worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Iniciar:
```bash
sudo systemctl start celery
sudo systemctl enable celery
```

## Troubleshooting

### Error: "Connection refused" o "ECONNREFUSED"
- **Causa**: Redis no está corriendo
- **Solución**: Iniciar Redis con `redis-server`

### Error: "Received unregistered task"
- **Causa**: Celery no encuentra las tareas
- **Solución**: Reiniciar el worker de Celery

### Tareas no se ejecutan
- **Verificar**:
  1. Redis está corriendo: `redis-cli ping` (debe responder "PONG")
  2. Worker está corriendo: Ver logs del worker
  3. Tareas están registradas: `celery -A config inspect registered`

### Performance lento
- **Solución**: Aumentar el número de workers:
  ```bash
  celery -A config worker --concurrency=4
  ```

## Resumen

| Modo | ¿Cuándo usar? | Ventajas |
|------|---------------|----------|
| **Sin Celery** (actual) | Desarrollo, demos, pruebas locales | No requiere configuración, funciona inmediatamente |
| **Con Celery** | Producción, alto tráfico | Escalable, profesional, mejor performance |

El proyecto está **listo para ambos modos**. La configuración actual permite trabajar sin Celery para desarrollo, y activarlo fácilmente para producción siguiendo esta guía.
