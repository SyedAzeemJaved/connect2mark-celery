from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlite.dependency import get_db_session
from sqlalchemy.orm import Session

from typing import Annotated
from jose import JWTError, jwt

from secret import secret

from sqlite.models import UserModel

import sqlite.crud.users as users
from sqlite.schemas import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, secret.SECRET_KEY, algorithms=[secret.ALGORITHM]
        )
        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await users.get_user_by_email(user_email=token_data.email, db=db)

    if user is None:
        raise credentials_exception

    return user


async def should_be_admin_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    if current_user.is_admin:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have the necessary permission to access this route",
    )


async def should_be_academic_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    if not current_user.is_admin:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="This route is for academic users only",
    )
