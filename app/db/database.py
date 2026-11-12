from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import SQLALCHEMY_DATABASE_URL

# pool_pre_ping=True asegura reconexión automática transparente ante reinicios de PostgreSQL
# pool_recycle=3600 evita que conexiones inactivas caigan por timeout a nivel de socket
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
