from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from sqlmodel import Session
from backend.crud.users import get_user_by_email, create_user
from backend.crud.database import get_session
from backend.schemas.users import UserCreate, UserRead
from backend.utils.email import send_email_async


router = APIRouter(prefix="/api")


@router.post(
    "/register",
    response_model=UserRead,
)
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

    # save user in database
    user = create_user(session, email=user_in.email, password=user_in.password)

    # send email
    subject = "Welcome, FlyingBee!"
    recipients = [user_in.email]
    body = f"Hello {user_in.email},\n\nThank you for registering."
    background_tasks.add_task(send_email_async, subject, recipients, body)

    # user = UserRead(id=1, email=user_in.email)
    return user
