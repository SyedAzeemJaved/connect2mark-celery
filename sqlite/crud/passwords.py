from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.crud.users import get_user_by_email

from utils.password import verify_password


async def authenticate_user(email: str, password: str, db: AsyncSession):
    """Authenticate a user, check if their password is correct"""
    user = await get_user_by_email(user_email=email, db=db)

    if not user:
        return False

    if not verify_password(
        plain_password=password, hashed_password=user.password
    ):
        return False

    return user
