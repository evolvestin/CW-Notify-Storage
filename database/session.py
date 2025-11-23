import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functions.SQL import postgresql_port

db_host = os.environ.get('DB_HOST') or '127.0.0.1'

DATABASE_URL = (
    f"postgresql://"
    f"{os.environ['DB_USER']}:{os.environ['DB_PASS']}"
    f"@{db_host}:{postgresql_port}"
    f"/{os.environ['DB_NAME']}"
)


engine = create_engine(DATABASE_URL, echo=False)  # Создаем движок для подключения к базе данных
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Создаем сессию для работы с БД