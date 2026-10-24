import abc

class AbstractUnitOfWork(abc.ABC):
    """
    Classe base abstrata para o padrão Unit of Work.
    Gerencia os limites de transação para os casos de uso.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()

    @abc.abstractmethod
    def commit(self):
        """Confirma a transação atual."""
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        """Desfaz a transação atual em caso de falha."""
        raise NotImplementedError
