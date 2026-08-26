# Escopo de produto

Funcionalidades por módulo. Para o "como" (stack, decisões técnicas), ver [docs/architecture/overview.md](./architecture/overview.md) e [docs/adr](./adr/README.md). O protótipo navegável de todas as telas está em [`docs/prototype/index.html`](./prototype/index.html).

Todo dado descrito abaixo pertence a uma **empresa** e só é visível de dentro dela ([ADR-0014](./adr/0014-escopo-por-empresa-organizations.md)).

## Módulo de Identidade e Acesso

- **Criar conta** com nome, e-mail e senha. A conta é da pessoa e não pertence a nenhuma empresa; sozinha, ela não dá acesso a nada.
- **Entrar** com e-mail e senha. Sessão de 8 h, sem renovação automática ([ADR-0006](./adr/0006-autenticacao-jwt-fastapi.md)).
- **Suas empresas** — tela intermediária após o login, listando as empresas em que a pessoa tem vínculo e o perfil dela em cada uma. É onde ela escolhe em qual vai trabalhar; a empresa ativa também pode ser trocada a qualquer momento pela barra superior.
- **Cadastrar empresa** — disponível apenas para quem já é Admin de alguma empresa. Quem cria vira Admin dela automaticamente. O primeiro Admin do sistema é criado por seed.
- **Usuários da empresa** — exclusivo do perfil Admin. Lista quem tem acesso, permite alterar o perfil de cada pessoa e remover acessos. Adicionar exige que a pessoa **já tenha conta**, informando o e-mail exato — não há busca parcial nem convite por e-mail no v1. Uma empresa nunca pode ficar sem Admin.
- **Permissão por empresa** ([ADR-0009](./adr/0009-rbac-dois-perfis.md)): a mesma pessoa pode ser Admin em uma empresa e apenas Usuário em outra.

| Perfil | Pode |
|---|---|
| **Admin** | Tudo: importar, cadastrar, editar e excluir registros, definir metas, gerenciar usuários da empresa |
| **Usuário** | Ler tudo — Painel geral, Registros, Metas e Histórico. Não altera nada e não vê a tela de Usuários |

## Módulo de Ingestão e Centralização de Dados

- Upload e mapeamento de colunas de planilhas (.xlsx, .csv, até 20 MB) — o arquivo é parseado no momento do upload; o arquivo bruto não é persistido, só os dados estruturados vão para o Postgres ([ADR-0010](./adr/0010-sem-storage-arquivo-bruto.md))
- Modelo de planilha padrão para download, já com as colunas esperadas — reduz erro de mapeamento na origem
- Validação linha a linha, com as **linhas não importadas** listadas por motivo:
  - **erro de formato ou conteúdo** (valor inválido, campo obrigatório vazio)
  - **unidade ou categoria inexistente** — a linha é rejeitada; a importação nunca cria cadastro novo a partir da planilha
  - **duplicata** — registro idêntico já existente na base da empresa; não é importado, mas fica registrado para revisão
- Relatório das linhas não importadas disponível para download
- Formulários de cadastro manual validados (data, valor, categoria, unidade de negócio, cliente, observações), com opção de salvar e adicionar outro em sequência
- Gateway de integração via API REST ou leitura direta de banco
- Histórico de importações com status, contagens e detalhamento das linhas rejeitadas
- Listagem completa dos dados centralizados, com busca, filtros por período, unidade e origem, paginação e exportação (CSV, Excel, PDF)
- Edição e exclusão de registro, exclusivas do Admin. A exclusão é **lógica** — o dado sai das telas e dos totais, mas continua rastreável ([data-model.md](./architecture/data-model.md))

## Módulo de Dashboards

- Painel com gráficos de linha, barra, pizza e cards de métricas
- Filtros por período, categoria e unidade de negócio
- Definição de metas de vendas por mês, categoria e unidade de negócio, comparadas ao realizado (real vs. meta). Unidade sem meta lançada entra como zero na comparação, e a tela avisa quantas estão nessa situação
- Exportação de relatórios em PDF e Excel
- Responsivo para desktop e tablet

## Funcionalidades adicionais sugeridas (a validar com o cliente)

Nenhuma destas está no piloto.

- Trilha de auditoria completa, campo a campo (hoje há apenas quem criou, quem alterou por último e quando)
- Reversão de uma importação inteira — precisa ser feita pelo lote no banco, não por reprocessamento do arquivo, que não é guardado ([ADR-0010](./adr/0010-sem-storage-arquivo-bruto.md))
- Notificações (e-mail ou webhook) em falhas de importação
- Camada de regras de qualidade de dados configurável (campo obrigatório, formato, unicidade) antes de aceitar um upload
- Convite por e-mail para adicionar usuários, no lugar do e-mail exato
- Telas de gestão de unidades de negócio e categorias (hoje são seed data por empresa)
