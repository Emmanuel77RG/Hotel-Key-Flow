# 🏨 Hotel KeyFlow - Sistema de Gestión Hotelera (PMS)

**Hotel KeyFlow** es un Property Management System (PMS) de nivel empresarial diseñado para operar en un entorno local seguro (*On-Premise*). Su objetivo es gestionar integralmente las operaciones hoteleras: inventario físico y estados de habitaciones, reservaciones con prevención de sobreventa, check-in transaccional, check-out con balance de saldo cero, cuentas folio, cargos automáticos, facturación electrónica simulada, tickets de mantenimiento, punto de venta (POS) y arqueos diarios de corte de caja con reportes ejecutivos.

El proyecto está construido bajo una arquitectura modular cliente-servidor estrictamente local, con un backend de alto rendimiento en **FastAPI**, persistencia transaccional en **PostgreSQL 15** (vía Docker) con migraciones versionadas por **Alembic**, y una interfaz de escritorio nativa en **Python (CustomTkinter)**.

---

## 🛠️ Tecnologías y Herramientas

* **Backend:** Python 3.12, FastAPI, Uvicorn.
* **Base de Datos:** PostgreSQL 15 (aislado en contenedor Docker con healthcheck `pg_isready`).
* **Migraciones de Esquema:** Alembic.
* **ORM:** SQLAlchemy 2.0.
* **Validación de Datos y Esquemas:** Pydantic v2 (con validaciones numéricas estrictas y regex RFC).
* **Seguridad y Criptografía:** Passlib (Bcrypt con salting dinámico) y JWT (JSON Web Tokens) con RBAC.
* **Pruebas y Calidad:** Pytest, TestClient (HTTPX), Logging rotativo de 5 MB.
* **Frontend:** Python, CustomTkinter (interfaz modular con soporte multirol), Requests.

---

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu equipo:
1. [Python 3.12+](https://www.python.org/downloads/)
2. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (para el contenedor de la base de datos).
3. [Git](https://git-scm.com/)

---

## ⚙️ Configuración e Instalación

### 1. Clonar el repositorio
Abre tu terminal y clona el proyecto:
```bash
git clone https://github.com/Emmanuel77RG/Hotel-Key-Flow.git
cd Hotel-Key-Flow
```

### 2. Configurar el Entorno Virtual
Es obligatorio el uso de un entorno virtual para aislar las dependencias del proyecto:

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual (Windows - PowerShell)
.venv\Scripts\Activate.ps1

# Activar el entorno virtual (Mac / Linux)
# source .venv/bin/activate
```

> [!NOTE]
> Si en Windows PowerShell surge un error de restricción de ejecución de scripts, ejecuta:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Scope Process
> ```

### 3. Instalar Dependencias
Con el entorno virtual activado, instala las librerías necesarias:

```bash
# Para ejecución normal:
pip install -r requirements.txt

# Para desarrollo, linteo y suite de pruebas:
pip install -r requirements-dev.txt
```

### 4. Configurar Variables de Entorno (`.env`)
El proyecto no almacena credenciales en el código fuente. Copia la plantilla oficial [`.env.example`](.env.example) para crear tu archivo `.env`:

```bash
# Windows (PowerShell):
Copy-Item .env.example .env

# Mac / Linux:
cp .env.example .env
```

Verifica que tu archivo `.env` contenga la configuración para tu base de datos local:
```env
DATABASE_URL=postgresql://admin:adminpsw@localhost:5432/hotel_keyflow
SECRET_KEY=tu_super_llave_secreta_jwt_de_al_menos_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
*(Nota: El archivo `.env` está estrictamente ignorado por el `.gitignore`).*

---

## 🗄️ Base de Datos, Docker y Migraciones

### 1. Levantar el Contenedor PostgreSQL
Asegúrate de tener Docker Desktop en ejecución y levanta el servicio de base de datos:
```bash
docker-compose up -d
```
El contenedor se iniciará vinculando el puerto seguro `127.0.0.1:5432:5432` con monitoreo de salud mediante `pg_isready`.

### 2. Aplicar Migraciones de Esquema (Alembic)
Aplica la estructura completa de tablas en la base de datos PostgreSQL:
```bash
alembic upgrade head
```

### 3. Siembra Inicial de Roles
Ejecuta el script de aprovisionamiento para registrar los tres roles del sistema hotelero:
```bash
python scripts/seed_roles.py
```
* **Rol 1:** Administrador (Control total del sistema y gestión de personal).
* **Rol 2:** Recepción (Front-desk, reservas, folios, check-in, check-out y POS).
* **Rol 3:** Limpieza (Camarería, cambio de estados físicos y visualización de incidencias).

---

## ▶️ Ejecución del Sistema

Para operar el sistema, ejecuta la API Backend y la Interfaz de Escritorio en dos terminales independientes:

### Terminal 1: Servidor Backend (API FastAPI)
```bash
uvicorn app.main:app --reload
```
* **API base:** `http://127.0.0.1:8000`
* **Documentación interactiva (Swagger UI):** `http://127.0.0.1:8000/docs`
* **Healthcheck de servicio y base de datos:** `http://127.0.0.1:8000/health`

### Terminal 2: Cliente de Escritorio (CustomTkinter GUI)
```bash
python desktop_client/login_gui.py
```
Inicia sesión con las credenciales de tu usuario registrado (el panel cargará automáticamente los módulos autorizados según tu rol).

---

## 🧪 Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas unitarias y de integración que se ejecutan sobre una base de datos SQLite aislada en memoria:

```bash
pytest -v
```

Casos cubiertos en la suite:
* **Seguridad Criptográfica:** Hashing Bcrypt, salting dinámico y verificación de contraseñas.
* **Control de Acceso (RBAC):** Restricciones de endpoints, denegación 401 sin token y bloqueo 403 para roles sin privilegios.
* **Motor de Disponibilidad (Overbooking):** Detección de solapamiento de fechas (409 Conflict) y rechazo de fechas pasadas (400 Bad Request).
* **Operaciones Transaccionales:** Check-in con apertura de cuenta folio y cargo automático, y Check-out con validación de saldo cero y liberación a estado Sucia.

---

## 🔒 Estándares de Colaboración (Git Flow)

Este repositorio sigue políticas estrictas de control de calidad:
1. **Ramas protegidas:** No se realizan commits directos sobre la rama `main`.
2. **Nomenclatura de ramas:**
   * Nuevas funcionalidades: `feature/nombre-funcionalidad`
   * Corrección de errores / auditoría: `fix/nombre-correccion`
3. **Integración Continua:** Toda rama debe superar el pipeline automatizado de GitHub Actions (`.github/workflows/ci.yml`) antes de fusionarse.
4. **Revisión por Pares:** Los cambios se integran únicamente mediante Pull Request (PR) con aprobación de revisor.

---

## ⚠️ Solución de Problemas (Troubleshooting)

### Error de Docker: Virtualización deshabilitada en la BIOS
Si al iniciar Docker Desktop aparece un mensaje indicando que la virtualización por hardware no está habilitada:

#### 1. Activar la virtualización en la BIOS
* Apaga el equipo por completo.
* Enciéndelo y presiona repetidamente la tecla de acceso a la BIOS antes de que cargue Windows:
  * **Lenovo / Dell / Toshiba / Asus / Acer:** `F2` (o `Fn + F2` / `Supr`)
  * **HP:** `F10` o `Esc`
  * **MSI:** `Supr` (Delete)
* En el menú avanzado (`Advanced` o `CPU Configuration`):
  * Si tu procesador es AMD: busca **SVM Mode** y cámbialo a **Enabled**.
  * Si tu procesador es Intel: busca **Intel Virtualization Technology (VT-x)** y cámbialo a **Enabled**.
* Presiona `F10` para guardar cambios y reiniciar.

#### 2. Habilitar componentes en Windows
1. En el menú de inicio de Windows busca: *Activar o desactivar las características de Windows*.
2. Asegúrate de marcar las casillas:
   * **Plataforma de máquina virtual**
   * **Subsistema de Windows para Linux (WSL2)**
3. Haz clic en **Aceptar** y reinicia el equipo cuando lo solicite.
