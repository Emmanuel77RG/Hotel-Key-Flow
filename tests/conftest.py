import pytest
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.database import Base
from app.api.dependencias import get_db
from app.main import app
from app.models.usuarios import Rol, Usuario
from app.core import security

# Motor de BD de prueba aislado en memoria (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def preparar_db_base():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session():
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Sembrar roles base para tests
    for r_id, r_nom in [(1, "Administrador"), (2, "Recepción"), (3, "Limpieza")]:
        if not session.query(Rol).filter(Rol.id_rol == r_id).first():
            session.add(Rol(id_rol=r_id, nombre_rol=r_nom, descripcion=f"Rol {r_nom}"))
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def usuarios_prueba(db_session):
    """Crea y retorna usuarios con roles 1 (Admin), 2 (Recepción) y 3 (Limpieza)."""
    pw_hash = security.get_password_hash("Password123*")
    
    admin = db_session.query(Usuario).filter(Usuario.email == "admin@keyflow.test").first()
    if not admin:
        admin = Usuario(nombre="Admin Test", email="admin@keyflow.test", password_hash=pw_hash, id_rol=1, estado_activo=True)
        db_session.add(admin)

    recep = db_session.query(Usuario).filter(Usuario.email == "recepcion@keyflow.test").first()
    if not recep:
        recep = Usuario(nombre="Recep Test", email="recepcion@keyflow.test", password_hash=pw_hash, id_rol=2, estado_activo=True)
        db_session.add(recep)

    limp = db_session.query(Usuario).filter(Usuario.email == "limpieza@keyflow.test").first()
    if not limp:
        limp = Usuario(nombre="Limp Test", email="limpieza@keyflow.test", password_hash=pw_hash, id_rol=3, estado_activo=True)
        db_session.add(limp)

    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(recep)
    db_session.refresh(limp)

    return {"admin": admin, "recepcion": recep, "limpieza": limp}


@pytest.fixture
def headers_admin(usuarios_prueba):
    token = security.create_access_token(
        data={"sub": usuarios_prueba["admin"].email, "id_rol": 1},
        expires_delta=timedelta(minutes=60),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def headers_recepcion(usuarios_prueba):
    token = security.create_access_token(
        data={"sub": usuarios_prueba["recepcion"].email, "id_rol": 2},
        expires_delta=timedelta(minutes=60),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def headers_limpieza(usuarios_prueba):
    token = security.create_access_token(
        data={"sub": usuarios_prueba["limpieza"].email, "id_rol": 3},
        expires_delta=timedelta(minutes=60),
    )
    return {"Authorization": f"Bearer {token}"}
