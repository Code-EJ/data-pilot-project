# Documentação Técnica: Padrão Unit of Work (UoW)

## 1. Visão Geral
Esta documentação descreve a implementação do padrão **Unit of Work (UoW)** no `data-pilot-project`. 
O objetivo principal do UoW é definir um limite transacional por caso de uso. Ele garante a atomicidade das operações no banco de dados, permitindo que todas as mudanças sejam confirmadas (`commit`) em conjunto ou, em caso de erro, desfeitas integralmente (`rollback`), mantendo a consistência dos dados.

**Issue Relacionada:** #3

## 2. Estrutura e Arquitetura (DDD)
A implementação respeita rigorosamente os princípios de Clean Architecture e Domain-Driven Design, separando o contrato da implementação de infraestrutura.

- **`api/app/domain/uow.py`**: Contém a `AbstractUnitOfWork`. É uma classe puramente abstrata (Python nativo), sem nenhuma dependência de bibliotecas externas (como SQLAlchemy). Define o contrato que a camada de Aplicação deve consumir.
- **`api/app/infrastructure/uow.py`**: Contém a `SqlAlchemyUnitOfWork`. É a implementação concreta que gerencia o ciclo de vida do `sqlalchemy.orm.Session`.
- **`api/tests/fakes/uow_fake.py`**: Utilitário para mockar o UoW em testes unitários rápidos, gravando as chamadas de commit/rollback em memória.

## 3. Como Funciona (Context Manager)
O UoW foi construído utilizando o protocolo de *Context Manager* do Python (`__enter__` e `__exit__`).

1. Quando o bloco `with` é aberto, uma sessão de banco de dados é instanciada e injetada nos Repositórios (que compartilharão esta mesma sessão).
2. Se o fluxo ocorrer perfeitamente, a camada de serviço chama o `.commit()` no final.
3. Se qualquer **Exceção** for levantada durante a execução, o método `__exit__` intercepta o erro e dispara o `.rollback()` automaticamente, impedindo gravações parciais no banco.

## 4. Exemplo de Uso na Camada de Aplicação
A camada de aplicação não deve conhecer o SQLAlchemy, ela apenas recebe a abstração do UoW injetada.

```python
from app.domain.uow import AbstractUnitOfWork

def processar_transacao_complexa(uow: AbstractUnitOfWork):
    with uow:
        # Repositórios compartilham a mesma sessão do UoW
        uow.empresas.add(Empresa(...))
        uow.membros.add(Membro(...))
        
        # O commit é explícito no caso de sucesso
        uow.commit()
```
## 5. Assistência de Inteligência Artificial (AI-Assisted Development)
Durante o desenvolvimento desta task, ferramentas de IA foram utilizadas pontualmente como suporte técnico e *pair programming*. O entendimento do problema, a estruturação da lógica de negócio e as definições do fluxo da aplicação foram desenvolvidos manualmente. A inteligência artificial foi empregada para auxiliar exclusivamente nas partes mais complexas da implementação, como o refinamento do padrão DDD (Domain-Driven Design) para isolamento do SQLAlchemy, a configuração do boilerplate dos testes de integração com o banco efêmero e a formatação estrutural da documentação, garantindo agilidade e alinhamento com as melhores práticas de mercado.