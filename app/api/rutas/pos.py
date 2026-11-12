from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencias import get_db, get_usuario_actual
from app.schemas.pos import (
    ProductoPOSCrear,
    ProductoPOSActualizar,
    ProductoPOSRespuesta,
    ComandaHabitacionCrear,
)
from app.schemas.finanzas import CargoRespuesta
from app.models.finanzas import Cargo
from app.crud import crud_pos, crud_reservas_folios

router = APIRouter()


@router.get(
    "/productos",
    response_model=List[ProductoPOSRespuesta],
    summary="Listar catálogo de productos y servicios del Punto de Venta",
)
def listar_productos_pos(
    solo_disponibles: bool = False,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    return crud_pos.obtener_productos(db, solo_disponibles=solo_disponibles)


@router.post(
    "/productos",
    response_model=ProductoPOSRespuesta,
    status_code=201,
    summary="Registrar un nuevo producto o servicio en el catálogo POS",
)
def crear_producto_pos(
    producto: ProductoPOSCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    try:
        return crud_pos.crear_producto(db, producto)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo registrar el producto en el catálogo: {exc}",
        )


@router.put(
    "/productos/{id_producto}",
    response_model=ProductoPOSRespuesta,
    summary="Actualizar un producto o servicio del catálogo POS",
)
def actualizar_producto_pos(
    id_producto: int,
    datos: ProductoPOSActualizar,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    actualizado = crud_pos.actualizar_producto(db, id_producto, datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="El producto especificado no existe.")
    return actualizado


@router.delete(
    "/productos/{id_producto}",
    summary="Eliminar un producto o servicio del catálogo POS",
)
def eliminar_producto_pos(
    id_producto: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    eliminado = crud_pos.eliminar_producto(db, id_producto)
    if not eliminado:
        raise HTTPException(status_code=404, detail="El producto especificado no existe.")
    return {"mensaje": "Producto eliminado correctamente del catálogo."}


@router.post(
    "/cargar-habitacion",
    response_model=CargoRespuesta,
    status_code=201,
    summary="Enviar comanda de consumo directamente a la Cuenta Folio de una habitación (RF-POS-001 / RF-POS-007)",
)
def cargar_comanda_a_habitacion(
    comanda: ComandaHabitacionCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=comanda.id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="La reserva o folio especificado no existe.")

    if reserva.estado_folio != "Abierto":
        raise HTTPException(
            status_code=400,
            detail=f"No se puede enviar la comanda porque la Cuenta Folio se encuentra en estado '{reserva.estado_folio}'.",
        )

    if reserva.estado_reserva not in ("Activa", "Confirmada"):
        raise HTTPException(
            status_code=400,
            detail=f"La reserva asociada se encuentra en estado '{reserva.estado_reserva}' y no admite nuevos consumos.",
        )

    monto_total = round(
        sum(float(item.cantidad) * float(item.precio_unitario) for item in comanda.items),
        2,
    )
    if monto_total <= 0:
        raise HTTPException(
            status_code=400,
            detail="El monto total de la comanda debe ser mayor a $0.00.",
        )

    modalidad = (comanda.modalidad_servicio or "Room Service").strip()
    desglose_items = ", ".join(f"{item.cantidad}x {item.nombre}" for item in comanda.items)
    descripcion_cargo = f"[POS {modalidad}] {desglose_items}"
    if comanda.notas and comanda.notas.strip():
        descripcion_cargo += f" | Nota: {comanda.notas.strip()}"

    # Asegurar que no exceda los 255 caracteres de la columna en PostgreSQL
    if len(descripcion_cargo) > 252:
        descripcion_cargo = descripcion_cargo[:249] + "..."

    try:
        nuevo_cargo = Cargo(
            id_reserva=comanda.id_reserva,
            monto=monto_total,
            descripcion=descripcion_cargo,
        )
        db.add(nuevo_cargo)
        db.commit()
        db.refresh(nuevo_cargo)
        return nuevo_cargo
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error transaccional al registrar el cargo en la Cuenta Folio: {exc}",
        )
