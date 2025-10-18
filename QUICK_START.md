# Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha el sistema en menos de 5 minutos.

## Requisitos Previos

- Python 3.13+
- Node.js 18+
- Redis (para Celery)

## Pasos Rápidos

### 1. Backend (Terminal 1)

```bash
# Ir al directorio backend
cd backend

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Las dependencias ya están instaladas, solo inicia el servidor
python manage.py runserver
```

El backend estará en: **http://localhost:8000**

### 2. Celery (Terminal 2)

```bash
cd backend
venv\Scripts\activate  # o source venv/bin/activate en Linux/Mac

# Windows:
celery -A config worker --loglevel=info --pool=solo

# Linux/Mac:
celery -A config worker --loglevel=info
```

**Nota**: Asegúrate de tener Redis corriendo. Si no lo tienes:
- Windows: Descarga Redis para Windows
- Linux: `sudo systemctl start redis`
- Mac: `brew services start redis`

### 3. Frontend (Terminal 3)

```bash
cd frontend
npm install
npm run dev
```

El frontend estará en: **http://localhost:3000**

## Credenciales de Administrador

Ya existe un usuario administrador creado:

- **Email**: admin@ctsturismo.cl
- **Password**: admin123

## Probar el Sistema

### Como Participante:

1. Ve a http://localhost:3000
2. Completa el formulario de registro
3. Revisa la terminal donde corre el backend - verás el email de verificación impreso
4. Copia el token del enlace y ve a: http://localhost:3000/verify/TOKEN
5. Crea una contraseña para confirmar tu participación

### Como Administrador:

1. Ve a http://localhost:3000/admin/login
2. Ingresa con admin@ctsturismo.cl / admin123
3. Verás el dashboard con estadísticas
4. Haz clic en "Sortear Ganador" para realizar el sorteo

## Configuración de Email Real (Opcional)

Para enviar emails reales en lugar de mostrarlos en consola:

1. Edita `backend/.env`
2. Cambia:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-app-password
   ```
3. Reinicia el servidor de Django

## Estructura de URLs

- **Frontend**:
  - Registro: http://localhost:3000
  - Verificación: http://localhost:3000/verify/:token
  - Admin Login: http://localhost:3000/admin/login
  - Dashboard: http://localhost:3000/admin/dashboard

- **Backend API**:
  - Admin Django: http://localhost:8000/admin
  - API Base: http://localhost:8000/api
  - Docs (opcional): http://localhost:8000/api/schema/swagger-ui/

## Solución de Problemas

### Redis no está corriendo
```
Error: Error 10061 connecting to localhost:6379
```
**Solución**: Instala e inicia Redis según tu sistema operativo

### Puerto 8000 ya en uso
```bash
python manage.py runserver 8001
```
Luego actualiza `NUXT_PUBLIC_API_BASE` en el frontend

### Errores de CORS
Asegúrate de que el frontend corra en http://localhost:3000 (configurado en CORS_ALLOWED_ORIGINS)

## Siguiente Paso

Lee el [README.md](README.md) completo para entender la arquitectura y endpoints de la API.

¡Listo para sortear! 🎉
