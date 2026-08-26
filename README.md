# Plataforma de Análise de Dados

Plataforma que unifica ingestão/centralização de dados (substituição de planilhas e sistemas desconexos) e dashboards gerenciais de KPIs, em um fluxo único: **Ingestão → Validação → Armazenamento → Dashboards**.

Cada usuário tem uma conta própria e pode estar vinculado a várias **empresas**, com um perfil de acesso diferente em cada uma. Todo dado do sistema pertence a uma empresa.

## Estrutura do repositório

```
/web        → Next.js em modo SPA (TypeScript)
/api        → FastAPI — domínio, dados, autenticação, ingestão (Python)
/docs       → documentação de arquitetura, produto e protótipo
```

`/web` e `/api` são independentes entre si (linguagens diferentes, sem build compartilhado) e se comunicam só via HTTP REST. Ver [ADR-0013](./docs/adr/0013-repo-unico-sem-monorepo.md).

## Documentação

- [docs/architecture/overview.md](./docs/architecture/overview.md) — visão geral da arquitetura, stack e o caminho que o dado percorre
- [docs/architecture/data-model.md](./docs/architecture/data-model.md) — schema do banco ([diagrama](./docs/architecture/data-model.svg))
- [docs/adr](./docs/adr/README.md) — decisões arquiteturais, uma por arquivo, com contexto e alternativas descartadas
- [docs/product-scope.md](./docs/product-scope.md) — funcionalidades por módulo
- [docs/api-contract.md](./docs/api-contract.md) — estimativa dos endpoints e convenções da API (formato de erro, paginação, autorização)
- [docs/prototype/index.html](./docs/prototype/index.html) — protótipo visual navegável de todas as telas (abra no navegador; dados fictícios)
- [docs/import-spec.md](./docs/import-spec.md) — regras de leitura, conversão e validação de planilha
- [docs/metrics.md](./docs/metrics.md) — fórmula de cada número do Painel
- [docs/backlog.md](./docs/backlog.md) — 87 cards prontos para virar sprint, com dependências e tamanhos
- [docs/definition-of-done.md](./docs/definition-of-done.md) — o que significa um card estar pronto

**Entrando no projeto agora?** Abra o protótipo para entender o produto, leia o [overview](./docs/architecture/overview.md) e o [data-model](./docs/architecture/data-model.md), e então os ADRs [0001](./docs/adr/0001-unificacao-modulos-ingestao-dashboards.md), [0003](./docs/adr/0003-backend-dominio-fastapi.md), [0014](./docs/adr/0014-escopo-por-empresa-organizations.md) e [0002](./docs/adr/0002-frontend-nextjs-spa.md). O resto dos ADRs é consulta.

## Como rodar

_A definir — projeto ainda em fase de setup inicial (código-fonte de `/web` e `/api` ainda não escrito)._

O objetivo é que `docker compose up` suba o ambiente completo (`web`, `api`, `db`, `backup` e proxy), sem passo manual além de copiar o `.env.example` e rodar o seed. Ver [ADR-0008](./docs/adr/0008-deploy-docker-compose-unificado.md) e [ADR-0015](./docs/adr/0015-uma-instancia-por-cliente.md).

## Contribuindo

Ver [CONTRIBUTING.md](./CONTRIBUTING.md).
