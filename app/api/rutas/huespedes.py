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
    if not huesped.nombre_completo or not huesped.nombre_completo.strip():
        raise HTTPException(status_code=400, detail="El nombre completo del huésped es obligatorio")
    if not huesped.documento_identidad or huesped.documento_identidad.strip() in ("", "Selecciona una opción"):
        huesped.documento_identidad = "Sin especificar"
    return crud_huespedes.crear_huesped(db=db, huesped=huesped)

@router.put("/{id_huesped}", response_model=HuespedRespuesta, summary="Modificar datos de un huésped")
def modificar_huesped(
    id_huesped: int,
    datos: HuespedActualizar,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    if datos.documento_identidad is not None and datos.documento_identidad.strip() in ("", "Selecciona una opción"):
        datos.documento_identidad = "Sin especificar"
    actualizado = crud_huespedes.actualizar_huesped(db, id_huesped=id_huesped, datos=datos)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Huésped no encontrado")
    return actualizado