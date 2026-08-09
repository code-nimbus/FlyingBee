from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from typing import Annotated
from sqlmodel import Session
from backend.crud.users import get_user_by_email, create_user
from backend.crud.database import get_session
from backend.schemas.users import UserCreate, UserRead

# from backend.schemas.auth import Token
from backend.utils.email import send_email_async
from backend.models.auth import Token
from fastapi.security import OAuth2PasswordRequestForm
from backend.utils.security import authenticate_user
from backend.utils.security import create_access_token

router = APIRouter(prefix="/api")


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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # save user in database
    user = create_user(session, email=user_in.email, password=user_in.password)

    # send email
    subject = "Welcome, FlyingBee!"
    recipients = [user_in.email]
    body = f"Hello {user_in.email},\n\nThank you for registering."
    background_tasks.add_task(send_email_async, subject, recipients, body)

    # user = UserRead(id=1, email=user_in.email)
    return user


@router.post("/token")
async def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    session: Session = Depends(get_session),
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email already registered",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
    )
    return Token(access_token=access_token, token_type="bearer")


# def authenticate_user(session: Session, email: str, password: str):
#     user = get_user_by_email(session, email)
#     if not user:
#         return False
#     if not verify_password(password, user.password):
#         return False
#     return user
