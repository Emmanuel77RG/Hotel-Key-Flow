from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.api.dependencias import get_db, get_usuario_actual
from app.models.habitaciones import Habitacion
from app.models.huespedes import Huesped
from app.models.reservas_folios import ReservaFolio
from app.models.finanzas import Cargo, Pago
from app.models.mantenimiento import TicketMantenimiento
from app.models.usuarios import Usuario
from app.core.security import enmascarar_token_pago

router = APIRouter()


@router.get(
    "/resumen",
    summary="Obtener reporte ejecutivo, operativo y corte de caja (RF-REP-001)",
)
def obtener_resumen_reportes(
    fecha: Optional[str] = None,
    solo_mi_turno: bool = False,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    fecha_filtro: Optional[date] = None
    if fecha and fecha.strip() and fecha.strip().lower() != "todos":
        try:
            fecha_filtro = datetime.strptime(fecha.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha inválido. Utilice AAAA-MM-DD (ej. 2026-11-09).",
            )

    # 1. Inventario y Ocupación de Habitaciones
    habitaciones = db.query(Habitacion).all()
    total_habs = len(habitaciones)
    conteo_estados = {
        "Ocupada": 0,
        "Limpia": 0,
        "Sucia": 0,
        "En Limpieza": 0,
        "Mantenimiento": 0,
    }
    for h in habitaciones:
        est = h.estado or "Sucia"
        conteo_estados[est] = conteo_estados.get(est, 0) + 1

    ocupadas = conteo_estados.get("Ocupada", 0)
    porcentaje_ocupacion = round((ocupadas / total_habs) * 100.0, 1) if total_habs > 0 else 0.0

    # 2. Mapa de Usuarios y Reservas con joinedload para evitar N+1 queries
    usuarios_map = {
        u.id_usuario: u.nombre
        for u in db.query(Usuario).all()
    }
    reservas = (
        db.query(ReservaFolio)
        .options(joinedload(ReservaFolio.huesped), joinedload(ReservaFolio.habitaciones))
        .order_by(ReservaFolio.id_reserva.desc())
        .all()
    )
    reservas_map = {r.id_reserva: r for r in reservas}

    # 3. Todos los cargos y pagos para calcular saldo pendiente en folios abiertos y corte de caja
    todos_cargos = db.query(Cargo).order_by(Cargo.id_cargo.desc()).all()
    todos_pagos = db.query(Pago).order_by(Pago.id_pago.desc()).all()

    cargos_por_res = {}
    for c in todos_cargos:
        cargos_por_res[c.id_reserva] = cargos_por_res.get(c.id_reserva, 0.0) + float(c.monto or 0.0)

    pagos_por_res = {}
    for p in todos_pagos:
        pagos_por_res[p.id_reserva] = pagos_por_res.get(p.id_reserva, 0.0) + float(p.monto or 0.0)

    saldo_por_cobrar_folios = 0.0
    for r in reservas:
        if r.estado_folio == "Abierto" and r.estado_reserva != "Cancelada":
            dif = round(cargos_por_res.get(r.id_reserva, 0.0) - pagos_por_res.get(r.id_reserva, 0.0), 2)
            if dif > 0:
                saldo_por_cobrar_folios = round(saldo_por_cobrar_folios + dif, 2)

    # 4. Filtrado de Pagos (Corte de Caja RF-REP-001)
    pagos_filtrados = []
    total_recaudado = 0.0
    total_efectivo = 0.0
    total_tarjeta = 0.0

    for p in todos_pagos:
        if solo_mi_turno and p.id_usuario != usuario_actual.id_usuario:
            continue
        if fecha_filtro and p.fecha_creacion and p.fecha_creacion.date() != fecha_filtro:
            continue

        monto_p = round(float(p.monto or 0.0), 2)
        metodo = p.metodo_pago or "Efectivo"
        total_recaudado = round(total_recaudado + monto_p, 2)
        if "efectivo" in metodo.lower():
            total_efectivo = round(total_efectivo + monto_p, 2)
        else:
            total_tarjeta = round(total_tarjeta + monto_p, 2)

        res_obj = reservas_map.get(p.id_reserva)
        hab_str = res_obj.numeros_habitaciones if res_obj else "S/N"
        huesped_str = (
            res_obj.nombre_huesped
            if res_obj and res_obj.nombre_huesped
            else (f"Huésped #{res_obj.id_huesped}" if res_obj else "General")
        )
        cajero_str = usuarios_map.get(p.id_usuario) or usuario_actual.nombre
        es_admin = getattr(usuario_actual, "id_rol", None) == 1
        metodo_mostrar = metodo if es_admin else enmascarar_token_pago(metodo)

        pagos_filtrados.append(
            {
                "id_pago": p.id_pago,
                "id_reserva": p.id_reserva,
                "habitaciones": hab_str,
                "huesped": huesped_str,
                "metodo_pago": metodo_mostrar,
                "monto": monto_p,
                "cajero": cajero_str,
                "fecha_creacion": p.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if p.fecha_creacion else "",
                "token_auditoria": metodo if es_admin else None,
            }
        )

    # 5. Filtrado de Cargos (Hospedaje vs Punto de Venta)
    cargos_filtrados = []
    total_cargos_periodo = 0.0
    cargos_hospedaje = 0.0
    cargos_pos = 0.0

    for c in todos_cargos:
        if fecha_filtro and c.fecha_creacion and c.fecha_creacion.date() != fecha_filtro:
            continue

        monto_c = round(float(c.monto or 0.0), 2)
        desc_c = c.descripcion or ""
        es_pos = desc_c.strip().upper().startswith("[POS")
        total_cargos_periodo = round(total_cargos_periodo + monto_c, 2)
        if es_pos:
            cargos_pos = round(cargos_pos + monto_c, 2)
        else:
            cargos_hospedaje = round(cargos_hospedaje + monto_c, 2)

        res_obj = reservas_map.get(c.id_reserva)
        hab_str = res_obj.numeros_habitaciones if res_obj else "S/N"
        huesped_str = (
            res_obj.nombre_huesped
            if res_obj and res_obj.nombre_huesped
            else (f"Huésped #{res_obj.id_huesped}" if res_obj else "General")
        )

        cargos_filtrados.append(
            {
                "id_cargo": c.id_cargo,
                "id_reserva": c.id_reserva,
                "habitaciones": hab_str,
                "huesped": huesped_str,
                "descripcion": desc_c,
                "monto": monto_c,
                "es_pos": es_pos,
                "fecha_creacion": c.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if c.fecha_creacion else "",
            }
        )

    # 6. Listado de Llegadas (Check-ins) y Salidas (Check-outs)
    llegadas = []
    salidas = []
    for r in reservas:
        if r.estado_reserva == "Cancelada":
            continue
        item_res = {
            "id_reserva": r.id_reserva,
            "huesped": r.nombre_huesped or f"Huésped #{r.id_huesped}",
            "habitaciones": r.numeros_habitaciones,
            "fecha_entrada": str(r.fecha_entrada),
            "fecha_salida": str(r.fecha_salida),
            "estado_reserva": r.estado_reserva,
            "estado_folio": r.estado_folio,
            "total_cargos": round(cargos_por_res.get(r.id_reserva, 0.0), 2),
            "total_pagos": round(pagos_por_res.get(r.id_reserva, 0.0), 2),
        }
        if fecha_filtro:
            if r.fecha_entrada == fecha_filtro:
                llegadas.append(item_res)
            if r.fecha_salida == fecha_filtro:
                salidas.append(item_res)
        else:
            if r.estado_reserva in ("Activa", "Confirmada"):
                llegadas.append(item_res)
            if r.estado_reserva in ("Finalizada", "Activa"):
                salidas.append(item_res)

    # 7. Resumen de Mantenimiento
    tickets = db.query(TicketMantenimiento).all()
    mant_pend = sum(1 for t in tickets if t.estado_ticket == "Pendiente")
    mant_rep = sum(1 for t in tickets if t.estado_ticket == "En Reparación")
    mant_crit = sum(
        1 for t in tickets
        if t.estado_ticket != "Resuelto" and (t.prioridad or "Media") == "Crítica"
    )
    mant_res = sum(1 for t in tickets if t.estado_ticket == "Resuelto")

    return {
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filtro_fecha": str(fecha_filtro) if fecha_filtro else "Todo el historial",
        "solo_mi_turno": solo_mi_turno,
        "cajero_actual": {
            "id_usuario": usuario_actual.id_usuario,
            "nombre": usuario_actual.nombre,
            "email": usuario_actual.email,
        },
        "ocupacion": {
            "total_habitaciones": total_habs,
            "ocupadas": ocupadas,
            "limpias": conteo_estados.get("Limpia", 0),
            "sucias": conteo_estados.get("Sucia", 0),
            "en_limpieza": conteo_estados.get("En Limpieza", 0),
            "mantenimiento": conteo_estados.get("Mantenimiento", 0),
            "porcentaje_ocupacion": porcentaje_ocupacion,
        },
        "finanzas": {
            "total_recaudado": total_recaudado,
            "total_efectivo": total_efectivo,
            "total_tarjeta": total_tarjeta,
            "num_pagos": len(pagos_filtrados),
            "total_cargos_periodo": total_cargos_periodo,
            "cargos_hospedaje": cargos_hospedaje,
            "cargos_pos": cargos_pos,
            "saldo_por_cobrar_folios": saldo_por_cobrar_folios,
        },
        "pagos_detalle": pagos_filtrados,
        "cargos_detalle": cargos_filtrados,
        "movimientos_operativos": {
            "llegadas": llegadas,
            "salidas": salidas,
        },
        "mantenimiento": {
            "pendientes": mant_pend,
            "en_reparacion": mant_rep,
            "criticos_activos": mant_crit,
            "resueltos": mant_res,
        },
    }
