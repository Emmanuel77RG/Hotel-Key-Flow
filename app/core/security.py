import re
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def crear_token_acceso(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Alias en inglés para compatibilidad estándar
create_access_token = crear_token_acceso


def enmascarar_token_pago(metodo_pago: str | None) -> str:
    """
    Enmascara el token de transacción/autorización para roles no administrativos (RNF-SEG-003).
    Preserva solo los últimos 4 caracteres del token.
    Ejemplos:
      - 'Tarjeta Chip ****7390 (Tok: 8A7B2C1D)' -> 'Tarjeta Chip ****7390 (Tok: ****2C1D)'
      - 'Tarjeta NFC ****4821 (Tok: 9B8C7D6E)'  -> 'Tarjeta NFC ****4821 (Tok: ****7D6E)'
      - 'Tarjeta (Token: tok_12345678)'         -> 'Tarjeta (Token: tok_****5678)'
      - 'Efectivo'                              -> 'Efectivo'
    """
    if not metodo_pago:
        return metodo_pago or ""

    def _repl_paren(match):
        pref = match.group(1)
        tok = match.group(2).strip()
        if len(tok) > 4:
            masked = "****" + tok[-4:]
        else:
            masked = "****"
        return f"({pref}{masked})"

    # Enmascara cualquier patrón (Tok: ...) o (Token: ...)
    resultado = re.sub(r"\((Tok(?:en)?:\s*)([^\)]+)\)", _repl_paren, metodo_pago, flags=re.IGNORECASE)
    return resultado

