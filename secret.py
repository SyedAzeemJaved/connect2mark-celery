import os

from dotenv import load_dotenv

# Load environment variables into memory
load_dotenv()


class Secret:
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int | str,
        database_url: str,
    ) -> None:
        self.SECRET_KEY = secret_key
        self.ALGORITHM = algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(access_token_expire_minutes)
        self.DATABASE_URL = database_url
        self.SYNC_DATABASE_URL = database_url.replace("+asyncpg", "")


secret = Secret(
    secret_key=os.getenv("SECRET_KEY"),
    algorithm=os.getenv("ALGORITHM"),
    access_token_expire_minutes=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
    database_url=os.getenv("DATABASE_URL"),
)
