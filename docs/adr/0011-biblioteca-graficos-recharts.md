# 0011. Biblioteca de gráficos: Recharts

Data: 2026-08-07

## Status

Aceita

## Contexto

O módulo de dashboards precisa de gráficos de linha, barra, pizza e cards de métricas — escopo definido no catálogo original (P-01).

## Decisão

Usar Recharts no front-end (Next.js).

## Alternativas consideradas

- **Tremor**: componentes de dashboard prontos (cards de métrica, gráficos) com visual polido out-of-the-box, construído sobre Recharts por baixo. Acelera o design inicial, mas é mais opinativo visualmente e dá menos controle fino — descartado por ora.
- **visx**: biblioteca de baixo nível (Airbnb) baseada em D3, máximo controle e customização. Exige bem mais código para montar cada gráfico do zero — overkill para o escopo atual (linha/barra/pizza/cards padrão).

## Consequências

Curva de aprendizado baixa, cobre o escopo pedido, boa comunidade e fácil de customizar com Tailwind. Se o produto evoluir para visualizações mais customizadas/complexas, pode ser necessário migrar para algo como visx em componentes específicos.
