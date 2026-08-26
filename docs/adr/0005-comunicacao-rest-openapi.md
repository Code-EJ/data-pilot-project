# 0005. Comunicação `/web` ↔ `/api` via REST + client gerado do OpenAPI

Data: 2026-08-07

## Status

Aceita

## Contexto

`/web` (Next.js, TypeScript) e `/api` (FastAPI, Python) são processos e linguagens separados (ver [ADR-0002](./0002-frontend-nextjs-spa.md), [ADR-0003](./0003-backend-dominio-fastapi.md), [ADR-0013](./0013-repo-unico-sem-monorepo.md)) e precisam de um contrato de comunicação tipado. Como o `/web` opera em modo SPA, quem faz essas chamadas é o navegador, não um servidor Node intermediário.

## Decisão

Usar REST, com um client TypeScript gerado a partir do schema OpenAPI que a FastAPI expõe nativamente. Validação de schema com Zod (TS) e Pydantic (Python) em cada ponta.

O client gerado é versionado no repositório e regenerado por um script (`npm run gen:api`) sempre que o contrato mudar.

## Alternativas consideradas

- **tRPC**: descartada por não ser cross-language — tRPC pressupõe TypeScript nas duas pontas, o que não é o caso aqui.
- **Tipos escritos à mão no front**: mais simples de começar, mas garantidamente desatualizados. O client gerado custa um comando e elimina uma classe inteira de bug ("a API mudou e ninguém avisou o front") — que é exatamente o tipo de erro difícil de diagnosticar para quem tem pouca experiência.

## Consequências

Contrato tipado de ponta a ponta sem exigir um pacote de tipos compartilhado no mesmo build — o client nasce do schema publicado pela FastAPI, não de código-fonte comum. Isso é compatível com a decisão de repositório único sem ferramenta de monorepo ([ADR-0013](./0013-repo-unico-sem-monorepo.md)).

Exige regenerar o client sempre que o schema OpenAPI mudar; se isso for esquecido, o front compila contra um contrato velho. Vale tornar a regeneração parte do checklist de PR que altera endpoint.

Como o client roda no navegador, **a API é pública**: toda autorização é responsabilidade da FastAPI ([ADR-0006](./0006-autenticacao-jwt-fastapi.md), [ADR-0009](./0009-rbac-dois-perfis.md)). Nada de segurança pode depender de a UI "não mostrar o botão".
