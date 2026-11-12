"""migracion_inicial_esquema

Revision ID: cafca216cd5b
Revises: 
Create Date: 2026-11-11 16:57:16.929711

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'cafca216cd5b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Roles
    op.create_table(
        'roles',
        sa.Column('id_rol', sa.Integer(), nullable=False),
        sa.Column('nombre_rol', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id_rol'),
        sa.UniqueConstraint('nombre_rol')
    )
    op.create_index(op.f('ix_roles_id_rol'), 'roles', ['id_rol'], unique=False)

    # 2. Usuarios
    op.create_table(
        'usuarios',
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('id_rol', sa.Integer(), nullable=True),
        sa.Column('estado_activo', sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['id_rol'], ['roles.id_rol'], ),
        sa.PrimaryKeyConstraint('id_usuario')
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id_usuario'), 'usuarios', ['id_usuario'], unique=False)

    # 3. Huéspedes
    op.create_table(
        'huespedes',
        sa.Column('id_huesped', sa.Integer(), nullable=False),
        sa.Column('documento_identidad', sa.String(length=50), nullable=False),
        sa.Column('nombre_completo', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('rfc', sa.String(length=20), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id_huesped')
    )
    op.create_index(op.f('ix_huespedes_documento_identidad'), 'huespedes', ['documento_identidad'], unique=True)
    op.create_index(op.f('ix_huespedes_id_huesped'), 'huespedes', ['id_huesped'], unique=False)

    # 4. Habitaciones
    op.create_table(
        'habitaciones',
        sa.Column('id_habitacion', sa.Integer(), nullable=False),
        sa.Column('numero_habitacion', sa.String(length=10), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('capacidad', sa.Integer(), nullable=False),
        sa.Column('precio_base', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('estado', sa.Enum('LIMPIA', 'SUCIA', 'EN_LIMPIEZA', 'OCUPADA', 'MANTENIMIENTO', name='estadohabitacion'), nullable=False),
        sa.PrimaryKeyConstraint('id_habitacion')
    )
    op.create_index(op.f('ix_habitaciones_id_habitacion'), 'habitaciones', ['id_habitacion'], unique=False)
    op.create_index(op.f('ix_habitaciones_numero_habitacion'), 'habitaciones', ['numero_habitacion'], unique=True)

    # 5. Reservas Folios
    op.create_table(
        'reservas_folios',
        sa.Column('id_reserva', sa.Integer(), nullable=False),
        sa.Column('fecha_entrada', sa.Date(), nullable=False),
        sa.Column('fecha_salida', sa.Date(), nullable=False),
        sa.Column('estado_reserva', sa.String(length=50), nullable=False),
        sa.Column('estado_folio', sa.String(length=50), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=True),
        sa.Column('id_huesped', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['id_huesped'], ['huespedes.id_huesped'], ),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ),
        sa.PrimaryKeyConstraint('id_reserva')
    )
    op.create_index(op.f('ix_reservas_folios_id_reserva'), 'reservas_folios', ['id_reserva'], unique=False)

    # 6. Tabla Intermedia reservas_habitaciones (con RESTRICT)
    op.create_table(
        'reservas_habitaciones',
        sa.Column('id_reserva', sa.Integer(), nullable=False),
        sa.Column('id_habitacion', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_habitacion'], ['habitaciones.id_habitacion'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['id_reserva'], ['reservas_folios.id_reserva'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id_reserva', 'id_habitacion')
    )

    # 7. Tickets Mantenimiento
    op.create_table(
        'tickets_mantenimiento',
        sa.Column('id_ticket', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=False),
        sa.Column('prioridad', sa.String(length=30), nullable=False),
        sa.Column('descripcion_falla', sa.String(length=255), nullable=False),
        sa.Column('estado_ticket', sa.String(length=50), nullable=False),
        sa.Column('nota_resolucion', sa.String(length=255), nullable=True),
        sa.Column('id_habitacion', sa.Integer(), nullable=True),
        sa.Column('id_usuario_reporta', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_resolucion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_habitacion'], ['habitaciones.id_habitacion'], ),
        sa.ForeignKeyConstraint(['id_usuario_reporta'], ['usuarios.id_usuario'], ),
        sa.PrimaryKeyConstraint('id_ticket')
    )
    op.create_index(op.f('ix_tickets_mantenimiento_id_ticket'), 'tickets_mantenimiento', ['id_ticket'], unique=False)

    # 8. Cargos (con RESTRICT y NUMERIC)
    op.create_table(
        'cargos',
        sa.Column('id_cargo', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('monto', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('descripcion', sa.String(length=255), nullable=False),
        sa.Column('id_reserva', sa.Integer(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['id_reserva'], ['reservas_folios.id_reserva'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id_cargo')
    )
    op.create_index(op.f('ix_cargos_id_cargo'), 'cargos', ['id_cargo'], unique=False)

    # 9. Pagos (con RESTRICT y NUMERIC)
    op.create_table(
        'pagos',
        sa.Column('id_pago', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('monto', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('metodo_pago', sa.String(length=100), nullable=False),
        sa.Column('id_reserva', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['id_reserva'], ['reservas_folios.id_reserva'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ),
        sa.PrimaryKeyConstraint('id_pago')
    )
    op.create_index(op.f('ix_pagos_id_pago'), 'pagos', ['id_pago'], unique=False)

    # 10. Productos POS
    op.create_table(
        'productos_pos',
        sa.Column('id_producto', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=120), nullable=False),
        sa.Column('categoria', sa.String(length=60), nullable=False),
        sa.Column('precio_unitario', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('disponible', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id_producto')
    )
    op.create_index(op.f('ix_productos_pos_id_producto'), 'productos_pos', ['id_producto'], unique=False)


def downgrade() -> None:
    op.drop_table('productos_pos')
    op.drop_table('pagos')
    op.drop_table('cargos')
    op.drop_table('tickets_mantenimiento')
    op.drop_table('reservas_habitaciones')
    op.drop_table('reservas_folios')
    op.drop_table('habitaciones')
    op.drop_table('huespedes')
    op.drop_table('usuarios')
    op.drop_table('roles')
