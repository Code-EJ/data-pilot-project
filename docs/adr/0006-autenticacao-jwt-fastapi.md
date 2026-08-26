# 0006. Autenticação e sessão inteiramente na FastAPI

Data: 2026-08-07 · revisado em 2026-08-14 (permissão por empresa)

## Status

Aceita

## Contexto

O sistema precisa de login, sessão e um papel de RBAC ([ADR-0009](./0009-rbac-dois-perfis.md)). A decisão é **onde** essa responsabilidade mora: sendo `/web` e `/api` processos e linguagens diferentes, qualquer divisão obriga os dois lados a concordarem sobre formato, assinatura e validação do token.

Com `organizations` ([ADR-0014](./0014-escopo-por-empresa-organizations.md)), surgiu uma segunda pergunta: o token carrega o papel do usuário? Ele não pode — o papel varia conforme a empresa em que a pessoa está trabalhando.

## Decisão

Autenticação 100% na FastAPI:

- `POST /auth/register` cria a conta (nome, e-mail, senha). A conta é da pessoa e não pertence a nenhuma empresa.
- `POST /auth/login` valida e-mail e senha contra `users.password_hash` (bcrypt via passlib).
- A API emite um JWT assinado em HS256, com o segredo em variável de ambiente. O token contém **apenas `sub`** (id do usuário) — sem papel, sem empresa.
- O token vai ao navegador em cookie `httpOnly`, `Secure`, `SameSite=Lax`.
- `GET /auth/me` devolve os dados da pessoa e a lista de empresas em que ela tem vínculo, com o papel em cada uma. É o que alimenta a tela "Suas empresas".
- A empresa ativa viaja em cada requisição (header `X-Organization-Id` ou segmento de rota). **A API sempre valida que existe `membership` do usuário naquela empresa** e resolve o papel dali — o valor enviado pelo cliente é uma afirmação a verificar, nunca uma autorização.
- Expiração curta (8 h) e **sem refresh token** no v1.

## Alternativas consideradas

- **NextAuth/Auth.js emitindo um JWT validado pela FastAPI**: era o desenho inicial. Descartada por dois motivos. Primeiro, o token de sessão do Auth.js v5 é, por padrão, um JWE criptografado pensado para ser lido pelo próprio Next — não um JWT assinado que um serviço em outra linguagem valide. Fazer as duas pontas concordarem exige configuração não-óbvia, e o sintoma do erro é um `401` sem explicação: a pior forma possível de travar alguém sem experiência. Segundo, dividiria a identidade do usuário entre dois serviços, e a resposta para "onde eu mudo isso?" deixaria de ser única.
- **Carregar `organization_id` e `role` no token, reemitindo-o a cada troca de empresa**: evita uma consulta por requisição. Descartada — o papel passaria a ter estado congelado no token, de modo que rebaixar ou remover alguém só teria efeito quando a sessão expirasse (até 8 h depois). Consultar `memberships` a cada requisição é uma leitura indexada barata e torna a revogação imediata.
- **JWT 100% custom, incluindo hashing próprio**: descartada — hash de senha e emissão de token são área onde não se improvisa. Vale notar que a decisão acima **não** é escrever isso do zero: passlib/bcrypt e o suporte a OAuth2/JWT do próprio FastAPI são bibliotecas maduras. O que muda em relação ao desenho inicial é apenas qual serviço as hospeda.
- **Sessão em banco (cookie opaco + tabela `sessions`)**: mais simples de revogar. Descartada por pouco: com 8 h de expiração e a permissão já sendo resolvida por requisição, o JWT cobre o caso sem consulta extra de sessão.

## Consequências

Um único serviço entende usuário, senha e permissão — o mesmo que já é dono das regras de negócio ([ADR-0003](./0003-backend-dominio-fastapi.md)). Para depurar um problema de acesso há um lugar só para olhar.

Resolver a permissão por requisição tem um efeito colateral bom: remover alguém de uma empresa vale na requisição seguinte, sem esperar a sessão expirar.

**Trade-offs aceitos:**

- Uma consulta a `memberships` por requisição autenticada. É uma leitura por índice único `(organization_id, user_id)`; irrelevante no volume do piloto.
- Sem refresh token, a sessão expira de forma abrupta e o usuário refaz o login.
- Um token roubado continua válido até expirar, mesmo com a conta desativada. Aceitável na janela de 8 h; é o primeiro item a rever se aparecer requisito de desconectar alguém imediatamente.

Como o navegador fala direto com a API ([ADR-0002](./0002-frontend-nextjs-spa.md)), o cookie precisa atravessar origens. Servir `/web` e `/api` sob o mesmo domínio via proxy reverso ([ADR-0008](./0008-deploy-docker-compose-unificado.md)) evita ter que configurar `SameSite=None` e CORS com credenciais — é o caminho recomendado.

**Fora de escopo no v1:** verificação de e-mail no cadastro, recuperação de senha e 2FA. Como só quem já é Admin de alguma empresa pode criar empresa ([ADR-0009](./0009-rbac-dois-perfis.md)), uma conta não verificada não consegue fazer nada sozinha — o que torna a ausência de verificação tolerável, mas não indefinidamente.
