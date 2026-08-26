# 0009. RBAC com dois perfis, definidos por empresa

Data: 2026-08-07 · revisado em 2026-08-14 (escopo por empresa)

## Status

Aceita

## Contexto

O sistema precisa de controle de acesso desde o início — nem todo usuário deve poder importar, cadastrar dados ou gerenciar quem tem acesso. O público (gerentes e diretores de PMEs) sugere um caso de uso simples.

Com a introdução de `organizations` ([ADR-0014](./0014-escopo-por-empresa-organizations.md)), a pergunta ganhou uma dimensão: o papel é da pessoa ou do vínculo dela com uma empresa? O protótipo respondeu — a mesma pessoa pode ser Admin numa empresa e apenas Usuário em outra.

## Decisão

Dois perfis, atribuídos **por empresa** e armazenados em `memberships`, não em `users`:

| Perfil | Permissões dentro daquela empresa |
|---|---|
| **Admin** | Lê tudo e escreve: importa planilhas, cadastra e edita registros, define metas, adiciona e remove usuários da empresa |
| **Usuário** | Lê tudo — Painel geral, Registros, Metas e Histórico — e não altera nada |

Regras que acompanham a decisão:

- O perfil é resolvido a cada requisição a partir de `memberships`, não carregado no token ([ADR-0006](./0006-autenticacao-jwt-fastapi.md)).
- **Usuário lê tudo.** As telas de escrita (Cadastro manual, Ingestão) e a de gestão de usuários não aparecem para ele; Metas aparece em modo somente leitura.
- Uma empresa **não pode ficar sem Admin**: remover ou rebaixar o último Admin é bloqueado.
- Só quem já é Admin de alguma empresa pode cadastrar uma nova empresa, e vira Admin dela automaticamente. O primeiro Admin do sistema é criado por script de seed — sem isso não haveria ponto de partida.
- Adicionar alguém a uma empresa exige que a pessoa **já tenha conta**, informando o e-mail exato. Não há busca parcial nem convite por e-mail no v1.

## Alternativas consideradas

- **Papel único por pessoa, global** (o desenho anterior, com `users.role`): mais simples, mas incompatível com o requisito de a mesma conta ter acessos diferentes em empresas diferentes.
- **3 perfis (Admin, Editor, Leitor)**: separaria quem importa dados de quem administra o acesso. Descartada por ora para não modelar uma distinção sem caso de uso validado — mas é a evolução natural, e a estrutura de `memberships` já a comporta sem migração estrutural.
- **RBAC granular por ação** (`import:create`, `dashboard:export`, `user:manage`): mais flexível, exige modelagem e uma UI de permissões. Desproporcional ao escopo atual.
- **Convite por e-mail em vez de e-mail exato**: fluxo mais natural para o usuário final. Descartado no v1 por exigir e-mail transacional e um fluxo de aceite — mais superfície do que o piloto comporta. Fica registrado como a melhoria mais provável desta tela.

## Consequências

Modelo simples de entender e implementar, e que já suporta o caso real de uma pessoa atuando em várias empresas com papéis distintos.

**Trade-offs aceitos:**

- Não existe perfil intermediário (alguém que importa mas não gerencia acesso). Se surgir, é adicionar um valor ao `check` de `memberships.role` e ajustar as regras.
- Exigir o e-mail exato é pouco amigável e obriga o admin a saber de antemão qual conta a pessoa criou. Em compensação, evita expor uma busca que permitiria enumerar quem tem conta na plataforma. As mensagens de erro não devem revelar se um e-mail existe fora do contexto de uma tentativa legítima de vínculo.

Como o navegador fala direto com a API ([ADR-0002](./0002-frontend-nextjs-spa.md)), **esconder um botão não é controle de acesso**. Toda regra desta tabela precisa ser verificada no servidor, em cada endpoint.
