from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.api.dependencias import get_db, get_usuario_actual, exigir_rol_recepcion_o_admin
from app.models.reservas_folios import ReservaFolio
from app.schemas.huespedes import HuespedCrear, HuespedActualizar, HuespedRespuesta
from app.crud import crud_huespedes

router = APIRouter()

@router.get("/", response_model=List[HuespedRespuesta], summary="Listar huéspedes")
def listar_huespedes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    return crud_huespedes.obtener_huespedes(db, skip=skip, limit=limit)

@router.post("/", response_model=HuespedRespuesta, status_code=status.HTTP_201_CREATED, summary="Registrar un nuevo huésped")
def crear_huesped(
    huesped: HuespedCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(exigir_rol_recepcion_o_admin),
):
    if not huesped.nombre_completo or not huesped.nombre_completo.strip():
        raise HTTPException(status_code=400, detail="El nombre completo del huésped es obligatorio")

    doc_existente = crud_huespedes.obtener_huesped_por_documento(db, documento_identidad=huesped.documento_identidad)
    if doc_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un huésped registrado con el documento de identidad '{huesped.documento_identidad}'.",
        )

    try:
        return crud_huespedes.crear_huesped(db=db, huesped=huesped)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de integridad referencial: el documento de identidad ya se encuentra registrado.",
        )

@router.put("/{id_huesped}", response_model=HuespedRespuesta, summary="Modificar datos de un huésped")
def modificar_huesped(
    id_huesped: int,
    datos: HuespedActualizar,
    db: Session = Depends(get_db),
    usuario_actual=Depends(exigir_rol_recepcion_o_admin),
):
    if datos.documento_identidad is not None:
        doc_ocupado = crud_huespedes.obtener_huesped_por_documento(db, documento_identidad=datos.documento_identidad)
        if doc_ocupado and doc_ocupado.id_huesped != id_huesped:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El documento '{datos.documento_identidad}' ya pertenece a otro huésped registrado.",
            )

    try:
        actualizado = crud_huespedes.actualizar_huesped(db, id_huesped=id_huesped, datos=datos)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Huésped no encontrado")
        return actualizado
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de integridad: conflicto con documento de identidad duplicado.",
        )

@router.delete("/{id_huesped}", summary="Eliminar un huésped sin reservas asociadas (RF-RES-001)")
def eliminar_huesped(
    id_huesped: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(exigir_rol_recepcion_o_admin),
):
    huesped = crud_huespedes.obtener_huesped(db, id_huesped=id_huesped)
    if not huesped:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")

    # Regla de Integridad Referencial (Sección 19.2): impedir borrado si tiene reservaciones asociadas
    reserva_asociada = db.query(ReservaFolio).filter(ReservaFolio.id_huesped == id_huesped).first()
    if reserva_asociada:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar este huésped porque ya cuenta con reservaciones registradas (Integridad Referencial)."
        )

    crud_huespedes.eliminar_huesped(db, id_huesped=id_huesped)
    return {"mensaje": f"Huésped '{huesped.nombre_completo}' (#{id_huesped}) eliminado correctamente."}
