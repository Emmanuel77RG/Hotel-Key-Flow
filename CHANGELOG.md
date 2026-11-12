# Changelog - Hotel KeyFlow

Todos los cambios notables de este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.7.0] - 2026-11-11
### Añadido
- **Punto de Venta (POS):** Catálogo de productos y alimentos, comandas con cargo directo a la Cuenta Folio y venta directa en mostrador.
- **Reportes Operativos:** Reporte ejecutivo con métricas de ocupación, inventario físico, auditoría por turno y balance financiero.
- **Corte de Caja:** Módulo de liquidación y arqueo de caja diario con generación de comprobantes en PDF.
- **Healthcheck Endpoint:** Endpoint `/health` con monitoreo activo de conectividad con PostgreSQL.
- **Control de Acceso RBAC:** Fábrica de dependencias `requerir_rol(*roles)` con respuesta `403 Forbidden` para roles no autorizados.
- **Validaciones Pydantic:** Restricciones estrictas `Field(gt=0)` para capacidades y montos, y `min_length=6` para contraseñas.
- **Script de Siembra:** `scripts/seed_roles.py` para provisión idempotente de roles (Admin, Recepción, Limpieza).
- **Plantilla de Entorno:** `.env.example` y soporte de carga con `python-dotenv`.
- **Healthcheck Docker:** Comando `pg_isready` en contenedor de base de datos.

### Modificado
- Restricción del puerto de PostgreSQL en Docker para vincular exclusivamente a `127.0.0.1:5432:5432`.
- `app/db/database.py` ahora consume `SQLALCHEMY_DATABASE_URL` centralizada desde `config.py`.
- Eliminación de la definición redundante de `get_db` en la capa de base de datos.
- Validación de fecha mínima en reservas para impedir fechas de entrada en el pasado (`HTTP 400`).

### Eliminado
- Endpoint obsoleto e inseguro `POST /usuarios/setup-roles`.
- Importaciones duplicadas en `app/main.py`.

---

## [0.5.0] - 2026-11-05
### Añadido
- Módulo de Mantenimiento (`tickets_mantenimiento`) con transición automática del estado de habitación a `Mantenimiento` y liberación a `Sucia`.
- Integración de interfaz de escritorio para control de incidencias operativas.

---

## [0.4.0] - 2026-10-28
### Añadido
- Check-in transaccional con validación de estado `Limpia`, transición a `Ocupada`, apertura de folio y cargo automático de tarifa por noches.
- Check-out con validación estricta de saldo cero, transición a `Sucia` y cierre de folio.
- Facturación electrónica con mock PAC y validación estricta de formato RFC vía regex (`HTTP 422`).

---

## [0.3.0] - 2026-10-15
### Añadido
- Motor de Reservas y prevención de overbooking por solapamiento de fechas (`HTTP 409 Conflict`).
- Módulo de Huéspedes con integridad referencial frente a reservaciones.

---

## [0.2.0] - 2026-09-25
### Añadido
- Gestión de Habitaciones y tipos de inventario.
- Autenticación JWT con hashing Bcrypt.
- Borrado lógico y control de estado activo para cuentas de usuario.

---

## [0.1.0] - 2026-09-02
### Añadido
- Estructura base del proyecto y configuración de FastAPI y PostgreSQL con Docker.
