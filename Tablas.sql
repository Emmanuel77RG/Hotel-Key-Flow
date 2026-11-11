-- ==============================================================================
-- HOTEL KEYFLOW - ESQUEMA DE BASE DE DATOS DDL (PostgreSQL 15)
-- Sincronizado con los modelos SQLAlchemy y reglas de integridad referencial
-- ==============================================================================

-- 1. Tabla de Roles (RBAC)
CREATE TABLE IF NOT EXISTS roles (
    id_rol SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- 2. Tabla de Usuarios del Sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    id_rol INTEGER REFERENCES roles(id_rol),
    estado_activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de Huéspedes
CREATE TABLE IF NOT EXISTS huespedes (
    id_huesped SERIAL PRIMARY KEY,
    documento_identidad VARCHAR(50) UNIQUE NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    rfc VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla de Habitaciones
CREATE TABLE IF NOT EXISTS habitaciones (
    id_habitacion SERIAL PRIMARY KEY,
    numero_habitacion VARCHAR(10) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    capacidad INTEGER NOT NULL,
    precio_base NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Limpia' NOT NULL
);

-- 5. Tabla de Reservas y Cuentas (Folio)
CREATE TABLE IF NOT EXISTS reservas_folios (
    id_reserva SERIAL PRIMARY KEY,
    fecha_entrada DATE NOT NULL,
    fecha_salida DATE NOT NULL,
    estado_reserva VARCHAR(50) NOT NULL,
    estado_folio VARCHAR(50) NOT NULL,
    id_usuario INTEGER REFERENCES usuarios(id_usuario),
    id_huesped INTEGER REFERENCES huespedes(id_huesped),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabla Intermedia: Reservas - Habitaciones (Restricción RESTRICT contable)
CREATE TABLE IF NOT EXISTS reservas_habitaciones (
    id_reserva INTEGER REFERENCES reservas_folios(id_reserva) ON DELETE RESTRICT,
    id_habitacion INTEGER REFERENCES habitaciones(id_habitacion) ON DELETE RESTRICT,
    PRIMARY KEY (id_reserva, id_habitacion)
);

-- 7. Tabla de Mantenimiento de Instalaciones
CREATE TABLE IF NOT EXISTS tickets_mantenimiento (
    id_ticket SERIAL PRIMARY KEY,
    categoria VARCHAR(50) DEFAULT 'General' NOT NULL,
    prioridad VARCHAR(30) DEFAULT 'Media' NOT NULL,
    descripcion_falla VARCHAR(255) NOT NULL,
    estado_ticket VARCHAR(50) DEFAULT 'Pendiente' NOT NULL,
    nota_resolucion VARCHAR(255),
    id_habitacion INTEGER REFERENCES habitaciones(id_habitacion),
    id_usuario_reporta INTEGER REFERENCES usuarios(id_usuario),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP
);

-- 8. Tabla de Cargos a la Cuenta Folio (Restricción RESTRICT contable)
CREATE TABLE IF NOT EXISTS cargos (
    id_cargo SERIAL PRIMARY KEY,
    monto NUMERIC(10, 2) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    id_reserva INTEGER REFERENCES reservas_folios(id_reserva) ON DELETE RESTRICT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Tabla de Pagos de la Cuenta Folio (Restricción RESTRICT contable)
CREATE TABLE IF NOT EXISTS pagos (
    id_pago SERIAL PRIMARY KEY,
    monto NUMERIC(10, 2) NOT NULL,
    metodo_pago VARCHAR(100) NOT NULL,
    id_reserva INTEGER REFERENCES reservas_folios(id_reserva) ON DELETE RESTRICT,
    id_usuario INTEGER REFERENCES usuarios(id_usuario),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Tabla de Catálogo de Productos y Servicios (POS)
CREATE TABLE IF NOT EXISTS productos_pos (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    categoria VARCHAR(60) DEFAULT 'Restaurante / Alimentos' NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
