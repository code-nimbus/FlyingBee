from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Annotated

# from models.users import UserInDB
from backend.schemas.users import UserCreate, UserRead
from backend.crud.users import get_user_by_email, create_user
from backend.crud.database import Session
from backend.crud.database import get_session
from backend.utils.email import send_email_async
from backend.models.auth import Token
from fastapi.security import OAuth2PasswordRequestForm
from backend.utils.security import authenticate_user, create_access_token
import os
from datetime import timedelta

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


@router.post("/register", response_model=UserRead)
async def register(
    background_tasks: BackgroundTasks,
    user_in: UserCreate,
    session: Session = Depends(get_session),
):
    # verify that the user does not already exist
    user = get_user_by_email(session, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # save user in the database
    user = create_user(session, email=user_in.email, password=user_in.password)

    # send email

    subject = "Welcome, Flying Bee!"
    recipients = [user_in.email]
    body_text = f"Hello {user_in.email},\n\nThank you for registering."
    background_tasks.add_task(send_email_async, subject, recipients, body_text)

    return user


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
