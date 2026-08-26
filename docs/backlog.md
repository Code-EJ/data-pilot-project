# Backlog do piloto

Backlog organizado em sprints curtas e sequenciais. Um card só é concluído com o [Definition of Done](./definition-of-done.md); o texto abaixo informa apenas o objetivo e o aceite específico.

**Tamanhos:** P até meio dia; M até um dia; G até dois dias. Card maior deve ser dividido antes de entrar na sprint.

## Sprint 0 — Fundação concluída

| Item | Estado |
|---|---|
| Compose com `web`, `api`, `worker`, `db` e `migrate` | Concluído |
| Migration inicial aplicada automaticamente pelo Compose | Concluído |
| API em DDD: controller, service/DTO, domínio e infraestrutura | Concluído |
| Configuração tipada, CORS e healthcheck | Concluído |
| Front e worker sem funcionalidade de produto | Concluído |

O `worker` permanece apenas como esqueleto. Não há cards de fila no piloto, conforme a [ADR-0007](./adr/0007-processamento-assincrono-backgroundtasks.md).

---

## Sprint 1 — Base da API

Objetivo: tornar a fundação atual pronta para recursos de negócio.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| BASE-01 | Sessão SQLAlchemy por requisição | Dependency abre, entrega e fecha uma `Session`; rollback em erro. | — | P |
| BASE-02 | Base e mapeamentos de persistência | Modelos SQLAlchemy ficam em `infrastructure`; entidades de domínio não os importam. | BASE-01 | M |
| BASE-03 | Unit of Work | Service confirma ou desfaz uma transação por caso de uso. | BASE-01 | M |
| BASE-04 | Erro padronizado da API | Erros saem em `{code, message, fields?}`; validação também segue o formato. | — | M |
| BASE-05 | Dependência de autenticação | Rota protegida sem sessão responde `401`; token inválido não vaza detalhes. | — | M |
| BASE-06 | Base de testes da API | Fixture sobe schema isolado e permite testar repository, service e rota. | BASE-01 | M |
| BASE-07 | CI mínima | Pull request executa testes, typecheck e build do front. | BASE-06 | M |

## Sprint 2 — Conta e sessão

Objetivo: permitir criar conta e entrar, sem ainda acessar dados de empresa.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| AUTH-01 | Repositório de usuário | Busca por e-mail e inclusão respeitam unicidade global. | BASE-02 | P |
| AUTH-02 | Cadastro de conta | `POST /auth/register` cria hash de senha; e-mail repetido retorna `409`. | AUTH-01 | M |
| AUTH-03 | Login e cookie | `POST /auth/login` emite cookie httpOnly; falha retorna `401` genérico. | AUTH-01, BASE-05 | M |
| AUTH-04 | Logout | `POST /auth/logout` remove o cookie; rota protegida volta a retornar `401`. | AUTH-03 | P |
| AUTH-05 | Perfil autenticado | `GET /auth/me` retorna id, nome e e-mail sem hash. | AUTH-03 | P |
| AUTH-06 | Telas Entrar e Criar conta | Formulários chamam a API, mostram erro e redirecionam após sucesso. | AUTH-02, AUTH-03 | M |

## Sprint 3 — Empresas e permissões

Objetivo: introduzir a empresa ativa e garantir o isolamento de dados.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| ORG-01 | Criar empresa e membership inicial | Uma transação cria empresa e vínculo `admin` do criador. | AUTH-05, BASE-03 | M |
| ORG-02 | Empresa ativa na dependency | Header válido resolve membership; sem vínculo retorna `404`. | ORG-01 | M |
| ORG-03 | Listar empresas no perfil | `/auth/me` retorna empresas e papel da pessoa. | ORG-01 | P |
| ORG-04 | Adicionar membro existente | E-mail exato; inexistente retorna `404` e membro repetido, `409`. | ORG-02 | M |
| ORG-05 | Alterar ou remover papel | Impede deixar empresa sem admin; escrita exige admin. | ORG-04 | M |
| ORG-06 | Tela Suas empresas e seletor | Seleção persiste no navegador e envia a empresa ativa nas chamadas. | ORG-03 | M |
| ORG-07 | Tela Usuários da empresa | Admin lista, adiciona, altera e remove; perfil usuário não acessa a tela. | ORG-04, ORG-05 | M |

## Sprint 4 — Dimensões e leitura de registros

Objetivo: entregar a primeira fatia vertical de leitura por empresa.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| DIM-01 | Seed de dimensões | Comando cria admin, empresa, unidades e categorias de desenvolvimento. | ORG-01 | M |
| DIM-02 | Consultas de dimensões | Unidades e categorias retornam apenas dados da empresa ativa. | ORG-02 | P |
| REG-01 | Repositório de registros | Listagem aplica `organization_id` e `deleted_at is null` sempre. | ORG-02 | M |
| REG-02 | Endpoint paginado de registros | Filtros de período, unidade, origem e busca; dinheiro sai como string decimal. | REG-01 | M |
| REG-03 | Client TypeScript do OpenAPI | Comando gera o client e o front o utiliza para a listagem. | REG-02 | M |
| REG-04 | Tela Registros | Tabela, filtros, paginação e estados de carregamento, vazio e erro. | REG-02, REG-03 | M |

## Sprint 5 — Cadastro manual e metas

Objetivo: permitir ao Admin manter registros e metas mensais.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| REG-05 | Criar registro manual | Admin cria com `origin=manual`; campos inválidos apontam o erro. | REG-01 | M |
| REG-06 | Editar e excluir logicamente | Atualiza auditoria; exclusão preenche `deleted_at` e retorna `204`. | REG-05 | M |
| REG-07 | Tela Cadastro manual | Formulário usa dimensões e permite salvar e adicionar outro. | REG-05, DIM-02 | M |
| REG-08 | Ações na tela Registros | Admin edita e confirma exclusão; usuário somente lê. | REG-06, REG-04 | M |
| GOAL-01 | Repositório e leitura de metas | Retorna grade anual por unidade, incluindo meses sem meta. | ORG-02 | M |
| GOAL-02 | Upsert de metas em lote | Salva a grade em uma transação; `null` remove e `0` mantém meta zero. | GOAL-01 | M |
| GOAL-03 | Cobertura e sugestão | Informa unidades sem meta e sugere realizado do ano anterior. | GOAL-01, REG-01 | M |
| GOAL-04 | Tela Metas | Grade editável para Admin; usuário vê somente leitura e aviso de cobertura. | GOAL-02, GOAL-03 | G |

## Sprint 6 — Ingestão: processamento

Objetivo: receber uma planilha, validar linhas e persistir o resultado.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| IMP-01 | Leitor e análise de arquivo | CSV/XLSX devolve cabeçalho, amostra e mapeamento sugerido sem gravar dados. | DIM-02 | M |
| IMP-02 | Conversão de data e valor | Formatos definidos em [import-spec.md](./import-spec.md) passam em testes. | IMP-01 | M |
| IMP-03 | Resolução de dimensões | Unidade ou categoria inexistente rejeita a linha; importação não cria dimensão. | IMP-02 | M |
| IMP-04 | Regra de duplicata | Compara a chave natural dentro da empresa e ignora registros excluídos. | IMP-03, REG-01 | M |
| IMP-05 | Orquestrador de importação | Persiste batch, registros e rejeições; testa `total = valid + error + duplicate`. | IMP-04 | G |
| IMP-06 | Endpoints de análise e envio | Análise não grava; envio responde `202` e processa em `BackgroundTasks`. | IMP-01, IMP-05 | M |
| IMP-07 | Recuperação de batch travado | Batch em `processing` por mais de 15 minutos passa a `failed` na subida. | IMP-05 | P |

## Sprint 7 — Ingestão: acompanhamento

Objetivo: tornar a importação utilizável e auditável pela interface.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| IMP-08 | Status, histórico e rejeições | Endpoints filtram por empresa e expõem contagens, detalhes e duplicatas. | IMP-05 | M |
| IMP-09 | Planilha modelo | Download contém as colunas previstas na especificação. | IMP-01 | P |
| IMP-10 | Tela Ingestão: arquivo e mapeamento | Dropzone, amostra e campos obrigatórios bloqueiam envio incompleto. | IMP-06 | M |
| IMP-11 | Tela Ingestão: resultado | Polling termina no status final e mostra contagens e rejeições. | IMP-06, IMP-08 | M |
| IMP-12 | Tela Histórico | Lista batches, filtra status e abre detalhes das rejeições. | IMP-08 | M |

## Sprint 8 — Painel

Objetivo: apresentar métricas calculadas exclusivamente pela API.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| DASH-01 | Serviço de métricas | Consultas agregadas ficam em um módulo; front não calcula números. | REG-01 | M |
| DASH-02 | Período atual e anterior | Calcula período anterior de mesma duração; divisão por zero retorna `null`. | DASH-01 | P |
| DASH-03 | Summary e receita mensal | APIs retornam KPIs, sparklines e meses sem venda como zero. | DASH-02 | M |
| DASH-04 | Receita por unidade | Percentuais somam 100 e dados excluídos não entram. | DASH-01 | M |
| DASH-05 | Realizado versus meta | Meta ausente vale zero e cobertura vem no resultado. | DASH-01, GOAL-01 | M |
| DASH-06 | Tela Painel | Filtros, cards e gráficos Recharts exibem os dados da API. | DASH-03..05 | G |
| DASH-07 | Importações recentes | Painel mostra os quatro últimos batches com link ao histórico. | IMP-08, DASH-06 | P |

## Sprint 9 — Fechamento do piloto

Objetivo: preparar a entrega, operação e uso em tablet.

| ID | Card | Aceite | Dep. | Tam. |
|---|---|---|---|---|
| EXP-01 | Exportação CSV | Respeita os filtros da listagem e limita 50 mil linhas. | REG-02 | M |
| EXP-02 | Exportação XLSX | Arquivo preserva números como números, não texto. | EXP-01 | M |
| EXP-03 | Exportação PDF | Cabeçalho mostra filtros aplicados e layout cabe em página. | EXP-01 | M |
| EXP-04 | Relatório de rejeições | Download contém somente as linhas rejeitadas do batch selecionado. | IMP-08 | P |
| FIN-01 | Backup e restore | Backup automatizado e restore testado em banco limpo. | BASE-07 | G |
| FIN-02 | Responsividade e acessibilidade | Telas funcionam em 768 px, foco é visível e inputs têm label. | DASH-06 | M |
| FIN-03 | Guia de operação | Explica subir stack, migration, seed, backup e restore. | FIN-01 | P |

---

## Regras de planejamento

- Só entra card cuja dependência esteja concluída.
- Mudança de schema exige migration Alembic no mesmo card.
- Um card de interface só começa quando o endpoint e o contrato estiverem estáveis.
- Antes de iniciar a Sprint 6, validar [import-spec.md](./import-spec.md); antes da Sprint 8, validar [metrics.md](./metrics.md).
