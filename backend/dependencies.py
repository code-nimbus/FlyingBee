from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from backend.crud.database import get_session
from backend.models.users import UserInDB
from backend.utils.security import (
    ALGORITHM,
    SECRET_KEY,
    authentication_scheme,
)


def get_current_user(
    token: Annotated[str, Depends(authentication_scheme)],
    session: Session = Depends(get_session),
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    user = session.exec(select(UserInDB).where(UserInDB.email == email)).first()

    if user is None:
        raise credentials_exception

    return user
