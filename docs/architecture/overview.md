# Visão geral da arquitetura

## Contexto

Este projeto unifica duas frentes que antes seriam tratadas separadamente:

- **Módulo de Ingestão e Centralização de Dados** (ex-P-02): substituição progressiva de processos baseados em planilhas e sistemas desconexos, com upload, cadastro manual, gateway de integração e histórico de importações.
- **Módulo de Dashboards** (ex-P-01): visualização de KPIs, gráficos, filtros, exportação de relatórios.

O módulo de ingestão alimenta diretamente o de dashboards — por isso são um projeto único ([ADR-0001](../adr/0001-unificacao-modulos-ingestao-dashboards.md)).

A esses dois somou-se um terceiro, que apareceu ao desenhar o protótipo:

- **Módulo de Identidade e Acesso**: conta de usuário, empresas, e permissão por empresa ([ADR-0014](../adr/0014-escopo-por-empresa-organizations.md), [ADR-0009](../adr/0009-rbac-dois-perfis.md)).

Fluxo geral: **Ingestão → Validação → Armazenamento → Dashboards**, tudo dentro do escopo de uma empresa.

Funcionalidades por módulo estão em [product-scope.md](../product-scope.md); a estimativa de endpoints e as convenções da API, em [api-contract.md](../api-contract.md). O protótipo navegável de todas as telas está em [`docs/prototype/index.html`](../prototype/index.html).

## Princípio que orienta as decisões

O time do piloto é formado por estudantes com pouca experiência de mercado. Por isso, **número de fronteiras** (processos, linguagens, pontos de integração) é critério de decisão tão importante quanto capacidade técnica: cada fronteira é um lugar onde o erro aparece em um serviço e a causa está em outro.

Na prática, quatro regras atravessam vários ADRs:

1. **Um dono por responsabilidade.** Regra de negócio, banco e autenticação vivem todos na `/api`.
2. **O front é só front.** O `/web` renderiza e chama a API. Não acessa banco, não decide negócio, e esconder um botão nunca é controle de acesso.
3. **Nada entra na stack sem uso comprovado.** Fila, storage de objetos e cache ficam de fora até haver medição que os justifique.
4. **Todo dado pertence a uma empresa.** Nenhuma consulta de negócio roda sem filtro de `organization_id` e de `deleted_at is null`.

## Estrutura do repositório

Repositório único, sem ferramenta de monorepo ([ADR-0013](../adr/0013-repo-unico-sem-monorepo.md)):

```
/web        → Next.js em modo SPA (TypeScript)
/api        → FastAPI — domínio, dados, autenticação, ingestão (Python)
/docs       → esta documentação (adr/, architecture/, prototype/, product-scope.md)
```

`/web` e `/api` se comunicam só via HTTP REST; o client TypeScript é gerado do schema OpenAPI publicado pela API ([ADR-0005](../adr/0005-comunicacao-rest-openapi.md)).

## Stack

| Camada | Tecnologia | ADR |
|---|---|---|
| Front-end (SPA, sem BFF) | Next.js (TypeScript) | [0002](../adr/0002-frontend-nextjs-spa.md) |
| Backend de domínio | FastAPI (Python) | [0003](../adr/0003-backend-dominio-fastapi.md) |
| Banco de dados | PostgreSQL + SQLAlchemy + Alembic — acesso exclusivo da `/api` | [0004](../adr/0004-banco-dados-postgresql.md), [0012](../adr/0012-dimensionamento-postgresql-piloto.md), [0018](../adr/0018-persistencia-ddd-com-sqlalchemy-e-alembic.md) |
| Comunicação web ↔ api | REST + client TS gerado do OpenAPI | [0005](../adr/0005-comunicacao-rest-openapi.md) |
| Autenticação | JWT emitido e validado pela FastAPI, cookie httpOnly | [0006](../adr/0006-autenticacao-jwt-fastapi.md) |
| Escopo de dados | `organizations` — toda tabela e toda query | [0014](../adr/0014-escopo-por-empresa-organizations.md) |
| RBAC | Admin / Usuário, **por empresa** | [0009](../adr/0009-rbac-dois-perfis.md) |
| Processamento de importações | `BackgroundTasks` do FastAPI (sem fila) | [0007](../adr/0007-processamento-assincrono-backgroundtasks.md) |
| Testes e CI | pytest contra Postgres real; GitHub Actions no PR | [0017](../adr/0017-testes-e-ci.md) |
| Deploy | Docker Compose — `web`, `api`, `db`, `backup` + proxy; uma stack por cliente | [0008](../adr/0008-deploy-docker-compose-unificado.md), [0015](../adr/0015-uma-instancia-por-cliente.md) |
| Backup | `pg_dump` diário → OneDrive via `rclone`, pastas datadas | [0016](../adr/0016-backup-pgdump-onedrive.md) |
| Storage de arquivo bruto | Nenhum (v1) — só dados estruturados persistem | [0010](../adr/0010-sem-storage-arquivo-bruto.md) |
| Gráficos (front) | Recharts | [0011](../adr/0011-biblioteca-graficos-recharts.md) |
| Validação de schema | Zod (TS) / Pydantic (Python) | — |
| Parsing de planilhas | Pandas (`/api`) | [0003](../adr/0003-backend-dominio-fastapi.md) |

Para o raciocínio completo por trás de cada escolha, ver [docs/adr](../adr/README.md).

## Persistência: fronteiras entre API e banco

O PostgreSQL é acessado somente por implementações de repositório na camada de infraestrutura. O caminho de uma operação que persiste ou lê dados é:

```text
controller -> service de aplicação -> contrato de repositório (domínio)
                                      ^
                                      |
             repositório SQLAlchemy (infraestrutura) -> Session -> PostgreSQL
```

O controller recebe HTTP e injeta as dependências. O service executa o caso de uso e depende apenas do contrato. A infraestrutura adapta esse contrato para SQLAlchemy 2.x e converte os modelos de persistência em entidades de domínio; portanto, entidades, DTOs e services não importam FastAPI nem SQLAlchemy.

O schema é evoluído somente por migrations Alembic versionadas: cada mudança de tabela, índice, constraint ou coluna acompanha uma migration revisada e o deploy executa `alembic upgrade head`. A API não usa criação automática de tabelas no startup. A decisão detalhada está na [ADR-0018](../adr/0018-persistencia-ddd-com-sqlalchemy-e-alembic.md).

## Como o dado atravessa o sistema

Vale ler antes de pegar a primeira tarefa — é o caminho que toda funcionalidade percorre.

**Entrar no sistema:** login valida a senha e devolve um JWT que contém apenas o id do usuário → `GET /auth/me` lista as empresas em que ele tem vínculo, com o papel em cada uma → a pessoa escolhe a empresa → a partir daí, toda requisição carrega a empresa ativa, e a API confirma o vínculo e resolve o papel a cada chamada ([ADR-0006](../adr/0006-autenticacao-jwt-fastapi.md)).

**Importação de planilha:** o navegador envia o arquivo → a API cria um `import_batch` com status `processing` e responde na hora → em segundo plano, Pandas lê o arquivo, Pydantic valida linha a linha, linhas válidas viram `sales_records` e linhas rejeitadas (erro ou duplicata) viram `import_errors` → o batch fecha com as contagens → a tela, que estava consultando o batch, mostra o resultado. O arquivo é descartado ([ADR-0010](../adr/0010-sem-storage-arquivo-bruto.md)).

**Leitura de dashboard:** o navegador chama um endpoint de agregação → a API valida o JWT, confirma o vínculo com a empresa, aplica o RBAC, roda a consulta agregada filtrando por `organization_id` e devolve JSON pronto para o gráfico → Recharts renderiza. O front não agrega dado nem calcula métrica.

## Modelo de dados

Ver [data-model.md](./data-model.md) — schema relacional completo, com o diagrama em [data-model.svg](./data-model.svg).

## Pontos em aberto

Itens conhecidos que ainda não viraram decisão. Quando um for resolvido, vira ADR e sai daqui.

| Item | Por que importa |
|---|---|
| Persistência do mapeamento de colunas | Hoje o usuário remapeia a cada upload. |
| Row-Level Security | Obrigatória antes de duas empresas de clientes diferentes dividirem a mesma instância ([ADR-0014](../adr/0014-escopo-por-empresa-organizations.md)). |
| Verificação de e-mail no cadastro | Hoje qualquer e-mail cria conta. Tolerável porque uma conta sem vínculo não faz nada, mas não indefinidamente. |
| LGPD | `sales_records.client_name` pode ser pessoa física, e a EJ passa a ser operadora dos dados ([ADR-0016](../adr/0016-backup-pgdump-onedrive.md)). Precisa estar em contrato. |
| Aba da planilha, datas futuras e valores negativos | Escolhas assumidas em [import-spec.md](../import-spec.md); precisam ser confirmadas com o cliente. |
| Janela de comparação dos KPIs | Assumida como período de mesma duração imediatamente anterior ([metrics.md](../metrics.md)); a alternativa é comparar com o ano anterior. |
