from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencias import get_db, get_usuario_actual
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

@router.post("/", response_model=HuespedRespuesta, summary="Registrar un nuevo huésped")
def crear_huesped(
    huesped: HuespedCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    existente = crud_huespedes.obtener_huesped_por_documento(db, documento_identidad=huesped.documento_identidad)
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un huésped registrado con ese documento de identidad"
        )
    return crud_huespedes.crear_huesped(db=db, huesped=huesped)

@router.put("/{id_huesped}", response_model=HuespedRespuesta, summary="Modificar datos de un huésped")
def modificar_huesped(
    id_huesped: int,
    datos: HuespedActualizar,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    if datos.documento_identidad:
        existente = crud_huespedes.obtener_huesped_por_documento(db, documento_identidad=datos.documento_identidad)
        if existente and existente.id_huesped != id_huesped:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro huésped registrado con ese documento de identidad"
            )
    actualizado = crud_huespedes.actualizar_huesped(db, id_huesped=id_huesped, datos=datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")
    return actualizado