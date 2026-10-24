import pytest
from tests.fakes.uow_fake import FakeUnitOfWork
from app.application.services.empresa_service import criar_empresa_e_membro

def test_deve_fazer_commit_quando_tudo_funciona():
    """
    Verifica se o UoW confirma (commit) a transação quando o caso de uso é concluído com sucesso.
    """
    uow_fake = FakeUnitOfWork()
    
    criar_empresa_e_membro(uow_fake, simular_falha=False)
    
    assert uow_fake.commited is True
    assert uow_fake.rollbacked is False

def test_deve_fazer_rollback_quando_ocorre_erro():
    """
    Verifica se o UoW desfaz (rollback) a transação automaticamente caso ocorra uma exceção durante o caso de uso.
    """
    uow_fake = FakeUnitOfWork()
    
    with pytest.raises(Exception):
        criar_empresa_e_membro(uow_fake, simular_falha=True)
    
    assert uow_fake.commited is False
    assert uow_fake.rollbacked is True
