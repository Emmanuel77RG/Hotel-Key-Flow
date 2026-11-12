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


# Fábrica de dependencias RBAC: Exige roles específicos y devuelve HTTP 403 Forbidden
def requerir_rol(*roles_permitidos: int):
    """
    Fábrica de dependencias RBAC (Role-Based Access Control).
    Exige que el usuario autenticado posea al menos uno de los roles indicados.
    Si el rol del usuario no está autorizado, interrumpe con HTTP 403 FORBIDDEN.
    """
    def _verificador_rol(usuario_actual=Depends(get_usuario_actual)):
        if usuario_actual.id_rol not in roles_permitidos:
            roles_txt = ", ".join(str(r) for r in roles_permitidos)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: permisos insuficientes para esta operación (roles requeridos: [{roles_txt}]).",
            )
        return usuario_actual

    return _verificador_rol


# Accesos directos convenientes para inyección de dependencias
exigir_rol_admin = requerir_rol(1)
exigir_rol_recepcion_o_admin = requerir_rol(1, 2)



