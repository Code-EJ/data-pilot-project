# 0002. Front-end em Next.js, usado como SPA (sem camada BFF)

Data: 2026-08-07

## Status

Aceita

## Contexto

Precisamos de uma camada de UI para os dois módulos (ingestão e dashboards). A questão não é só qual framework usar, mas quanta responsabilidade de servidor colocar no front-end.

O time do piloto é formado por estudantes de computação do 2º ao 6º período, com pouca experiência de mercado. Isso torna o número de fronteiras do sistema (processos, linguagens, pontos de integração) um critério de decisão tão importante quanto a capacidade técnica de cada ferramenta: cada fronteira é um lugar onde o erro aparece em um serviço e a causa está em outro.

## Decisão

Usar Next.js (TypeScript) como front-end, operado **em modo SPA**: renderização no cliente e chamadas HTTP diretas à FastAPI.

Regras explícitas — restrições de código, não recomendações:

- Não usar Route Handlers (`app/api/**`) como camada de agregação ou repasse para a FastAPI
- Componentes que consomem dados de domínio são `"use client"`; não buscar dados de negócio em Server Components ou Server Actions
- Nenhum acesso a banco a partir do `/web` (ver [ADR-0004](./0004-banco-dados-postgresql.md))
- Nenhuma regra de negócio no `/web` — validação de formulário para dar feedback ao usuário, sim; decisão de negócio, não (ver [ADR-0003](./0003-backend-dominio-fastapi.md))

## Alternativas consideradas

- **Next.js com camada BFF** (Route Handlers agregando e repassando chamadas para a FastAPI): era o desenho inicial. Descartada porque, no escopo do piloto, o BFF não agregaria nada — seria repasse puro, adicionando um salto de rede, um terceiro lugar onde regra de negócio pode vazar e a distinção server/client, que é o conceito mais confuso do React moderno para quem está começando. Se aparecer um caso concreto de agregação (uma tela que precise de várias chamadas à API compostas no servidor, ou um segredo que não pode ir ao navegador), revisitar.
- **Vite + React**: modelo mental mais simples (roda só no navegador, sem split server/client, build mais rápido) e alinhado ao catálogo original, que dizia apenas "React". Descartada por pouco — usado como SPA, o Next entrega praticamente a mesma simplicidade, já traz roteamento e estrutura de pastas prontos, e tem mais valor de formação para o time.
- **Full TypeScript, com Node também no backend**: ver [ADR-0003](./0003-backend-dominio-fastapi.md).

## Consequências

O front-end tem um único modelo mental (React no navegador) e um único destino para dados (a FastAPI). Um problema de dado sempre tem um lugar só para ser investigado.

**Trade-off aceito:** parte do Next.js fica deliberadamente sem uso (SSR, Server Components, Route Handlers). Isso é um risco de disciplina — a ferramenta permite o que a decisão proíbe. As restrições acima precisam ser verificadas em code review; se o time começar a usar recursos de servidor "porque dá", a fronteira volta pela porta dos fundos.

Sem BFF, o navegador fala direto com a FastAPI: CORS precisa ser configurado explicitamente na API e o cookie de sessão precisa funcionar entre origens — ou os dois serviços ficam sob o mesmo domínio via proxy reverso (ver [ADR-0008](./0008-deploy-docker-compose-unificado.md)).
