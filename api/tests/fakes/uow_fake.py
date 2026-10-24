from app.domain.uow import AbstractUnitOfWork

class FakeUnitOfWork(AbstractUnitOfWork):
    """
    Implementação falsa (Fake) do Unit of Work para testes unitários.
    Registra em memória se o commit ou rollback foi acionado.
    """
    def __init__(self):
        self.commited = False
        self.rollbacked = False

    def commit(self):
        self.commited = True

    def rollback(self):
        self.rollbacked = True
