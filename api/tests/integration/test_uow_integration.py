from uuid import uuid4

import pytest
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

from app.infrastructure.uow import SqlAlchemyUnitOfWork


Base = declarative_base()


class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)


URL_DO_BANCO = "postgresql+psycopg://usuario_teste:senha_secreta@localhost:5433/uow_db"


@pytest.fixture
def session_factory():
    engine = create_engine(URL_DO_BANCO, connect_args={"connect_timeout": 5})
    schema = f"test_uow_{uuid4().hex}"
    try:
        with engine.begin() as connection:
            connection.execute(CreateSchema(schema))
        try:
            isolated_engine = engine.execution_options(schema_translate_map={None: schema})
            Base.metadata.create_all(isolated_engine)
            yield sessionmaker(bind=isolated_engine)
        finally:
            with engine.begin() as connection:
                connection.execute(DropSchema(schema, cascade=True))
    finally:
        engine.dispose()


def nomes_persistidos(session_factory):
    # Outra sessão confirma o estado persistido, fora da transação do caso de uso.
    with session_factory() as session:
        return session.scalars(select(Empresa.nome).order_by(Empresa.id)).all()


def test_commit_persiste_todas_as_gravacoes(session_factory):
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        uow.session.add(Empresa(nome="Primeira empresa"))
        uow.session.flush()
        uow.session.add(Empresa(nome="Segunda empresa"))
        uow.commit()

    assert nomes_persistidos(session_factory) == ["Primeira empresa", "Segunda empresa"]


def test_erro_desfaz_gravacoes_ja_enviadas_ao_banco(session_factory):
    with pytest.raises(RuntimeError, match="Falha no caso de uso"):
        with SqlAlchemyUnitOfWork(session_factory) as uow:
            uow.session.add(Empresa(nome="Primeira empresa"))
            uow.session.flush()
            uow.session.add(Empresa(nome="Segunda empresa"))
            uow.session.flush()
            raise RuntimeError("Falha no caso de uso")

    assert nomes_persistidos(session_factory) == []


def test_erro_de_integridade_desfaz_gravacao_anterior(session_factory):
    with pytest.raises(IntegrityError):
        with SqlAlchemyUnitOfWork(session_factory) as uow:
            uow.session.add(Empresa(nome="Empresa válida"))
            uow.session.flush()
            uow.session.add(Empresa(nome=None))
            uow.commit()

    assert nomes_persistidos(session_factory) == []


def test_saida_sem_commit_nao_persiste_gravacoes(session_factory):
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        uow.session.add(Empresa(nome="Empresa não confirmada"))
        uow.session.flush()

    assert nomes_persistidos(session_factory) == []
