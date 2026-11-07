import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencias import get_db, get_usuario_actual
from app.schemas.finanzas import (
    CargoCrear,
    CargoRespuesta,
    PagoCrear,
    PagoRespuesta,
    FacturaSolicitar,
)
from app.crud import crud_finanzas, crud_reservas_folios

router = APIRouter()

# --- Endpoints de Cargos (RF-FAC-003) ---
@router.get("/cargos", response_model=List[CargoRespuesta], summary="Listar cargos")
def listar_cargos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    return crud_finanzas.obtener_cargos(db, skip=skip, limit=limit)

@router.post("/cargos", response_model=CargoRespuesta, summary="Crear un cargo manual/extra a la Cuenta Folio (RF-FAC-003)")
def crear_cargo(
    cargo: CargoCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=cargo.id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="La reserva especificada no existe.")
    if reserva.estado_folio != "Abierto":
        raise HTTPException(
            status_code=400,
            detail=f"No se pueden agregar cargos porque la Cuenta Folio está '{reserva.estado_folio}'."
        )
    if cargo.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto del cargo debe ser mayor a $0.00.")
    if not cargo.descripcion or not cargo.descripcion.strip():
        raise HTTPException(status_code=400, detail="La descripción del cargo es obligatoria.")

    return crud_finanzas.crear_cargo(db=db, cargo=cargo)

# --- Endpoints de Pagos (RF-FAC-004 y RNF-SEG-003) ---
@router.get("/pagos", response_model=List[PagoRespuesta], summary="Listar pagos")
def listar_pagos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    return crud_finanzas.obtener_pagos(db, skip=skip, limit=limit)

@router.post("/pagos", response_model=PagoRespuesta, summary="Registrar un pago descontando del saldo de la Cuenta Folio (RF-FAC-004)")
def crear_pago(
    pago: PagoCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=pago.id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="La reserva especificada no existe.")
    if reserva.estado_folio != "Abierto":
        raise HTTPException(
            status_code=400,
            detail=f"No se pueden registrar pagos porque la Cuenta Folio está '{reserva.estado_folio}'."
        )
    if pago.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto del pago debe ser mayor a $0.00.")

    resumen = crud_reservas_folios.calcular_saldo_folio(db, reserva_id=pago.id_reserva)
    if resumen["saldo_pendiente"] <= 0:
        raise HTTPException(status_code=400, detail="La Cuenta Folio ya se encuentra con saldo $0.00 (liquidada).")
    if round(pago.monto, 2) > round(resumen["saldo_pendiente"], 2):
        raise HTTPException(
            status_code=400,
            detail=f"El monto del pago (${pago.monto:.2f}) excede el saldo pendiente actual (${resumen['saldo_pendiente']:.2f})."
        )

    # RNF-SEG-003: Si el pago es con Tarjeta, se tokeniza sin almacenar PAN ni CVV
    if "tarjeta" in pago.metodo_pago.lower() and "tok_" not in pago.metodo_pago.lower():
        token_simulado = f"tok_{uuid.uuid4().hex[:8]}"
        pago.metodo_pago = f"Tarjeta (Token: {token_simulado})"

    pago.id_usuario = usuario_actual.id_usuario
    return crud_finanzas.crear_pago(db=db, pago=pago)

# --- Endpoint de Facturación Electrónica PAC Sandbox (RF-FAC-005) ---
@router.post("/facturar", summary="Timbrar Factura Electrónica ante el PAC (RF-FAC-005)")
def timbrar_factura_pac(
    datos_factura: FacturaSolicitar,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=datos_factura.id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    resumen = crud_reservas_folios.calcular_saldo_folio(db, reserva_id=datos_factura.id_reserva)
    if resumen["total_cargos"] <= 0:
        raise HTTPException(status_code=400, detail="El folio no tiene cargos registrados para facturar.")
    if resumen["saldo_pendiente"] > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Para timbrar la factura, la Cuenta Folio debe estar liquidada (Saldo pendiente: ${resumen['saldo_pendiente']:.2f})."
        )

    total = round(resumen["total_cargos"], 2)
    subtotal = round(total / 1.16, 2)
    iva = round(total - subtotal, 2)
    uuid_fiscal = str(uuid.uuid4()).upper()

    # Guardar o actualizar el RFC en el perfil del huésped para futuras estadías
    if reserva.huesped and datos_factura.rfc_cliente:
        reserva.huesped.rfc = datos_factura.rfc_cliente
        db.commit()

    return {
        "mensaje": "Factura timbrada exitosamente mediante PAC (Sandbox).",
        "uuid_fiscal": uuid_fiscal,
        "id_reserva": reserva.id_reserva,
        "rfc_receptor": datos_factura.rfc_cliente,
        "razon_social": datos_factura.razon_social or "PÚBLICO EN GENERAL",
        "subtotal": subtotal,
        "iva_16": iva,
        "total_facturado": total,
        "fecha_timbrado": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }