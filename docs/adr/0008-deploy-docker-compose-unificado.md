# 0008. Deploy unificado via Docker Compose

Data: 2026-08-07

## Status

Aceita

## Contexto

Web (Next.js), API (FastAPI) e Postgres precisam ser implantados em algum lugar. Era preciso decidir entre uma infra unificada ou serviços com deploy e escala independentes.

## Decisão

Todos os serviços sobem na mesma infraestrutura via Docker Compose, em um único host:

| Serviço | Conteúdo |
|---|---|
| `web` | Next.js em modo SPA ([ADR-0002](./0002-frontend-nextjs-spa.md)) |
| `api` | FastAPI — domínio, dados, autenticação e processamento de importações ([ADR-0003](./0003-backend-dominio-fastapi.md), [ADR-0007](./0007-processamento-assincrono-backgroundtasks.md)) |
| `db` | PostgreSQL ([ADR-0004](./0004-banco-dados-postgresql.md)) |
| `backup` | `pg_dump` diário enviado para fora do host ([ADR-0016](./0016-backup-pgdump-onedrive.md)) |
| `proxy` | Proxy reverso servindo `web` e `api` sob o mesmo domínio |

O proxy não é enfeite: é ele que faz o cookie de sessão e as chamadas do navegador à API ficarem same-origin, evitando configuração de CORS com credenciais e `SameSite=None` (ver [ADR-0006](./0006-autenticacao-jwt-fastapi.md)).

## Alternativas consideradas

- **Serviços separados** com deploy e escala independentes por camada (ex: Vercel para o Next, container service para a API, banco gerenciado): mais resiliente e escalável, mas mais complexidade operacional e custo — prematuro antes de validar o produto com um cliente real.

## Consequências

Mais simples e barato de operar para um piloto. Um `docker compose up` sobe o ambiente inteiro, o que também é o caminho de onboarding do time.

São três serviços de aplicação mais o proxy — menos do que o desenho inicial, que previa também um worker e um Redis (ver [ADR-0007](./0007-processamento-assincrono-backgroundtasks.md)). Cada serviço a menos é um a menos para subir, configurar e depurar.

Escala verticalmente até certo ponto, e há menos isolamento entre serviços: um problema de recurso em um deles pode afetar os outros. Revisitar quando houver tração real e necessidade de escalar componentes independentemente.

**Ponto ainda não decidido:** política de backup do volume do Postgres. Como o arquivo bruto da importação não é guardado ([ADR-0010](./0010-sem-storage-arquivo-bruto.md)), o banco é a única cópia dos dados do cliente — o backup precisa ser resolvido antes de qualquer dado real entrar no sistema.
