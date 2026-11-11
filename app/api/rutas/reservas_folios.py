from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencias import get_db, get_usuario_actual, requerir_rol, exigir_rol_recepcion_o_admin
from app.models.habitaciones import EstadoHabitacion
from app.models.finanzas import Cargo
from app.schemas.reservas_folios import ReservaCrear, ReservaRespuesta
from app.crud import crud_reservas_folios, crud_habitaciones

router = APIRouter()

@router.get("/", response_model=List[ReservaRespuesta], summary="Listar reservas y folios")
def listar_reservas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    return crud_reservas_folios.obtener_reservas(db, skip=skip, limit=limit)

@router.get("/{reserva_id}", summary="Obtener detalle de una reserva y su Cuenta Folio")
def obtener_detalle_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    resumen_folio = crud_reservas_folios.calcular_saldo_folio(db, reserva_id=reserva_id)
    habitaciones_info = [
        {
            "id_habitacion": h.id_habitacion,
            "numero_habitacion": h.numero_habitacion,
            "tipo": h.tipo,
            "precio_base": float(h.precio_base),
            "estado": h.estado.value if hasattr(h.estado, "value") else str(h.estado),
        }
        for h in reserva.habitaciones
    ]

    return {
        "id_reserva": reserva.id_reserva,
        "fecha_entrada": reserva.fecha_entrada,
        "fecha_salida": reserva.fecha_salida,
        "estado_reserva": reserva.estado_reserva,
        "estado_folio": reserva.estado_folio,
        "id_usuario": reserva.id_usuario,
        "id_huesped": reserva.id_huesped,
        "nombre_huesped": reserva.nombre_huesped,
        "rfc_huesped": reserva.huesped.rfc if reserva.huesped else None,
        "numeros_habitaciones": reserva.numeros_habitaciones,
        "habitaciones": habitaciones_info,
        "total_cargos": resumen_folio["total_cargos"],
        "total_pagos": resumen_folio["total_pagos"],
        "saldo_pendiente": resumen_folio["saldo_pendiente"],
        "cargos": [
            {
                "id_cargo": c.id_cargo,
                "descripcion": c.descripcion,
                "monto": float(c.monto),
                "fecha_creacion": c.fecha_creacion.strftime("%Y-%m-%d %H:%M") if c.fecha_creacion else "",
            }
            for c in resumen_folio["cargos"]
        ],
        "pagos": [
            {
                "id_pago": p.id_pago,
                "metodo_pago": p.metodo_pago,
                "monto": float(p.monto),
                "fecha_creacion": p.fecha_creacion.strftime("%Y-%m-%d %H:%M") if p.fecha_creacion else "",
            }
            for p in resumen_folio["pagos"]
        ],
    }

@router.post("/", response_model=ReservaRespuesta, status_code=status.HTTP_201_CREATED, summary="Crear una reserva")
def crear_reserva(
    reserva: ReservaCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(exigir_rol_recepcion_o_admin),
):
    
    # Lógica de negocio (F1SP3)
    # Asignar automáticamente el empleado autenticado (auditoría de sesión activa)
    reserva.id_usuario = usuario_actual.id_usuario
    
    # Validación de coherencia cronológica y prevención de fechas pasadas (RF-RES-003)
    if reserva.fecha_entrada < date.today():
        raise HTTPException(
            status_code=400,
            detail="No se pueden registrar reservas con fechas de entrada en el pasado."
        )

    if reserva.fecha_salida <= reserva.fecha_entrada:
        raise HTTPException(
            status_code=400, 
            detail="Error de lógica: La fecha de salida debe ser posterior a la fecha de entrada."
        )

    # Validación de existencia y estado físico de la habitación
    habitacion = crud_habitaciones.obtener_habitacion(db, habitacion_id=reserva.id_habitacion)
    if not habitacion:
        raise HTTPException(status_code=404, detail="La habitación solicitada no existe.")
    
    if habitacion.estado == EstadoHabitacion.MANTENIMIENTO:
        raise HTTPException(
            status_code=400,
            detail=f"La habitación {habitacion.numero_habitacion} se encuentra en Mantenimiento."
        )

    # RF-RES-003: Motor de Disponibilidad - Prevención de Overbooking por cruce de fechas
    disponible = crud_reservas_folios.verificar_disponibilidad_fechas(
        db,
        id_habitacion=reserva.id_habitacion,
        fecha_entrada=reserva.fecha_entrada,
        fecha_salida=reserva.fecha_salida,
    )
    if not disponible:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inventario no disponible para las fechas seleccionadas"
        )

    # OPERACIÓN CRUD
    nueva_reserva = crud_reservas_folios.crear_reserva(db=db, reserva=reserva)
    return nueva_reserva


# F1SP4 - Programar el Check-in
@router.post("/{reserva_id}/checkin", summary="Realizar Check-in y generar Cuenta Folio (F1SP4)")
def realizar_checkin(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(exigir_rol_recepcion_o_admin),
):
    
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.estado_reserva not in ["Pendiente", "Confirmada"]:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede hacer check-in. La reserva está '{reserva.estado_reserva}'."
        )

    # RF-HAB-004: Bloqueo operativo si la habitación no está estrictamente "Limpia"
    for hab in reserva.habitaciones:
        if hab.estado != EstadoHabitacion.LIMPIA:
            estado_txt = hab.estado.value if hasattr(hab.estado, "value") else str(hab.estado)
            raise HTTPException(
                status_code=400,
                detail=f"Bloqueo operativo: La habitación {hab.numero_habitacion} no está Limpia (estado actual: {estado_txt})."
            )

    # Calculamos noches de estadía y generamos el Cargo Automático de Hospedaje (RF-FAC-001 y RF-FAC-002)
    noches = max(1, (reserva.fecha_salida - reserva.fecha_entrada).days)
    monto_hospedaje_total = 0.0
    for hab in reserva.habitaciones:
        hab.estado = EstadoHabitacion.OCUPADA
        subtotal_hab = round(float(hab.precio_base) * noches, 2)
        monto_hospedaje_total += subtotal_hab
        cargo_hospedaje = Cargo(
            monto=subtotal_hab,
            descripcion=f"Hospedaje Hab. {hab.numero_habitacion} ({noches} noche(s) x ${float(hab.precio_base):.2f})",
            id_reserva=reserva_id,
        )
        db.add(cargo_hospedaje)

    reserva.estado_reserva = "Activa"
    reserva.estado_folio = "Abierto"
    db.commit()
    db.refresh(reserva)

    return {
        "mensaje": "Check-in realizado y Folio abierto con éxito.",
        "reserva_id": reserva_id,
        "nuevo_estado_reserva": "Activa",
        "nuevo_estado_folio": "Abierto",
        "noches": noches,
        "cargo_hospedaje_generado": round(monto_hospedaje_total, 2),
    }


# RF-RES-005 - Programar el Check-out
@router.post("/{reserva_id}/checkout", summary="Realizar Check-out validando saldo cero (RF-RES-005)")
def realizar_checkout(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(exigir_rol_recepcion_o_admin),
):
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.estado_reserva != "Activa":
        raise HTTPException(
            status_code=400,
            detail=f"Solo se puede realizar Check-out de una reserva 'Activa' (estado actual: '{reserva.estado_reserva}')."
        )

    resumen_folio = crud_reservas_folios.calcular_saldo_folio(db, reserva_id=reserva_id)
    if resumen_folio["saldo_pendiente"] > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede procesar el Check-out: la Cuenta Folio tiene un saldo pendiente de ${resumen_folio['saldo_pendiente']:.2f}."
        )

    # Liberar habitación(es) pasándolas a estado "Sucia" y cerrar Folio/Reserva
    for hab in reserva.habitaciones:
        hab.estado = EstadoHabitacion.SUCIA

    reserva.estado_reserva = "Finalizada"
    reserva.estado_folio = "Cerrado"
    db.commit()
    db.refresh(reserva)

    return {
        "mensaje": "Check-out realizado con éxito. Habitación marcada como Sucia y Folio cerrado.",
        "reserva_id": reserva_id,
        "nuevo_estado_reserva": "Finalizada",
        "nuevo_estado_folio": "Cerrado",
    }


# RF-RES-002 / RF-RES-003 - Cancelación de Reserva antes del Check-in
@router.patch("/{reserva_id}/cancelar", summary="Cancelar una reserva antes del Check-in (RF-RES-002)")
def cancelar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(exigir_rol_recepcion_o_admin),
):
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.estado_reserva not in ["Pendiente", "Confirmada"]:
        raise HTTPException(
            status_code=400,
            detail=f"Solo se pueden cancelar reservas en estado 'Pendiente' o 'Confirmada' (estado actual: '{reserva.estado_reserva}')."
        )

    reserva.estado_reserva = "Cancelada"
    reserva.estado_folio = "Cerrado"
    db.commit()
    db.refresh(reserva)

    return {
        "mensaje": f"Reserva #{reserva_id} cancelada con éxito. Las fechas han quedado liberadas en el inventario.",
        "reserva_id": reserva_id,
        "nuevo_estado_reserva": "Cancelada",
        "nuevo_estado_folio": "Cerrado",
    }