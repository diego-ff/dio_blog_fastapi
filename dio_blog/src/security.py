import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

# Configurações básicas
SECRET = "my-secret"
ALGORITHM = "HS256"


# MODELOS -------------------------------------------------------------

class AccessToken(BaseModel):
    iss: str
    sub: int
    exp: float
    iat: float
    nbf: float
    jti: str | None = None


class JWTToken(BaseModel):
    access_token: AccessToken


# GERAÇÃO -------------------------------------------------------------

def sign_jwt(user_id: int) -> dict[str, str]:
    now = time.time()
    payload = {
        "iss": "curso-fastapi.com.br",
        "sub": str(user_id),  # ✅ converter para string
        "exp": now + (60 * 30),  # expira em 30 minutos
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return {"access_token": token}


# DECODIFICAÇÃO -------------------------------------------------------------

async def decode_jwt(token: str) -> JWTToken | None:
    try:
        decoded = jwt.decode(
            token,
            SECRET,
            algorithms=[ALGORITHM],
            options={"verify_aud": False},  # ignora audience
        )

        # cria o modelo Pydantic
        token_obj = JWTToken.model_validate({"access_token": decoded})

        # verifica expiração manualmente
        if token_obj.access_token.exp < time.time():
            print("⚠️ Token expirado.")
            return None

        return token_obj

    except jwt.ExpiredSignatureError:
        print("⚠️ Token expirado.")
        return None
    except jwt.InvalidTokenError as e:
        print(f"⚠️ Token inválido: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Erro inesperado: {e}")
        return None


# MIDDLEWARE -------------------------------------------------------------

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing.",
            )

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme.",
            )

        payload = await decode_jwt(credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            )

        return payload


# DEPENDÊNCIAS -------------------------------------------------------------

async def get_current_user(
    token: Annotated[JWTToken, Depends(JWTBearer())]
) -> dict[str, int]:
    return {"user_id": token.access_token.sub}


def login_required(
    current_user: Annotated[dict[str, int], Depends(get_current_user)]
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
        )
    return current_user
