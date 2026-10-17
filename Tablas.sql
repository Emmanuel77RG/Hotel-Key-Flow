-- 1. Tabla de Huéspedes
CREATE TABLE huespedes (
    id_huesped SERIAL PRIMARY KEY,
    documento_identidad VARCHAR(50) NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Habitaciones
CREATE TABLE habitaciones (
    id_habitacion SERIAL PRIMARY KEY,
    numero_habitacion VARCHAR(10) NOT NULL,
    tipo_habitacion VARCHAR(50) NOT NULL,
    capacidad INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'Sucia',
    tarifa_base DECIMAL(10,2) NOT NULL
);

-- 3. Tabla de Reservas y Cuentas (Folio)
CREATE TABLE reservas_folios (
    id_reserva SERIAL PRIMARY KEY,
    fecha_entrada DATE NOT NULL,
    fecha_salida DATE NOT NULL,
    estado_reserva VARCHAR(50) NOT NULL, -- ej: Confirmada, Cancelada, Check-in
    estado_folio VARCHAR(50) NOT NULL,   -- ej: Abierta, Pagada, Cerrada
    id_usuario INTEGER REFERENCES usuarios(id_usuario), -- Recepcionista
    id_huesped INTEGER REFERENCES huespedes(id_huesped),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla Intermedia: Reservas - Habitaciones
CREATE TABLE reservas_habitaciones (
    id_reserva INTEGER REFERENCES reservas_folios(id_reserva) ON DELETE CASCADE,
    id_habitacion INTEGER REFERENCES habitaciones(id_habitacion) ON DELETE CASCADE,
    PRIMARY KEY (id_reserva, id_habitacion)
);

-- 5. Tabla de Mantenimiento
CREATE TABLE tickets_mantenimiento (
    id_ticket SERIAL PRIMARY KEY,
    descripcion_falla VARCHAR(255) NOT NULL,
    estado_ticket VARCHAR(50) NOT NULL, -- ej: Pendiente, Resuelto
    id_habitacion INTEGER REFERENCES habitaciones(id_habitacion),
    id_usuario_reporta INTEGER REFERENCES usuarios(id_usuario),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP
);

-- 6. Tabla de Cargos (Suman a la deuda)
CREATE TABLE cargos (
    id_cargo SERIAL PRIMARY KEY,
    monto DECIMAL(10,2) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    id_reserva INTEGER REFERENCES reservas_folios(id_reserva) ON DELETE CASCADE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Tabla de Pagos (Restan a la deuda)
CREATE TABLE pagos (
    id_pago SERIAL PRIMARY KEY,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(50) NOT NULL, -- ej: Tarjeta, Efectivo, Transferencia
    id_reserva INTEGER REFERENCES reservas_folios(id_reserva) ON DELETE CASCADE,
    id_usuario INTEGER REFERENCES usuarios(id_usuario), -- Quien cobró
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);