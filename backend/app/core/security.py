from fastapi import HTTPException, status
import bcrypt
from jose import jwt
from jose.exceptions import JWTError
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from app.core.config import settings

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para la contraseña proporcionada
    """

    # Genera una sal aleatoria
    salt = bcrypt.gensalt()
    # Crea el hash de la contraseña utilizando la sal
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    #Devuelve el hash como cadena de texto
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con el hash almacenado
    """
    #Compara la contraseña proporcionada con el hash almacenado
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    issued_at = datetime.now(timezone.utc)
    expire = issued_at + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": issued_at,
        "jti": str(uuid4()),
        "type": "access"
        })
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    issued_at = datetime.now(timezone.utc)
    expire = issued_at + expires_delta

    to_encode.update({
        "exp": expire,
        "iat": issued_at,
        "jti": str(uuid4()),
        "type": "refresh"
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
