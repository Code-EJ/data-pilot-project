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
  "fields": { "nome_do_campo": "motivo da falha" } // Opcional, presente apenas no erro 422
}
