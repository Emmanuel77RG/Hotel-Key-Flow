from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import habitaciones as schemas
from app.models.habitaciones import EstadoHabitacion
from app.crud import crud_habitaciones
from app.api.dependencias import get_db, get_usuario_actual, exigir_rol_admin

router = APIRouter()

# Matriz formal de transiciones de la Máquina de Estados de Habitaciones
TRANSICIONES_PERMITIDAS = {
    EstadoHabitacion.SUCIA: [EstadoHabitacion.EN_LIMPIEZA, EstadoHabitacion.MANTENIMIENTO],
    EstadoHabitacion.EN_LIMPIEZA: [EstadoHabitacion.LIMPIA, EstadoHabitacion.SUCIA, EstadoHabitacion.MANTENIMIENTO],
    EstadoHabitacion.LIMPIA: [EstadoHabitacion.EN_LIMPIEZA, EstadoHabitacion.OCUPADA, EstadoHabitacion.MANTENIMIENTO],
    EstadoHabitacion.OCUPADA: [EstadoHabitacion.SUCIA, EstadoHabitacion.MANTENIMIENTO],
    EstadoHabitacion.MANTENIMIENTO: [EstadoHabitacion.SUCIA],
}

@router.post("/", response_model=schemas.HabitacionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_habitacion(
    habitacion: schemas.HabitacionCrear, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(exigir_rol_admin) # RF-HAB-001: Solo Administrador registra habitaciones
):
    db_habitacion = crud_habitaciones.obtener_habitacion_por_numero(db, numero=habitacion.numero_habitacion)
    if db_habitacion:
        raise HTTPException(status_code=400, detail="El número de habitación ya existe")
    return crud_habitaciones.crear_habitacion(db=db, habitacion=habitacion)

@router.get("/", response_model=List[schemas.HabitacionRespuesta])
def listar_habitaciones(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual)
):
    return crud_habitaciones.obtener_habitaciones(db, skip=skip, limit=limit)

@router.patch("/{id_habitacion}/estado", response_model=schemas.HabitacionRespuesta)
def cambiar_estado_limpieza(
    id_habitacion: int, 
    estado_update: schemas.HabitacionEstadoUpdate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual)
):
    habitacion = crud_habitaciones.obtener_habitacion(db, id_habitacion)
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    estado_actual = habitacion.estado
    nuevo_estado = estado_update.estado

    # Si ya tiene el estado solicitado, retornar sin cambios
    if estado_actual == nuevo_estado:
        return habitacion

    # Regla RBAC: Limpieza no puede colocar habitaciones en "Ocupada" arbitrariamente
    if nuevo_estado == EstadoHabitacion.OCUPADA and usuario_actual.id_rol == 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación denegada: el personal de limpieza no puede marcar habitaciones como 'Ocupada'. Este estado se asigna en Recepción vía Check-in."
        )

    # Validación de la Matriz de Transiciones
    estados_validos = TRANSICIONES_PERMITIDAS.get(estado_actual, [])
    if nuevo_estado not in estados_validos:
        estados_validos_str = ", ".join(e.value for e in estados_validos) or "Ninguno"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición de estado inválida: no se permite cambiar de '{estado_actual.value}' a '{nuevo_estado.value}'. Estados permitidos: [{estados_validos_str}]."
        )

    habitacion_actualizada = crud_habitaciones.actualizar_estado_habitacion(db, id_habitacion, estado_update)
    return habitacion_actualizada

@router.put("/{id_habitacion}", response_model=schemas.HabitacionRespuesta)
def modificar_habitacion(
    id_habitacion: int,
    datos: schemas.HabitacionActualizar,
    db: Session = Depends(get_db),
    usuario_actual = Depends(exigir_rol_admin)
):
    habitacion_existente = crud_habitaciones.obtener_habitacion(db, id_habitacion)
    if not habitacion_existente:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    if datos.numero_habitacion and datos.numero_habitacion != habitacion_existente.numero_habitacion:
        ocupada = crud_habitaciones.obtener_habitacion_por_numero(db, numero=datos.numero_habitacion)
        if ocupada:
            raise HTTPException(status_code=400, detail="El número de habitación ya existe")

    return crud_habitaciones.actualizar_habitacion(db, id_habitacion=id_habitacion, datos=datos)
