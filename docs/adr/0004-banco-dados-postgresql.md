# 0004. PostgreSQL como banco de dados, acessado só pela FastAPI

Data: 2026-08-07

## Status

Aceita

## Contexto

Precisamos de um banco relacional que suporte bem dados estruturados (tabelas de negócio) e metadados semi-estruturados (log e metadados de importação), sem custo de licenciamento. Era preciso decidir também **quem** pode se conectar a ele.

## Decisão

Usar PostgreSQL, com SQLAlchemy como ORM e Alembic para migrations.

**A FastAPI é o único componente com acesso ao banco.** O `/web` não tem string de conexão, credencial nem ORM — todo dado passa pela API por HTTP (ver [ADR-0002](./0002-frontend-nextjs-spa.md), [ADR-0005](./0005-comunicacao-rest-openapi.md)).

Essa exclusividade se refere ao PostgreSQL da plataforma. Quando uma integração precisar ler um banco externo do cliente, a FastAPI será o consumidor dessa fonte e usará uma credencial somente-leitura, separada das credenciais do banco interno.

## Alternativas consideradas

- **SQL Server**: descartado — não há licenciamento corporativo já existente nem exigência de integração com o ecossistema Microsoft. PostgreSQL tem melhor suporte no ecossistema Python/Node, sem custo de licença.
- **Prisma no `/web`, para acesso direto a dados leves**: era o desenho inicial. Descartada — dois ORMs sobre o mesmo schema significam duas fontes de verdade sobre a estrutura das tabelas, duas ferramentas de migration que podem divergir, e um segundo caminho pelo qual regra de negócio vaza para o front-end. O ganho (evitar um salto HTTP em leituras simples) não paga esse custo, ainda mais com um time em formação.

## Consequências

Suporte nativo a JSON cobre a necessidade de metadados de importação sem precisar de um segundo banco. Uma única ferramenta de migration (Alembic) e um único mapeamento objeto-relacional para aprender e manter.

Ver [ADR-0012](./0012-dimensionamento-postgresql-piloto.md) para o dimensionamento inicial esperado e [data-model.md](../architecture/data-model.md) para o schema.
