from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import SECRET_KEY, ALGORITHM
from app.db.database import SessionLocal
from app.crud.crud_usuarios import obtener_usuario_por_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# Función para inyectar la conexión de la BD en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Función para obtener el usuario autenticado mediante JWT
def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email= payload.get("sub")
        if email is None:
            raise credenciales_exception
    except JWTError:
        raise credenciales_exception

    usuario = obtener_usuario_por_email(db, email=email)
    if usuario is None:
        raise credenciales_exception
    if not usuario.estado_activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta del usuario está desactivada",
        )
    return usuario


# Dependencia RBAC: Exige que el usuario autenticado tenga rol de Administrador (id_rol == 1)
def exigir_rol_admin(usuario_actual=Depends(get_usuario_actual)):
    if usuario_actual.id_rol != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requieren permisos de Administrador",
        )
    return usuario_actual


