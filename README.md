# Backend - Portfolio Contact API

Este es el backend de mi portafolio personal, construido con
**FastAPI**, **SQLAlchemy**, y la API HTTP de **Brevo** para el envío de
correos.\
El sistema procesa envíos del formulario de contacto, valida reCAPTCHA
v3, guarda mensajes en la base de datos y envía notificaciones por
correo de forma confiable incluso en producción.

## 🚀 Características

-   Recepción segura de mensajes del formulario de contacto (nombre,
    email, mensaje)
-   Almacenamiento de mensajes en PostgreSQL mediante SQLAlchemy ORM
-   Envío de correos usando la **Brevo Transactional Email API** (no
    SMTP)
-   Protección con **reCAPTCHA v3**
-   Límite de peticiones (rate limiting) → 3 solicitudes por minuto
-   Configuración de CORS para integración con el frontend
-   Variables de entorno para toda información sensible

## 🛠️ Tecnologías

-   **FastAPI**
-   **SQLAlchemy**
-   **PostgreSQL**
-   **Brevo API (v3)**
-   **httpx**
-   **slowapi** (rate limiting)
-   **python-dotenv**
-   Python **3.11+**

## 📦 Instalación y ejecución

### 1. Clonar el repositorio

``` bash
git clone <tu-repo>
cd backend
```

### 2. Crear un entorno virtual

``` bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### 3. Instalar dependencias

``` bash
pip install -r requirements.txt
```

### 4. Crear archivo `.env`

``` env
DATABASE_URL=postgresql://user:password@host:port/dbname
BREVO_API_KEY=tu_api_key
MAIL_FROM=correo_que_envia@ejemplo.com
MAIL_RECEIVER=correo_que_recibe@ejemplo.com
RECAPTCHA_SECRET_KEY=tu_recaptcha_secret_key
FRONTEND_URLS=https://tudominio.com
IS_DEV=true
```

### 5. Ejecutar servidor de desarrollo

``` bash
uvicorn app.main:app --reload
```

## 📡 Endpoint

### `POST /contact`

Recibe datos del formulario, valida reCAPTCHA, guarda en BD y envía
correo mediante Brevo API.

### Body JSON

``` json
{
  "name": "Hector Aliaga",
  "email": "hector@example.com",
  "message": "Hola, me gustó tu portafolio."
}
```

### Headers

    recaptcha-token: <token_generado_en_el_frontend>

### Respuesta

``` json
{
  "message": "Gracias por contactarme, te responderé de inmediato."
}
```

## 🔐 Notas importantes

-   Brevo API v3 debe usarse con **API Key**, no SMTP Key.

-   Render/Vercel deben tener las variables de entorno configuradas
    correctamente.

-   Si usas localhost durante desarrollo, añade:

        FRONTEND_URLS=http://localhost:5173

-   reCAPTCHA v3 requiere que el dominio coincida exactamente con tu
    dominio real.

## 📄 Licencia

Este proyecto está bajo la licencia MIT.
