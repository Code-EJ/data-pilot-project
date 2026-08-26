# 0013. Repositório único com pastas independentes, sem ferramenta de monorepo

Data: 2026-08-07

## Status

Aceita

## Contexto

`/web` (Next.js) e `/api` (FastAPI) são linguagens diferentes (TypeScript e Python) que se comunicam só via HTTP (ver [ADR-0005](./0005-comunicacao-rest-openapi.md)) — não há código compartilhado em tempo de build entre elas: o client TS é gerado a partir do schema OpenAPI publicado, não de um pacote de tipos comum. Era preciso decidir a estrutura de repositório(s) e se valeria usar uma ferramenta de monorepo (Turborepo ou Nx).

## Decisão

Um único repositório Git, com `/web` e `/api` como pastas irmãs independentes — cada uma com seu próprio gerenciador de dependências (`package.json` / `pyproject.toml`) e sem ferramenta de monorepo orquestrando build ou cache entre elas.

## Alternativas consideradas

- **Turborepo**: leve e focado em JS/TS, mas a `/api` ficaria fora do grafo de cache/build de qualquer forma — o ganho se limitaria ao `/web`, e não há pacote TS compartilhado a cachear.
- **Nx**: suporte multi-linguagem mais robusto (inclusive Python via plugins), mas maior curva de aprendizado e overhead de configuração — desproporcional ao problema real, que é só comunicação HTTP entre duas linguagens.
- **Dois repositórios Git separados**: máximo desacoplamento, permitiria deploys e times totalmente independentes. Descartada por ora — exigiria coordenar versões entre repos a cada mudança de contrato de API e espalharia PRs e issues em dois lugares, sem um motivo concreto para esse nível de isolamento ainda.

## Consequências

Estrutura simples de clonar e rodar, sem ferramenta de build adicional para aprender ou manter. Web e API evoluem com histórico de commits e PRs unificados — o que também facilita revisar uma mudança que atravessa as duas pontas (endpoint novo + tela que o consome) em um PR só.

Sem cache de build compartilhado entre as partes, mas isso não é perda real: as linguagens são diferentes e não há código-fonte comum.

Se no futuro surgir necessidade de deploys ou times totalmente independentes, migrar para dois repositórios é possível separando o histórico das pastas.
