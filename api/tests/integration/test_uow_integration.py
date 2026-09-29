import pytest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

from app.infrastructure.uow import SqlAlchemyUnitOfWork

Base = declarative_base()

class Empresa(Base):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String)

URL_DO_BANCO = "postgresql://usuario_teste:senha_secreta@localhost:5432/uow_db"
engine = create_engine(URL_DO_BANCO)
SessionFactory = sessionmaker(bind=engine)

def service_real_com_banco(uow, forcar_erro=False):
    """
    Serviço simulado para validar o comportamento do UoW com uma sessão de banco de dados real.
    """
    with uow:
        nova_empresa = Empresa(nome="Empresa de Teste Ltda")
        uow.session.add(nova_empresa)
        
        if forcar_erro:
            raise Exception("Erro ao gravar o membro!")

        uow.commit()


def test_garante_atomicidade_no_banco_de_dados():
    """
    Teste de integração utilizando PostgreSQL para verificar se o Unit of Work do SQLAlchemy
    desfaz as alterações (rollback) no banco caso ocorra uma exceção no bloco da transação.
    """
    Base.metadata.create_all(engine)
    
    uow_real = SqlAlchemyUnitOfWork(SessionFactory)
    
    with pytest.raises(Exception):
        service_real_com_banco(uow_real, forcar_erro=True)
    
    sessao_verificacao = SessionFactory()
    empresas_salvas = sessao_verificacao.query(Empresa).all()
    sessao_verificacao.close()
    
    assert len(empresas_salvas) == 0
