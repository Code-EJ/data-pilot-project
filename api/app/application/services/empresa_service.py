from app.domain.uow import AbstractUnitOfWork

def criar_empresa_e_membro(uow: AbstractUnitOfWork, simular_falha=False):
    """
    Função da camada de serviço para criação de Empresa e Membro.
    Demonstra os limites de transação e isolamento utilizando o padrão Unit of Work.
    """
    with uow:
        if simular_falha:
            raise Exception("Erro ao processar as entidades.")

        uow.commit()
