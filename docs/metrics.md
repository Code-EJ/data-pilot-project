# Definição de métricas

A fórmula de cada número exibido no Painel geral. Existe por um motivo específico: sem isso, o valor do card e o valor do gráfico são calculados por pessoas diferentes, divergem, e é sempre o cliente que descobre.

Complementa o [contrato da API](./api-contract.md) (área 8).

> **Status: proposta.** As fórmulas seguem do schema e do protótipo; as janelas de comparação são escolha minha e estão marcadas **[a validar]**.

---

## Regra de ouro

**Toda métrica é calculada em um só lugar** — um módulo de métricas na `/api`, consumido tanto pelos endpoints do painel quanto pelas exportações. Nenhuma agregação no `/web`, nenhuma consulta agregada escrita direto num handler.

O teste que prova que isso está valendo: o total exportado em Excel bate, ao centavo, com o card do painel usando os mesmos filtros. Se divergir, alguém escreveu a consulta duas vezes.

## Base comum a tudo

Todo cálculo parte de `sales_records`, com três cláusulas que **nunca** podem faltar:

```sql
where organization_id = :empresa_ativa
  and deleted_at is null
  and sale_date between :date_from and :date_to
```

Mais os filtros opcionais do painel: `business_unit_id` e `category_id`.

- A data de referência é sempre `sale_date` (quando a venda aconteceu), **nunca** `created_at` (quando foi digitada). Uma planilha de julho importada em agosto conta em julho.
- Exceção: as métricas de importação usam `import_batches.uploaded_at`, porque medem a operação de importar, não a venda.
- Dinheiro sempre em `numeric`. Arredondamento só na apresentação final — nunca em passo intermediário, senão a soma das partes não fecha com o total.

## Período anterior

**[a validar]** O período anterior tem a **mesma duração**, imediatamente antes do período atual. "Últimos 30 dias" compara com os 30 dias anteriores a esses.

A alternativa seria comparar com o mesmo período do ano anterior, o que é melhor para negócio sazonal. Escolhi a duração equivalente por ser mais previsível para o usuário e por não exigir 13 meses de histórico para funcionar — no piloto, o cliente pode ter acabado de importar os dados.

**Variação:** `(atual − anterior) / anterior`, em porcentagem, uma casa decimal.
Se `anterior = 0`, a variação **não é calculada** — a API devolve `null` e a tela mostra `—`. Dividir por zero ou exibir "+∞%" é pior que não mostrar nada.

---

## Cards de KPI (`GET /dashboard/summary`)

### Receita total

```
sum(value)
```
sobre a base comum. Variação em **%** contra o período anterior.

### Registros importados

```
sum(import_batches.valid_records)
where uploaded_at between :date_from and :date_to
```

Conta pela **operação de importação**, não por `sales_records`. Duas razões: é o que o rótulo do card diz ("registros importados", não "registros de venda"), e assim o número não muda retroativamente quando alguém exclui um registro. Variação em **%**.

Este card **ignora** os filtros de unidade e categoria — um lote de importação não pertence a uma unidade só. A tela precisa deixar isso claro, ou o usuário vai estranhar que o número não reage ao filtro. **[a validar]**

### Taxa de erro de importação

```
sum(error_records) / sum(total_records)
where uploaded_at between :date_from and :date_to
```

Em porcentagem, uma casa decimal. `total_records = 0` no período → devolve `null`, tela mostra `—`.

Variação em **pontos percentuais** (`atual − anterior`), não em porcentagem — é o que o protótipo exibe (`0,8 p.p.`) e é a leitura correta para comparar duas taxas. Dizer que uma taxa "caiu 25%" quando foi de 3,1% para 2,3% é tecnicamente verdade e comunica mal.

**Duplicatas não entram no numerador.** Duplicata não é erro de qualidade do arquivo — é o sistema funcionando.

### Unidades ativas

```
count(*) filter (where active) || ' / ' || count(*)
from business_units
```

Sem recorte de período: é um retrato do agora. Sem variação — o protótipo mostra "estável".

### Sparklines

Cada card traz uma série de 12 pontos mensais da própria métrica, terminando no mês do fim do período. Serve como contexto visual; não precisa respeitar `date_from` exatamente.

---

## Receita mensal (`GET /dashboard/revenue-monthly`)

Série dos **últimos 12 meses** contados a partir do fim do período selecionado, agregada por mês de `sale_date`.

Mês sem venda entra com **zero**, não é omitido — omitir faria o gráfico de linha pular meses e mentir sobre a tendência.

Ignora `date_from`/`date_to` (são sempre 12 meses), mas **respeita** os filtros de unidade e categoria.

---

## Receita por unidade (`GET /dashboard/revenue-by-unit`)

```
sum(value) group by business_unit_id
```
sobre a base comum, ordenado do maior para o menor.

Cada fatia leva o valor e o percentual do total. Os percentuais são arredondados para inteiro **e ajustados** para somar exatamente 100 — a maior sobra absorve a diferença. Sem isso, a legenda mostra 99% ou 101% e parece defeito.

Unidades sem venda no período não aparecem.

---

## Real vs. meta por categoria (`GET /dashboard/category-performance`)

Duas séries por categoria:

**Real** — `sum(value) group by category_id` sobre a base comum.

**Meta** —
```sql
sum(target_value) from sales_goals
where organization_id = :empresa
  and (year, month) dentro do período
  and business_unit_id in (:unidades filtradas ou todas)
```

Três regras que decidem se esse gráfico diz a verdade:

1. **Meta ausente conta como zero.** Se uma unidade não teve meta lançada, ela contribui com zero para a soma — a barra de meta fica menor que a intenção real do gestor. É por isso que a tela avisa quantas unidades estão sem meta no ano ([data-model.md](./architecture/data-model.md)); sem o aviso, o gráfico mente em silêncio.
2. **Meta é mensal; o período pode não ser.** Se o período selecionado não cobrir meses inteiros, a meta é **rateada por dia** dentro do mês parcial. **[a validar]** — a alternativa é só permitir períodos de meses fechados nesse gráfico, o que é mais honesto e menos flexível.
3. Categoria com meta e sem venda aparece com real zero. Categoria com venda e sem meta aparece com meta zero. Nenhuma das duas é omitida.

---

## Importações recentes (`GET /dashboard/recent-imports`)

As 4 últimas de `import_batches` por `uploaded_at desc`, com nome do arquivo, quem enviou, contagem e status. Sem cálculo — é a mesma consulta do Histórico com `page_size=4`.

---

## Formato de resposta

A API devolve valores **crus**, o front formata. Dinheiro como string decimal (`"284750.00"`), percentual como número (`12.4`), data em ISO.

Nenhum endpoint devolve `"R$ 284.750"` — formatação é apresentação, e concentrá-la no front garante que o mesmo número exportado para Excel entre como número, não como texto.

---

## Testes que provam que isso funciona

- Soma das fatias de "receita por unidade" = "receita total", ao centavo, com os mesmos filtros
- Percentuais da rosca somam exatamente 100
- Exportação de registros com filtro X soma o mesmo que o card de receita com filtro X
- Período anterior com receita zero devolve variação `null`, não erro nem infinito
- Registro com `deleted_at` preenchido não entra em nenhuma métrica
- Registro de outra empresa não entra em nenhuma métrica
- Mês sem venda aparece com zero na série mensal
