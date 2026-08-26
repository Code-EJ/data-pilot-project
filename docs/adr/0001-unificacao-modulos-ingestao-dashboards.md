# 0001. Unificação dos módulos de Ingestão e Dashboards em um projeto único

Data: 2026-08-07

## Status

Aceita

## Contexto

O catálogo de serviços original previa dois projetos separados: P-01 (Dashboard Gerencial Web) e P-02 (Sistema de Digitalização e Centralização de Dados). O módulo de ingestão (P-02) alimenta diretamente os dados que o módulo de dashboards (P-01) visualiza.

## Decisão

Tratar os dois módulos como um único projeto, com fluxo geral **Ingestão → Validação → Armazenamento → Dashboards**.

## Alternativas consideradas

- **Dois projetos separados (P-01 e P-02 independentes)**: descartada — geraria duplicação de autenticação, modelo de dados e infraestrutura, já que um módulo depende diretamente do outro.

## Consequências

Simplifica autenticação, modelo de dados e deploy (um único sistema). Em contrapartida, acopla o roadmap dos dois módulos — não é possível evoluir ou desligar um sem considerar o outro.
