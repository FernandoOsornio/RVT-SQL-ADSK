import os
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "change_me")  # ⚠️ cambia esto en producción
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

# ===============================
# 🔐 Crear un JWT (para Revit / API)
# ===============================
def create_jwt(client_id: str, expires_minutes: int = 15):
    """
    Crea un token JWT firmado con el secreto definido en .env.
    """
    now = datetime.utcnow()
    payload = {
        "sub": client_id,
        "iat": int(now.timestamp()),  # Issued at
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp())  # Expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token

# ===============================
# 🧾 Verificar y decodificar un JWT
# ===============================
def verify_jwt(token: str):
    """
    Verifica y decodifica un token JWT.
    Lanza errores si el token no es válido o está expirado.
    """
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return decoded
    except ExpiredSignatureError:
        print("❌ Token expirado.")
        raise ValueError("El token ha expirado.")
    except JWTError:
        print("⚠️ Token inválido.")
        raise ValueError("El token es inválido.")
