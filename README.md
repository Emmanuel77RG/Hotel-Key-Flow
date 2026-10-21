# 🏨 Hotel KeyFlow - Sistema de Gestión Hotelera

**Hotel KeyFlow** es un Property Management System (PMS) diseñado para operar en un entorno local (On-Premise). Su objetivo es gestionar las reservaciones, el inventario de habitaciones, la limpieza, el punto de venta y la facturación de manera segura y eficiente.

El proyecto está desarrollado bajo una arquitectura cliente-servidor estrictamente local, con un backend construido en **FastAPI**, persistencia de datos en **PostgreSQL** (vía Docker) y una interfaz de escritorio nativa en **Python (CustomTkinter)**.

---

## 🛠️ Tecnologías y Herramientas
* **Backend:** Python 3.12, FastAPI, Uvicorn.
* **Base de Datos:** PostgreSQL 15 (aislado en contenedor Docker).
* **ORM:** SQLAlchemy.
* **Validación de Datos:** Pydantic.
* **Seguridad:** Passlib (Bcrypt) y JWT para tokens de sesión.
* **Frontend:** Python, CustomTkinter, Requests.

---

## 🚀 Requisitos Previos
Para ejecutar este proyecto en tu entorno local, asegúrate de tener instalado:
1. [Python 3.12.7]([https://www.python.org/downloads/](https://www.python.org/downloads/release/python-3127/))
2. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Para levantar la base de datos).
3. [Git](https://git-scm.com/)

---

## ⚙️ Configuración e Instalación

### 1. Clonar el repositorio
Abre tu terminal y clona este repositorio en tu computadora:
```bash
git clone [https://github.com/Emmanuel77RG/Hotel-Key-Flow.git](https://github.com/Emmanuel77RG/Hotel-Key-Flow.git)
cd Hotel-KeyFlow
````

### 2. Configurar el Entorno Virtual
Es obligatorio el uso de un entorno virtual para aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual (Windows - PowerShell)
.venv\Scripts\Activate.ps1
# Activar el entorno virtual (Mac/Linux)
# source .venv/bin/activate
````
Nota: Si al activar el entorno virtual surge un errorde bloqueo por PowerShell ejecutar el siguiente comando:
```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
```

### 3. Instalar las Dependencias
Con el entorno activado, instala todas las librerías necesarias ejecutando:

```bash
pip install -r requirements.txt
````

### 4. Configurar Variables de Entorno (.env)
Por seguridad (Cero Hardcoding), las contraseñas y llaves jamás se suben al repositorio. Crea un archivo llamado .env en la raíz del proyecto y agrega las siguientes variables (ajusta las contraseñas según tu entorno):

```bash
DATABASE_URL=postgresql://postgres:TU_PASSWORD_SEGURO@localhost:5432/keyflow_db
SECRET_KEY=tu_super_llave_secreta_jwt_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
````
(Nota: El archivo .env ya está ignorado por nuestro .gitignore).


## 🗄️ Configuración de la Base de Datos (Docker y Tablas)
### 1. Levantar el Contenedor PostgreSQL
Asegúrate de tener Docker Desktop abierto. El proyecto incluye un archivo docker-compose.yml. Para levantar el motor de base de datos aislado, ejecuta:

```bash
docker-compose up -d
````
Esto descargará la imagen de PostgreSQL 15, creará la base de datos y la expondrá de forma segura en el puerto 5432 de tu red local.

### 2. Creación de las Tablas (Migraciones)
El sistema utiliza SQLAlchemy como ORM. Para crear las tablas (Usuarios, Habitaciones, Huéspedes, etc.) directamente en la base de datos vacía, el servidor FastAPI lo hará automáticamente al arrancar, o puedes ejecutar el script de inicialización:

```bash
Nota: Si el equipo de desarrollo configuró Alembic para migraciones, ejecuta:
alembic upgrade head
````

## ▶️ Ejecución del Proyecto
Para poder utilizar el sistema, debes correr tanto el servidor (Backend) como el cliente de escritorio (Frontend) al mismo tiempo en dos terminales separadas.

### 1. Ejecutar el Servidor Backend (API)
En tu primera terminal (con el entorno virtual activado), ejecuta:

```bash
uvicorn app.main:app --reload
La API estará disponible en: http://127.0.0.1:8000
````
Puedes consultar la documentación interactiva (Swagger) generada automáticamente en: http://127.0.0.1:8000/docs

### 2. Ejecutar la Aplicación de Escritorio
Abre una segunda terminal, asegúrate de que el entorno virtual también esté activado ahí, y ejecuta la interfaz gráfica:

```bash
python desktop_client/login_gui.py
````
¡Listo! Verás la pantalla de inicio de sesión. Puedes ingresar con los usuarios de prueba creados en tu base de datos (Ej. Administrador o Recepción).

### 🔒 Estándares de Colaboración (GitHub Flow)
Este proyecto sigue estrictas compuertas de calidad. Todo desarrollador debe:

No programar directamente en la rama main.

Crear una rama aislada: git checkout -b feature/nombre-del-modulo

Abrir un Pull Request (PR) en GitHub para la revisión de código por pares antes de integrar cualquier cambio.

---


## ⚠️ Solución de Problemas (Troubleshooting)

**Error de Docker: Virtualización deshabilitada en la BIOS**
Si al intentar iniciar el programa Docker Desktop te aparece un error rojo indicando que la "virtualización por hardware" no está disponible, significa que tu computadora tiene esta función de procesamiento apagada desde fábrica. Para solucionarlo, no necesitas ser un experto, solo sigue estos dos pasos:

### 1. Activar la virtualización en la BIOS
Primero, debemos entrar al sistema de configuración básico de tu computadora (la BIOS).

- Apaga tu computadora por completo.
- Enciéndela y, antes de que aparezca el logo de Windows o de la marca cargando, presiona repetidamente la **tecla de acceso a la BIOS**. Esta tecla cambia según la marca de tu computadora:
  * **MSI:** `Supr` (Delete) o `Del`
  * **Lenovo:** `F2` o `Fn + F2`
  * **Toshiba / Dynabook:** `F2`
  * **HP:** `F10` o `Esc`
  * **Dell:** `F2`
  * **Asus:** `F2` o `Supr` (Del)
  * **Acer:** `F2` o `Supr` (Del)

- Una vez dentro de la BIOS (que suele ser una pantalla gris, azul o con el diseño de la marca), usa las flechas de tu teclado o el mouse para buscar la configuración avanzada (suele llamarse `Advanced` o `CPU Configuration`).
- Localiza la opción de virtualización. Si tu procesador es AMD se llamará **SVM Mode**, y si es Intel se llamará **Intel Virtualization Technology (VT-x)**.
- Cambia la opción para que diga **Enabled** (Habilitado).
- Presiona la tecla `F10` para guardar los cambios y salir. Tu computadora se reiniciará sola.

### 2. Verificar características de Windows
Una vez que tu computadora encendió normalmente y ya estás en tu escritorio de Windows, debemos asegurarnos de que el sistema reconozca esta función.

1. **Abre el buscador:** Haz clic en el botón de Inicio de Windows.
2. **Busca la herramienta:** Buscar *Activar o desactivar las características de Windows* y haz clic en el resultado que te aparezca (suele tener el ícono de una ventanita con un disco o un bloque).
3. **Explora la lista:** Se abrirá una ventana pequeña con una lista de opciones que tienen un cuadrito a la izquierda. Usa la barra lateral para bajar por la lista con calma.
4. **Marca las casillas correctas:** Busca estas dos opciones específicas y haz clic en sus cuadritos para asegurarte de que tengan una "palomita" (✔) azul o negra:
   * **Plataforma de máquina virtual**
   * **Subsistema de Windows para Linux**
5. **Aplica los cambios:** Haz clic en el botón **Aceptar** en la parte inferior. Windows comenzará a cargar y aplicar los cambios. Es normal que tarde un par de minutos.
6. **Reinicia tu equipo:** Al terminar, la misma pantalla te avisará que necesita reiniciar la computadora para finalizar. Haz clic en el botón "Reiniciar ahora".

¡Y listo! Al encender nuevamente, podrás abrir Docker Desktop sin ningún mensaje de error y levantar la base de datos del hotel.
