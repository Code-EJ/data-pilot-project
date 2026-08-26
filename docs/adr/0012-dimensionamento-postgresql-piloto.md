# 0012. Dimensionamento inicial do PostgreSQL para o piloto

Data: 2026-08-07

## Status

Aceita

## Contexto

Era preciso estimar a escala de dados esperada para decidir se o schema/infra inicial precisa de cuidados extras (particionamento, índices avançados, read replicas) desde o começo.

## Decisão

Dimensionar para volume pequeno/piloto: milhares a poucas centenas de milhares de linhas (planilhas típicas de PME, até dezenas de milhares de linhas por importação). Uma instância Postgres padrão, sem particionamento, sem read replica.

## Alternativas consideradas

- **Médio (milhões de linhas)**: exigiria índices bem planejados desde o início e possivelmente particionamento por data/unidade de negócio. Descartado por ora — mais cuidado de modelagem agora significa mais tempo de design de schema antes de começar a codar, sem um cliente real que justifique essa escala ainda.

## Consequências

Schema inicial mais simples e rápido de implementar. **Ponto a revisitar:** quando houver um cliente/piloto real com clareza de volume, reavaliar necessidade de particionamento e índices — esse é o item mais provável de precisar de um ADR de revisão no curto prazo.
