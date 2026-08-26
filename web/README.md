# web

Front-end em Next.js (TypeScript), operado **em modo SPA**. Ver [ADR-0002](../docs/adr/0002-frontend-nextjs-spa.md).

Responsabilidades:

- UI dos módulos de identidade, ingestão e dashboards — o protótipo de referência está em [`docs/prototype/index.html`](../docs/prototype/index.html)
- Fluxo de entrada: login → tela "Suas empresas" → aplicação dentro da empresa escolhida
- Envia a empresa ativa em cada requisição; a API é quem confirma o vínculo e resolve o perfil ([ADR-0006](../docs/adr/0006-autenticacao-jwt-fastapi.md))
- Chamadas diretas à `/api` pelo client TS gerado do OpenAPI ([ADR-0005](../docs/adr/0005-comunicacao-rest-openapi.md))
- Exibe ou esconde elementos conforme o perfil retornado pela API — conveniência de UI, **nunca** garantia de segurança ([ADR-0009](../docs/adr/0009-rbac-dois-perfis.md))

Não faz parte deste projeto:

- Route Handlers (`app/api/**`) como camada de agregação ou repasse
- Busca de dados de domínio em Server Components ou Server Actions
- Qualquer acesso a banco ou ORM
- Regra de negócio (validação de formulário para feedback ao usuário é permitida; decisão de negócio não)

Ainda não inicializado — próximo passo é rodar `create-next-app` aqui.
