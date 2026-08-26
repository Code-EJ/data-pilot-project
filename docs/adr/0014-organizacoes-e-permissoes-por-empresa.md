# 0014. Organizações como escopo de dados e permissões

Data: 2026-08-14

## Status

Aceita

## Contexto

O produto precisa permitir que uma conta participe de uma ou mais empresas, escolha a empresa ativa depois do login e tenha um perfil diferente em cada uma. A mesma base de código também deve servir a instalações com apenas uma empresa, como um deploy on-premise, sem fechar antecipadamente a decisão de hospedagem.

## Decisão

Modelar empresas como `organizations` e a relação N–N com contas como `organization_memberships (user_id, organization_id, role)`.

- A conta em `users` é global e não possui `role`.
- O papel `admin` ou `usuario` pertence ao vínculo com a organização.
- Toda tabela de negócio possui `organization_id` ou herda o escopo por uma relação obrigatória.
- Toda operação da API valida que o usuário é membro da organização ativa.
- FKs compostas com `organization_id` impedem referências cruzadas entre empresas.
- A primeira organização e seu primeiro vínculo Admin são criados por script de bootstrap da implantação.
- Depois do bootstrap, somente quem já é Admin de pelo menos uma organização pode criar outra; o criador vira Admin da nova organização na mesma transação.
- O último Admin de uma organização não pode ser removido nem rebaixado.
- Somente Admins acessam a gestão de membros; uma conta precisa estar com o e-mail verificado antes de receber vínculo.
- A tela de seleção de organização é sempre exibida depois do login, inclusive quando existe apenas um vínculo.

## Alternativas consideradas

- **Uma stack e um banco por empresa, sem `organization_id`:** isolamento operacional mais forte e modelo mais simples, mas impede contas com acesso a várias empresas na mesma instalação e acopla o produto à estratégia de deploy antes de ela ser definida.
- **Perfil global em `users`:** descartado porque a mesma pessoa pode ter permissões diferentes em empresas distintas.
- **Schema ou banco separado por organização dentro da mesma instalação:** aumenta o custo de provisionamento, migrations e consultas consolidadas sem necessidade comprovada no piloto.

## Consequências

O mesmo código suporta uma organização on-premise ou várias organizações em um ambiente compartilhado. Em contrapartida, o isolamento passa a ser uma propriedade que precisa ser preservada em toda consulta e testada explicitamente.

O JWT identifica a conta, mas não é fonte definitiva do papel. A autorização consulta `organization_memberships`, permitindo que remoções e mudanças de perfil tenham efeito imediato.

O escopo adiciona `organization_id` às tabelas de negócio, muda unicidades globais para unicidades por organização e exige testes negativos que comprovem que um membro da organização A não acessa identificadores da organização B.
