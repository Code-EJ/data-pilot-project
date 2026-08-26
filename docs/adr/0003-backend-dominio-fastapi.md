# 0003. Backend de domínio em FastAPI

Data: 2026-08-07

## Status

Aceita

## Contexto

O módulo de ingestão precisa de parsing de planilhas, ETL, validação de dados e um gateway de integração — tarefas de engenharia de dados onde o ecossistema Python (Pandas) é significativamente mais maduro que o do Node.

## Decisão

Usar FastAPI (Python) como backend de domínio, e como **único** dono de tudo que não é interface:

- Regras de negócio dos módulos de ingestão e dashboards
- Ingestão, ETL, validação (Pydantic) e gateway de integração
- Acesso ao banco (ver [ADR-0004](./0004-banco-dados-postgresql.md)) — nenhum outro serviço se conecta ao Postgres
- Autenticação, sessão e autorização (ver [ADR-0006](./0006-autenticacao-jwt-fastapi.md), [ADR-0009](./0009-rbac-dois-perfis.md))
- Processamento assíncrono das importações (ver [ADR-0007](./0007-processamento-assincrono-backgroundtasks.md))

## Alternativas consideradas

- **Full TypeScript (Node no backend, ex: NestJS ou Express)**: descartada — rodar tudo em Node exigiria contornos para parsing e ETL de planilhas, ou um processo Python isolado de qualquer forma, então não eliminaria o Python da stack. Melhor assumir o Python onde ele é forte.

## Consequências

Ganha o ecossistema Python maduro para dados (Pandas). Custa manter dois runtimes (Node para o front, Python para o domínio) e uma fronteira HTTP explícita entre eles ([ADR-0005](./0005-comunicacao-rest-openapi.md)).

Concentrar domínio, dados e autenticação em um só serviço é deliberado: reduz a decisão de "onde isso mora?" a uma única pergunta — é regra de negócio ou é tela? Esse critério importa mais do que o normal para um time em formação. O risco natural do arranjo é a API crescer sem estrutura interna; organizá-la por módulo de domínio desde o começo é o contrapeso.
