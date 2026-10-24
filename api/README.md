# api

Backend de domínio em FastAPI (Python). Ver [ADR-0003](../docs/adr/0003-backend-dominio-fastapi.md).

É o único serviço com acesso ao banco e o dono de tudo que não é interface.

Responsabilidades:

- Regras de negócio dos módulos de identidade, ingestão e dashboards
- Autenticação: cadastro, login, emissão e validação do JWT ([ADR-0006](../docs/adr/0006-autenticacao-jwt-fastapi.md))
- Autorização: resolve o perfil do usuário **na empresa ativa** a cada requisição, a partir de `memberships` ([ADR-0009](../docs/adr/0009-rbac-dois-perfis.md))
- Validação (Pydantic) e persistência (SQLAlchemy + Alembic + PostgreSQL, [ADR-0004](../docs/adr/0004-banco-dados-postgresql.md))
- Parsing e validação de planilhas com Pandas, em `BackgroundTasks` ([ADR-0007](../docs/adr/0007-processamento-assincrono-backgroundtasks.md))
- Gateway de integração via REST ou leitura direta de banco
- Endpoints de agregação que alimentam os gráficos — o front não calcula métrica
- Expõe o schema OpenAPI consumido pelo `/web` para gerar o client TS ([ADR-0005](../docs/adr/0005-comunicacao-rest-openapi.md))

**Regra que não pode ser esquecida:** toda consulta de dado de negócio filtra por `organization_id` (da sessão, nunca do cliente) e por `deleted_at is null` ([ADR-0014](../docs/adr/0014-escopo-por-empresa-organizations.md)). Por isso as queries vivem numa camada de repositório, não espalhadas pelos handlers — ver [CONTRIBUTING.md](../CONTRIBUTING.md).

## Padrão de Resposta de Erros da API

Para evitar exposição de dados sensíveis e facilitar o tratamento no front-end, todas as respostas de erro da API seguem um contrato único. O formato base é:

```json
{
  "code": "string_com_o_codigo_do_erro",
  "message": "Mensagem amigável que pode ser exibida ao usuário final",
  "fields": { "nome_do_campo": "motivo da falha" }
}
```

`fields` é opcional e aparece apenas no erro 422.

## Ambiente local e testes

No PowerShell, a partir da raiz do repositório, use Python 3.13:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r api/requirements-dev.txt
cd api
..\.venv\Scripts\python.exe -m pytest tests --ignore=tests/integration
```

`requirements.txt` contém as dependências da API; `requirements-dev.txt` inclui também o pytest, previsto na [ADR-0017](../docs/adr/0017-testes-e-ci.md).

O banco de desenvolvimento usa PostgreSQL 17, porta 5432 e o volume persistente `postgres_data`. Para iniciá-lo a partir da raiz do repositório, execute `docker compose up -d --wait db`.

Para executar também os testes de integração, use o Compose de testes em um projeto separado e rode a suíte completa, ainda no diretório `api`:

```powershell
docker compose -p projetopiloto-base03-test -f ../docker-compose.test.yml up -d --wait db
..\.venv\Scripts\python.exe -m pytest tests
```

Os testes de integração usam PostgreSQL 17, banco `uow_db` em `localhost:5433`, com o driver `psycopg` declarado nas dependências. A porta separada permite manter o banco de desenvolvimento ativo. O comando aguarda o healthcheck antes de retornar.

Cada teste cria um schema exclusivo e o remove ao terminar. A cobertura inclui commit, rollback após `flush`, rollback por erro de integridade e saída sem commit. O projeto Compose separado evita reutilizar volumes de outra versão do PostgreSQL.
