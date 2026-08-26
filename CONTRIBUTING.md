# Contribuindo

## As quatro regras

O raciocínio completo está em [docs/architecture/overview.md](./docs/architecture/overview.md). Estas quatro valem em toda linha de código:

1. **Regra de negócio, acesso a banco e autorização ficam na `/api`.** Sempre.
2. **O `/web` renderiza e chama a API.** Não acessa banco, não usa Route Handlers como camada intermediária, não decide negócio ([ADR-0002](./docs/adr/0002-frontend-nextjs-spa.md)).
3. **Toda consulta de dado de negócio filtra por `organization_id` e por `deleted_at is null`.** A empresa vem da sessão, nunca de parâmetro do cliente ([ADR-0014](./docs/adr/0014-escopo-por-empresa-organizations.md)).
4. **Não adicione dependência nem serviço novo sem uma ADR.** Vários já foram deliberadamente deixados de fora.

Na dúvida sobre onde algo mora, pergunte antes de implementar — é mais barato que refatorar depois.

## Consultas ficam numa camada de repositório

Nada de `session.query(...)` espalhado pelos handlers. Toda leitura e escrita de dado de negócio passa por uma função de repositório que já aplica os filtros da regra 3. Isso não é preciosismo de organização: é o que garante que, quando um filtro obrigatório mudar (ou quando Row-Level Security entrar), exista **um lugar só** para mexer — em vez de trinta chamadas para auditar uma a uma.

## Segurança não mora na UI

O navegador fala direto com a API ([ADR-0002](./docs/adr/0002-frontend-nextjs-spa.md)), então a API é pública. Esconder um botão é conveniência visual, não controle de acesso. Toda regra de permissão ([ADR-0009](./docs/adr/0009-rbac-dois-perfis.md)) precisa ser verificada no servidor, em cada endpoint.

## Registrando uma decisão de arquitetura (ADR)

Sempre que uma escolha técnica não-óbvia for tomada (troca de biblioteca, mudança de escopo, decisão de infra), registre em [docs/adr](./docs/adr/README.md):

1. Copie [docs/adr/template.md](./docs/adr/template.md) para `docs/adr/000X-titulo-curto.md` (próximo número sequencial)
2. Preencha contexto, decisão, alternativas descartadas e consequências
3. Adicione a linha na tabela de [docs/adr/README.md](./docs/adr/README.md)
4. Se a decisão substitui uma ADR antiga, marque a antiga como "Superada por ADR-000X" — não edite nem apague o conteúdo antigo

## Branches e commits

- Branches: `feature/nome-curto`, `fix/nome-curto`, `docs/nome-curto`
- Commits: descreva o "porquê" da mudança, não só o "o quê" (o diff já mostra o que mudou)

## Checklist de PR

- [ ] Toda consulta nova filtra por `organization_id` e por `deleted_at is null`
- [ ] Toda regra de permissão nova é verificada no servidor, não só escondida na UI
- [ ] Se mudou endpoint ou schema da API, o client TypeScript foi regerado ([ADR-0005](./docs/adr/0005-comunicacao-rest-openapi.md))
- [ ] Se mudou tabela, existe migration do Alembic no PR
- [ ] Nenhuma regra de negócio nova no `/web`
- [ ] Se a mudança envolveu uma escolha técnica não-óbvia, existe ADR

## Quando travar

Se você ficar mais de meio dia sem avançar em uma tarefa, avise no canal do time. Não é sinal de que você não sabe — é como o projeto evita perder uma semana em um problema que outra pessoa resolve em dez minutos. Travar em silêncio é o maior risco de prazo que temos.
