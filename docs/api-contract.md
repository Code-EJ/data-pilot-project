# Contrato da API — estimativa de endpoints

Levantamento de **todos os endpoints** que o protótipo (`docs/prototype/index.html`) e o [modelo de dados](./architecture/data-model.md) exigem. Serve para o time ter uma convenção única antes de escrever o primeiro endpoint, em vez de cada pessoa inventar a sua.

> **Status: estimativa.** Nada aqui é ADR. Foi derivado das telas e do schema, não validado com o cliente. Onde eu tive que decidir algo que a documentação não define, está marcado com **[decisão a validar]**. O contrato verdadeiro será o schema OpenAPI que a FastAPI publica ([ADR-0005](./adr/0005-comunicacao-rest-openapi.md)) — este documento é o ponto de partida, e deve ser considerado desatualizado assim que o código existir.

---

## Convenções

Valem para todos os endpoints. Divergir delas em um endpoint específico exige justificativa no PR.

### Prefixo e versão

Tudo sob `/api/v1`. O `v1` no caminho é barato agora e evita quebrar o front no dia de uma mudança incompatível.

### Autenticação

Cookie `httpOnly` com o JWT emitido pela API ([ADR-0006](./adr/0006-autenticacao-jwt-fastapi.md)). O front nunca lê o token; o navegador o envia automaticamente. Sem cookie válido → `401`.

### Empresa ativa

Todo endpoint marcado com 🏢 exige o header:

```
X-Organization-Id: 42
```

A API **sempre** verifica que existe `membership` do usuário autenticado naquela empresa e resolve o papel dali. O valor enviado é uma afirmação a verificar, nunca uma autorização ([ADR-0014](./adr/0014-escopo-por-empresa-organizations.md)).

**[decisão a validar]** Header em vez de `/organizations/{id}/...` no caminho. O header deixa as rotas mais curtas e impede que alguém esqueça o filtro por "a rota não tinha o id". A alternativa (id no caminho) é mais explícita e mais fácil de cachear. Escolhi o header porque o filtro passa a vir de uma dependency única do FastAPI, aplicada em todas as rotas — que é o contrapeso certo para um time em formação.

### Autorização

| Marcação | Quem pode |
|---|---|
| 🔓 | Qualquer um, sem sessão |
| 🔑 | Qualquer usuário autenticado |
| 🏢 | Autenticado **e** membro da empresa ativa |
| 👑 | Membro da empresa ativa com papel `admin` |

Ver [ADR-0009](./adr/0009-rbac-dois-perfis.md). Toda regra é verificada no servidor — esconder o botão no front não conta.

### Códigos de resposta

| Código | Quando |
|---|---|
| `200` | Sucesso com corpo |
| `201` | Recurso criado |
| `204` | Sucesso sem corpo (exclusão) |
| `400` | Requisição malformada |
| `401` | Sem sessão válida |
| `403` | Autenticado e membro, mas sem papel para a ação |
| `404` | Recurso inexistente **ou de outra empresa** |
| `409` | Conflito de estado (e-mail já cadastrado, pessoa já é membro, último admin) |
| `422` | Validação de campo falhou |

**Regra importante:** um recurso que existe mas pertence a outra empresa responde `404`, nunca `403`. Responder `403` confirmaria a existência do recurso e permitiria mapear a base de outra empresa por tentativa e erro.

### Formato de erro

Um formato só, em todos os erros. Exige um exception handler customizado — o padrão do FastAPI (`{"detail": ...}`) não serve porque muda de forma entre `422` e os demais.

```json
{
  "code": "validation_error",
  "message": "Não foi possível salvar o registro.",
  "fields": { "value": "Informe um valor válido, ex: 1204.50" }
}
```

`fields` só aparece em `422`. `code` é um identificador estável que o front pode testar; `message` é texto para exibir.

### Paginação

Query: `?page=1&page_size=25` (padrão 25, máximo 100).

```json
{ "items": [], "page": 1, "page_size": 25, "total": 14 }
```

### Formato dos valores no wire

- **Dinheiro: string decimal** — `"1204.50"`, ponto como separador, sem símbolo. Nunca `number`: JSON não tem decimal, e `1204.50` em float vira `1204.4999...` em algum momento. Isso espelha o `numeric(12,2)` do banco.
- **Datas: ISO 8601** — `"2026-08-05"` para data, `"2026-08-05T17:32:00-03:00"` para timestamp.
- Formatação brasileira (`R$ 1.204,50`, `05/08/2026`) é responsabilidade do front. A API não formata.

---

## 1. Autenticação e conta

| | Método | Rota | Descrição |
|---|---|---|---|
| 🔓 | `POST` | `/auth/register` | Cria a conta. Corpo: `name`, `email`, `password`. `409` se o e-mail já existe. |
| 🔓 | `POST` | `/auth/login` | Valida credenciais e devolve o cookie de sessão. `401` genérico em falha — não distinguir "e-mail não existe" de "senha errada". |
| 🔑 | `POST` | `/auth/logout` | Limpa o cookie. Não invalida o token no servidor (não há lista de revogação, [ADR-0006](./adr/0006-autenticacao-jwt-fastapi.md)). |
| 🔑 | `GET` | `/auth/me` | Dados da pessoa **e a lista de empresas com o papel em cada uma**. É o que monta a tela "Suas empresas". |

**Resposta de `/auth/me`:**

```json
{
  "id": 7,
  "name": "Marina Alves",
  "email": "marina.alves@grupovertice.com.br",
  "organizations": [
    { "id": 1, "name": "Grupo Vértice", "role": "admin",
      "business_units_count": 5, "members_count": 8 },
    { "id": 2, "name": "Padaria Aurora", "role": "usuario",
      "business_units_count": 2, "members_count": 3 }
  ]
}
```

Os dois contadores aparecem nos cards da tela e evitam N chamadas extras.

**Fora do v1:** verificação de e-mail, recuperação de senha, refresh token, 2FA.

---

## 2. Empresas

| | Método | Rota | Descrição |
|---|---|---|---|
| 🔑 | `POST` | `/organizations` | Cria empresa. Corpo: `name`, `tax_id` (opcional). Cria também o `membership` do criador como `admin`. **`403` se o solicitante não for admin de nenhuma empresa** ([ADR-0009](./adr/0009-rbac-dois-perfis.md)). |
| 🏢 | `GET` | `/organizations/current` | Dados da empresa ativa, para a barra superior. |
| 👑 | `PATCH` | `/organizations/current` | Edita nome e CNPJ. **[decisão a validar]** — nenhuma tela do protótipo faz isso ainda. |

A listagem das empresas do usuário sai de `/auth/me`, não de `GET /organizations` — não existe caso de uso para listar empresas que não são suas, e um endpoint desses seria uma porta para enumerar a base.

---

## 3. Usuários da empresa

Tela **Usuários da empresa**, exclusiva de Admin.

| | Método | Rota | Descrição |
|---|---|---|---|
| 👑 | `GET` | `/members` 🏢 | Lista os membros. Query: `q` (busca por nome ou e-mail), `role`. Devolve nome, e-mail, papel e data de entrada. |
| 👑 | `POST` | `/members` 🏢 | Adiciona pessoa existente. Corpo: `email` (exato), `role`. `404` se não houver conta com esse e-mail; `409` se já for membro. |
| 👑 | `PATCH` | `/members/{user_id}` 🏢 | Altera o papel. `409` se rebaixar o último admin. |
| 👑 | `DELETE` | `/members/{user_id}` 🏢 | Remove o acesso. `409` se remover o último admin. |

**Sem busca parcial de usuário, por design.** Não existe `GET /users?q=...`: uma busca por trecho de e-mail permitiria enumerar quem tem conta na plataforma. O `POST /members` recebe o e-mail exato e devolve `404` sem revelar nada além disso.

**[decisão a validar]** Rebaixar ou remover a si mesmo é permitido, desde que não seja o último admin. Alternativa: bloquear sempre, para evitar que alguém se tranque para fora por engano.

---

## 4. Dimensões (unidades e categorias)

Alimentam os filtros de praticamente todas as telas e os `<select>` do cadastro manual.

| | Método | Rota | Descrição |
|---|---|---|---|
| 🏢 | `GET` | `/business-units` | Query `active=true` para o padrão dos formulários de lançamento; sem o filtro para as telas de histórico, que precisam exibir unidades já desativadas. |
| 🏢 | `GET` | `/product-categories` | |

CRUD de escrita não entra no v1 — são seed data por empresa ([data-model.md](./architecture/data-model.md)). Quando entrar, é `POST`/`PATCH` nas mesmas rotas, 👑.

---

## 5. Registros

Tela **Registros** e **Cadastro manual**.

| | Método | Rota | Descrição |
|---|---|---|---|
| 🏢 | `GET` | `/sales-records` | Lista paginada. |
| 🏢 | `GET` | `/sales-records/{id}` | Um registro. |
| 👑 | `POST` | `/sales-records` | Cadastro manual. Grava `origin = 'manual'`, `import_batch_id = null`. |
| 👑 | `PATCH` | `/sales-records/{id}` | Edição. Preenche `updated_by` e `updated_at`. |
| 👑 | `DELETE` | `/sales-records/{id}` | Exclusão **lógica** — preenche `deleted_at`. Responde `204`. |
| 🏢 | `GET` | `/sales-records/export` | Exportação. Query `format=csv\|xlsx\|pdf` + os mesmos filtros da listagem. |

**Filtros de `GET /sales-records`:** `q` (cliente ou categoria), `business_unit_id`, `origin` (`import`/`manual`), `date_from`, `date_to`, `page`, `page_size`, `sort`.

**[decisão a validar]** O protótipo oferece período por atalho ("Últimos 30 dias", "Trimestre atual"). A API recebe `date_from`/`date_to` resolvidos, e é o front que traduz o atalho. Assim o significado de "trimestre atual" fica num lugar só e a API continua genérica.

A exportação devolve o arquivo direto (`Content-Disposition: attachment`), sem paginação. **Precisa de um teto** — sugestão de 50 000 linhas, acima disso `422` pedindo para filtrar. Sem teto, uma exportação sem filtro derruba o processo da API, que é o mesmo que atende as requisições ([ADR-0007](./adr/0007-processamento-assincrono-backgroundtasks.md)).

---

## 6. Metas

Tela **Metas**: grade categoria × mês, filtrada por ano e unidade.

| | Método | Rota | Descrição |
|---|---|---|---|
| 🏢 | `GET` | `/sales-goals` | Query obrigatória: `year`, `business_unit_id`. Devolve a grade inteira do ano. |
| 👑 | `PUT` | `/sales-goals` | Salva a grade inteira de uma vez (upsert em lote). |
| 🏢 | `GET` | `/sales-goals/suggestion` | Valores sugeridos para o botão "Restaurar sugestão". **[decisão a validar]** — a base da sugestão não está definida em lugar nenhum. Proposta: realizado do mesmo mês no ano anterior. |
| 🏢 | `GET` | `/sales-goals/coverage` | Query `year`. Quantas unidades ainda não têm meta lançada — alimenta o aviso da tela. |

**`PUT` e não `PATCH`**: a tela salva a grade inteira, e o upsert é garantido pela constraint única `(organization_id, business_unit_id, category_id, year, month)`. Enviar célula a célula geraria dezenas de requisições e um estado intermediário inconsistente se uma falhasse.

**[decisão a validar]** Uma célula apagada na tela significa "meta zero" ou "sem meta lançada"? São coisas diferentes para o gráfico real vs. meta. Proposta: `null` no corpo = remover a linha (sem meta); `0` = meta de zero.

---

## 7. Ingestão

Tela **Ingestão**, fluxo de quatro passos.

| | Método | Rota | Descrição |
|---|---|---|---|
| 🏢 | `GET` | `/imports/template` | Baixa a planilha modelo. Estática por ora; as colunas ainda precisam ser especificadas. |
| 👑 | `POST` | `/imports/analyze` | Passo 1→2. Recebe o arquivo, lê o cabeçalho e uma amostra, devolve as colunas detectadas e o mapeamento sugerido. **Não grava nada.** |
| 👑 | `POST` | `/imports` | Passo 2→3. Recebe arquivo + mapeamento confirmado. Cria o `import_batch` com `status = 'processing'`, dispara a `BackgroundTask` e responde `202` com o id. |
| 🏢 | `GET` | `/imports/{id}` | Estado do batch: status e contagens. É o alvo do polling da tela. |
| 🏢 | `GET` | `/imports/{id}/rejections` | Linhas não importadas. Query `kind=error\|duplicate`. |
| 🏢 | `GET` | `/imports/{id}/rejections/export` | "Baixar relatório de linhas não importadas". |
| 🏢 | `GET` | `/imports` | Tela **Histórico**. Filtros: `q`, `status`, `date_from`, `date_to`, paginação. |

**O arquivo sobe duas vezes** — uma em `/analyze`, outra em `/imports`. É desperdício, e é deliberado: guardar o arquivo entre os dois passos exigiria storage temporário, que o [ADR-0010](./adr/0010-sem-storage-arquivo-bruto.md) descarta. Com arquivos de até 20 MB, o custo é aceitável. **[decisão a validar]** — se incomodar, a saída é um diretório temporário com TTL curto, o que é bem menos do que reabrir o ADR-0010.

**Filtro `status` do Histórico.** A tela oferece *Processando, Concluído, Com erros, Duplicados, Falhou*. Os quatro primeiros e o último mapeiam para `import_batches.status`, mas **"Duplicados" não é um status** — é `duplicate_records > 0`. A API aceita os dois no mesmo parâmetro e traduz internamente; o front não precisa saber da diferença.

`POST /imports` responde `202`, não `201`: o recurso foi aceito, o processamento ainda não terminou.

---

## 8. Painel geral

Endpoints de agregação. **O front não calcula métrica** — recebe JSON pronto para o gráfico ([overview.md](./architecture/overview.md)).

Todos aceitam os mesmos filtros do painel: `date_from`, `date_to`, `business_unit_id`, `category_id`.

| | Método | Rota | Alimenta |
|---|---|---|---|
| 🏢 | `GET` | `/dashboard/summary` | Os quatro cards de KPI, cada um com valor, variação e a série do sparkline |
| 🏢 | `GET` | `/dashboard/revenue-monthly` | Gráfico de linha, últimos 12 meses |
| 🏢 | `GET` | `/dashboard/revenue-by-unit` | Rosca de distribuição do período |
| 🏢 | `GET` | `/dashboard/category-performance` | Barras real vs. meta por categoria |
| 🏢 | `GET` | `/dashboard/recent-imports` | Tabela "Importações recentes" (atalho para `GET /imports?page_size=4`) |

**Cinco endpoints em vez de um.** Um `/dashboard` único devolveria tudo de uma vez, mas cada filtro alterado recalcularia as quatro consultas. Separados, dá para cachear e evoluir cada um sem mexer nos outros.

**Buraco conhecido:** as fórmulas por trás desses números não estão definidas em lugar nenhum. "Receita total" com qual filtro? A variação de `+12,4%` compara com o período anterior de mesma duração ou com o mesmo período do ano passado? "Taxa de erro" é `error_records / total_records` somado no período? Isso precisa virar `docs/metrics.md` **antes** de alguém implementar, senão o número do card vai divergir do número do gráfico — e é sempre o cliente que descobre.

---

## Resumo

| Área | Endpoints | Observação |
|---|---|---|
| Autenticação e conta | 4 | |
| Empresas | 3 | 1 a validar |
| Usuários da empresa | 4 | |
| Dimensões | 2 | leitura apenas no v1 |
| Registros | 6 | inclui exportação |
| Metas | 4 | 2 a validar |
| Ingestão | 7 | |
| Painel | 5 | fórmulas ainda indefinidas |
| **Total** | **35** | |

Trinta e cinco endpoints é bastante para um piloto com time em formação, mas quase nenhum é complexo: dezoito são leitura com filtro e paginação, e seguem o mesmo padrão. Os que realmente exigem cuidado são os sete de ingestão e os cinco do painel.

## O que precisa ser resolvido antes de implementar

1. **`docs/import-spec.md`** — locale, encoding, colunas da planilha modelo e regra de validação por campo. Bloqueia a área 7 inteira.
2. **`docs/metrics.md`** — a fórmula e a janela de comparação de cada número. Bloqueia a área 8.
3. Os pontos marcados **[decisão a validar]** acima — nenhum bloqueia sozinho, mas cada um vira uma convenção diferente por pessoa se ninguém decidir.
