# Architecture Decision Records (ADR)

Este diretório registra as decisões arquiteturais do projeto, uma por arquivo, no formato MADR simplificado.

## Por que ADRs

Decisões de arquitetura tomadas em conversa ou em um doc único tendem a perder o "porquê" com o tempo. Um ADR captura contexto, alternativas consideradas e consequências — assim, decisões futuras podem reavaliar uma escolha antiga sem precisar reconstruir o raciocínio do zero.

## Por onde começar

Quem está entrando no projeto não precisa ler os dezessete. Leia, nesta ordem: [0001](./0001-unificacao-modulos-ingestao-dashboards.md) (por que é um projeto só), [0003](./0003-backend-dominio-fastapi.md) (onde mora a regra de negócio), [0014](./0014-escopo-por-empresa-organizations.md) (por que toda query filtra por empresa) e [0002](./0002-frontend-nextjs-spa.md) (o que o front pode e não pode fazer). O restante é consulta, quando você for mexer naquela parte.

## Convenção

- Um arquivo por decisão: `000X-titulo-curto-em-kebab-case.md`
- Numeração sequencial, nunca reaproveitada
- Use o [`template.md`](./template.md) como ponto de partida

## Status possíveis

- **Proposta** — em discussão, ainda não decidida
- **Aceita** — decisão em vigor
- **Superada por ADR-000Y** — não vale mais; o ADR novo explica o motivo da mudança

Quando uma decisão muda, **não edite o ADR antigo para refletir a nova escolha** — crie um novo ADR e marque o antigo como superado, linkando um para o outro. Isso preserva o histórico de por que a decisão original fazia sentido no momento em que foi tomada.

> Os ADRs 0001–0013 foram revisados uma vez, ainda na fase de desenho e antes de existir código, para simplificar a arquitetura ao tamanho do time. A partir de 0014 a regra acima vale integralmente: os ADRs 0006 e 0009 trazem, no cabeçalho, a data da revisão que os ajustou ao escopo por empresa, e mudanças futuras devem virar ADRs novos.

## Índice

| ADR | Título | Status |
|---|---|---|
| [0001](./0001-unificacao-modulos-ingestao-dashboards.md) | Unificação dos módulos de Ingestão e Dashboards em um projeto único | Aceita |
| [0002](./0002-frontend-nextjs-spa.md) | Front-end em Next.js, usado como SPA (sem camada BFF) | Aceita |
| [0003](./0003-backend-dominio-fastapi.md) | Backend de domínio em FastAPI | Aceita |
| [0004](./0004-banco-dados-postgresql.md) | PostgreSQL como banco de dados, acessado só pela FastAPI | Aceita |
| [0005](./0005-comunicacao-rest-openapi.md) | Comunicação `/web` ↔ `/api` via REST + client gerado do OpenAPI | Aceita |
| [0006](./0006-autenticacao-jwt-fastapi.md) | Autenticação e sessão inteiramente na FastAPI | Aceita |
| [0007](./0007-processamento-assincrono-backgroundtasks.md) | Processamento assíncrono de importações via BackgroundTasks | Aceita |
| [0008](./0008-deploy-docker-compose-unificado.md) | Deploy unificado via Docker Compose | Aceita |
| [0009](./0009-rbac-dois-perfis.md) | RBAC com dois perfis, definidos por empresa | Aceita |
| [0010](./0010-sem-storage-arquivo-bruto.md) | Sem storage de arquivo bruto na ingestão (v1) | Aceita |
| [0011](./0011-biblioteca-graficos-recharts.md) | Biblioteca de gráficos: Recharts | Aceita |
| [0012](./0012-dimensionamento-postgresql-piloto.md) | Dimensionamento inicial do PostgreSQL para o piloto | Aceita |
| [0013](./0013-repo-unico-sem-monorepo.md) | Repositório único com pastas independentes, sem ferramenta de monorepo | Aceita |
| [0014](./0014-escopo-por-empresa-organizations.md) | Escopo por empresa: `organizations` como camada de isolamento | Aceita |
| [0015](./0015-uma-instancia-por-cliente.md) | Uma instância por cliente (por ora), com schema preparado para compartilhar | Aceita |
| [0016](./0016-backup-pgdump-onedrive.md) | Backup: `pg_dump` diário enviado ao OneDrive em pastas datadas | Aceita |
| [0017](./0017-testes-e-ci.md) | Testes onde o erro é caro, e CI mínima no PR | Aceita |
| [0018](./0018-persistencia-ddd-com-sqlalchemy-e-alembic.md) | Persistência DDD com SQLAlchemy 2.x e Alembic | Aceita |
