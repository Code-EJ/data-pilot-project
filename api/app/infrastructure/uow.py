from sqlalchemy.orm import Session
from app.domain.uow import AbstractUnitOfWork

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    Implementação do Unit of Work baseada no SQLAlchemy.
    """
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
