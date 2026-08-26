# 0018. Persistência DDD com SQLAlchemy 2.x e Alembic

Data: 2026-08-21

## Status

Aceita

## Contexto

A API foi organizada em camadas de controlador, aplicação, domínio e infraestrutura. Precisamos definir como o PostgreSQL se relaciona com essas camadas sem fazer o domínio depender de FastAPI, SQLAlchemy ou do formato físico das tabelas.

A [ADR-0004](./0004-banco-dados-postgresql.md) já definiu PostgreSQL, SQLAlchemy e Alembic como stack de persistência. Esta decisão detalha o encaixe dessa stack na arquitetura DDD.

## Decisão

Usar **SQLAlchemy 2.x** para acesso ao PostgreSQL e **Alembic** para versionar o schema.

- SQLAlchemy fica exclusivamente em `infrastructure`: engine, sessão, modelos de persistência, mapeamentos e implementações dos repositórios.
- Cada repositório de domínio é um contrato. O serviço de aplicação depende desse contrato, não de `Session`, de classes mapeadas ou de consultas SQLAlchemy.
- As entidades do domínio não são modelos SQLAlchemy. O repositório converte entre entidade e modelo de persistência quando necessário.
- A sessão é criada por requisição via dependência da API e é encerrada ao fim dela. O limite de transação é definido pelo caso de uso, não pelo controller.
- As migrations Alembic são arquivos versionados e revisados em pull request. O deploy executa `alembic upgrade head`; a API não cria nem altera tabelas ao iniciar.
- A primeira implementação usará a API síncrona do SQLAlchemy 2.x com PostgreSQL. Adoção de driver e sessão assíncronos só será considerada após medição de carga ou necessidade de I/O concorrente.

## Alternativas consideradas

- **SQLAlchemy direto nos controllers ou services**: descartada. Acopla casos de uso ao banco, dificulta testes unitários e viola a inversão de dependência definida pela arquitetura DDD.
- **Modelos SQLAlchemy como entidades de domínio**: descartada. O domínio passa a carregar detalhes de coluna, relacionamento e ciclo de vida da sessão.
- **SQLModel**: descartada. É útil para projetos menores, mas mistura convenientemente modelos de validação e persistência; aqui a separação explícita entre DTO, entidade e modelo de banco é mais importante.
- **SQLAlchemy assíncrono desde o início**: descartada por ora. A complexidade adicional não se justifica no piloto; a migração é localizada na infraestrutura se vier a ser necessária.

## Consequências

Há uma camada extra de mapeamento entre domínio e banco, mas as regras de negócio permanecem testáveis sem PostgreSQL ou SQLAlchemy. Os testes de repositório e migrations usam PostgreSQL real, conforme a ADR-0017.

Toda mudança de schema terá uma migration Alembic correspondente, e `alembic upgrade head` será pré-requisito do deploy. O `organization_id` e os índices e constraints definidos no modelo de dados continuam sendo responsabilidade do schema, além dos filtros obrigatórios dos repositórios.
