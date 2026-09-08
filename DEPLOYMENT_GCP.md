# Guía Maestra de Despliegue a Producción en Google Cloud Platform (GCP)
## Proyecto: Chivapp (chiv.app)

Esta guía documenta paso a paso cómo desplegar la plataforma **Chivapp** (Frontend Next.js 16 + Backend FastAPI + Base de datos PostgreSQL) en **Google Cloud Platform (GCP)** con el dominio oficial **`chiv.app`** y la pasarela de pagos **Mercado Pago** en modo Producción.

---

## 1. Arquitectura de Producción

* **Frontend:** Google Cloud Run (Contenedor Docker Next.js 16 Standalone, auto-escalable de 0 a N instancias).
* **Backend:** Google Cloud Run (Contenedor Docker FastAPI + Uvicorn).
* **Base de Datos:** Google Cloud SQL para PostgreSQL (versión 15 o 16).
* **Archivos y Contratos (`/uploads`):** Google Cloud Storage (Bucket montado como volumen nativo en Cloud Run gen2).
* **Pasarela de Pagos:** Mercado Pago API Producción con Webhooks HMAC-SHA256 verificados.
* **Dominio y SSL:** `https://chiv.app` (Frontend) y `https://api.chiv.app` (Backend) con certificados SSL gestionados automáticamente por Google.

---

## 2. Preparación Previa en Google Cloud

### Opción A: Usar Google Cloud Shell (Recomendado - Sin instalar nada localmente)
1. Entra a la consola de Google Cloud: [https://console.cloud.google.com](https://console.cloud.google.com).
2. En la barra superior, haz clic en el ícono de terminal **"Activar Cloud Shell"** (`>_`).
3. Clona tu repositorio o sube el código fuente a tu entorno de Cloud Shell.

### Opción B: Usar `gcloud` CLI desde tu computadora
Si prefieres ejecutar desde tu terminal local:
1. Instala el SDK de Google Cloud: `https://cloud.google.com/sdk/docs/install`
2. Inicia sesión:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

---

## 3. Paso 1: Configurar Proyecto y Habilitar APIs

Ejecuta en tu terminal o Cloud Shell:

```bash
# Reemplaza 'chivapp-prod' por el ID de tu proyecto de GCP
export PROJECT_ID="chivapp-prod"
export REGION="us-central1"

gcloud config set project $PROJECT_ID

# Habilitar servicios de GCP requeridos
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com
```

---

## 4. Paso 2: Crear la Base de Datos Cloud SQL (PostgreSQL)

1. **Crear la instancia de PostgreSQL:**
   ```bash
   gcloud sql instances create chivapp-db \
       --database-version=POSTGRES_16 \
       --tier=db-f1-micro \
       --region=$REGION \
       --root-password="TU_PASSWORD_ROOT_SEGURO"
   ```
   *(Nota: Puedes empezar con `db-f1-micro` para costos mínimos y aumentarlo a `db-custom-1-3840` según el tráfico).*

2. **Crear la base de datos de producción:**
   ```bash
   gcloud sql databases create chivapp_prod --instance=chivapp-db
   ```

3. **Crear el usuario de la aplicación:**
   ```bash
   gcloud sql users create chivapp_user \
       --instance=chivapp-db \
       --password="PASSWORD_SUPER_SEGURO_CHIVAPP"
   ```

4. **Obtener el nombre de conexión de la instancia:**
   ```bash
   gcloud sql instances describe chivapp-db --format="value(connectionName)"
   # Ejemplo de salida: chivapp-prod:us-central1:chivapp-db
   ```

Tu cadena de conexión para el backend será:
`postgresql://chivapp_user:PASSWORD_SUPER_SEGURO_CHIVAPP@/chivapp_prod?host=/cloudsql/chivapp-prod:us-central1:chivapp-db`

---

## 5. Paso 3: Crear el Bucket de Cloud Storage para Archivos

Para que las imágenes de perfiles, comprobantes y contratos PDF no se pierdan cuando Cloud Run escale:

```bash
gcloud storage buckets create gs://chivapp-uploads-prod --location=$REGION
```

---

## 6. Paso 4: Desplegar el Backend en Cloud Run

1. **Crear el repositorio de Docker en Artifact Registry:**
   ```bash
   gcloud artifacts repositories create chivapp-repo \
       --repository-format=docker \
       --location=$REGION \
       --description="Repositorio Chivapp"
   ```

2. **Compilar la imagen del Backend:**
   ```bash
   gcloud builds submit Backend \
       --tag $REGION-docker.pkg.dev/$PROJECT_ID/chivapp-repo/backend:latest
   ```

3. **Desplegar el servicio en Cloud Run:**
   ```bash
   gcloud run deploy chivapp-backend \
       --image $REGION-docker.pkg.dev/$PROJECT_ID/chivapp-repo/backend:latest \
       --platform managed \
       --region $REGION \
       --allow-unauthenticated \
       --port 8080 \
       --execution-environment gen2 \
       --add-cloudsql-instances $PROJECT_ID:$REGION:chivapp-db \
       --add-volume name=uploads-vol,type=cloud-storage,bucket=chivapp-uploads-prod \
       --add-volume-mount volume=uploads-vol,mount-path=/app/uploads \
       --set-env-vars "\
SQLALCHEMY_DATABASE_URI=postgresql://chivapp_user:PASSWORD_SUPER_SEGURO_CHIVAPP@/chivapp_prod?host=/cloudsql/$PROJECT_ID:$REGION:chivapp-db,\
JWT_SECRET_KEY=$(openssl rand -hex 32),\
BACKEND_CORS_ORIGINS=['https://chiv.app','https://www.chiv.app','https://api.chiv.app'],\
FRONTEND_URL=https://chiv.app,\
OAUTH_REDIRECT_BASE_URL=https://chiv.app/api/v1,\
BREVO_API_KEY=TU_API_KEY_DE_BREVO,\
EMAIL_FROM=Chivapp <soporte@chiv.app>,\
EMAIL_ENABLED=True,\
RATE_LIMITING_ENABLED=True,\
ENABLE_HSTS=True,\
MERCADO_PAGO_PUBLIC_KEY=APP_USR-TU_PUBLIC_KEY,\
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-TU_ACCESS_TOKEN,\
MERCADO_PAGO_WEBHOOK_SECRET=TU_WEBHOOK_SECRET,\
MERCADO_PAGO_SANDBOX=False,\
MERCADO_PAGO_WEBHOOK_BASE_URL=https://api.chiv.app"
   ```

4. **Copiar la URL del Backend generada** (ejemplo: `https://chivapp-backend-xyz.a.run.app`).

---

## 7. Paso 5: Desplegar el Frontend en Cloud Run

1. **Compilar la imagen del Frontend con las variables de producción:**
   ```bash
   gcloud builds submit Frontend \
       --tag $REGION-docker.pkg.dev/$PROJECT_ID/chivapp-repo/frontend:latest \
       --build-arg NEXT_PUBLIC_API_URL=/api/v1 \
       --build-arg NEXT_PUBLIC_SITE_URL=https://chiv.app \
       --build-arg NEXT_PUBLIC_MERCADO_PAGO_PUBLIC_KEY=APP_USR-TU_PUBLIC_KEY
   ```

2. **Desplegar el servicio en Cloud Run:**
   ```bash
   # Reemplaza BACKEND_URL con la URL obtenida en el paso anterior o https://api.chiv.app
   gcloud run deploy chivapp-frontend \
       --image $REGION-docker.pkg.dev/$PROJECT_ID/chivapp-repo/frontend:latest \
       --platform managed \
       --region $REGION \
       --allow-unauthenticated \
       --port 8080 \
       --set-env-vars "\
PORT=8080,\
API_PROXY_TARGET=https://api.chiv.app,\
NEXT_PUBLIC_SITE_URL=https://chiv.app,\
NEXT_PUBLIC_API_URL=/api/v1,\
NEXT_PUBLIC_MERCADO_PAGO_PUBLIC_KEY=APP_USR-TU_PUBLIC_KEY"
   ```

---

## 8. Paso 6: Configurar tu Dominio `chiv.app` y SSL Gratuito

Google Cloud Run gestiona los certificados SSL de forma 100% automática y gratuita.

1. **Mapear el Frontend (`chiv.app` y `www.chiv.app`):**
   ```bash
   # Mapear dominio raíz
   gcloud beta run domain-mappings create \
       --service chivapp-frontend \
       --domain chiv.app \
       --region $REGION

   # Mapear subdominio www
   gcloud beta run domain-mappings create \
       --service chivapp-frontend \
       --domain www.chiv.app \
       --region $REGION
   ```

2. **Mapear la API (`api.chiv.app`):**
   ```bash
   gcloud beta run domain-mappings create \
       --service chivapp-backend \
       --domain api.chiv.app \
       --region $REGION
   ```

3. **Configurar los registros DNS en tu proveedor de dominio (donde compraste `chiv.app`):**
   * El comando anterior te mostrará los registros exactos (registros **A**, **AAAA** o **CNAME**).
   * Agrégalos en el panel DNS de tu registrador de dominio.
   * En 15 a 30 minutos, Google verificará el dominio y emitirá el certificado SSL con candado verde `https://`.

---

## 9. Paso 7: Configuración de Mercado Pago en Producción

1. **Obtener tus llaves de producción:**
   * Entra a [Mercado Pago Developers](https://www.mercadopago.com/developers/panel/app).
   * Ve a **PRODUCCIÓN** ➡️ **Credenciales de producción**.
   * Copia tu **Public Key** (`APP_USR-...`) y tu **Access Token** (`APP_USR-...`).
2. **Configurar el Webhook:**
   * En el menú lateral, ve a **Webhooks** (o *Notificaciones IPN*).
   * En la URL de producción ingresa:
     ```text
     https://api.chiv.app/api/v1/payments/mercadopago/webhook
     ```
   * En eventos a escuchar selecciona:
     * **Pagos (`payment`)**
     * **Órdenes (`merchant_order`)**
   * Guarda y copia el **Secreto de firma del Webhook** (`MERCADO_PAGO_WEBHOOK_SECRET`).

---

## 10. Prueba de Fuego en Vivo

Una vez desplegado:
1. Entra a **`https://chiv.app`**.
2. Inicia sesión o regístrate como contratista.
3. Elige un músico y haz una reserva de prueba con monto de **S/ 1.00**.
4. Paga con tu tarjeta bancaria real o Yape real en la plataforma.
5. Verás el flujo completarse en segundos:
   * Pago aprobado.
   * Reserva confirmada.
   * Contrato PDF generado y guardado en Cloud Storage.
   * Correos de confirmación recibidos.
6. Entra a tu cuenta de Mercado Pago y haz clic en **Reembolsar** para devolverte el sol de inmediato.
