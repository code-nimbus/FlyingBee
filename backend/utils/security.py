from datetime import datetime, timedelta, timezone
import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session, select

from backend.models.users import UserInDB
from backend.crud.database import get_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")


# ---------------------------------------------------------
# PASSWORD
# ---------------------------------------------------------


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ---------------------------------------------------------
# JWT
# ---------------------------------------------------------


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not configured")

    data_to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    data_to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        data_to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


# ---------------------------------------------------------
# USER AUTHENTICATION
# ---------------------------------------------------------


def authenticate_user(
    session: Session,
    email: str,
    password: str,
):
    user = session.exec(select(UserInDB).where(UserInDB.email == email)).first()

    if not user:
        return False

    if not verify_password(
        password,
        user.password,
    ):
        return False

    return user


# ---------------------------------------------------------
# GET CURRENT USER
# ---------------------------------------------------------


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not configured")

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        email: str | None = payload.get("sub")

        if email is None:
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = session.exec(select(UserInDB).where(UserInDB.email == email)).first()

    if user is None:
        raise credentials_exception

    return user
