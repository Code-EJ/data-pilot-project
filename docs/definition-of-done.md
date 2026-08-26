# Definition of Done

O que significa um card estar **pronto**. Existe porque, sem isso escrito, cada pessoa fecha o card em um estado diferente e a dívida aparece toda junta na última semana.

Vale para todo card. Se algum item não se aplica, marque como N/A no PR em vez de ignorar.

---

## Todo card

- [ ] Faz o que o card descreve, e o **critério de aceite do card** foi verificado — por quem fez, antes do review
- [ ] Roda em ambiente limpo: `docker compose down -v && docker compose up` e a funcionalidade funciona, sem passo manual não documentado
- [ ] Passou na CI (lint, typecheck, testes) — ver [ADR-0017](./adr/0017-testes-e-ci.md)
- [ ] Revisado e aprovado por **uma outra pessoa** do time
- [ ] Commit descreve o porquê, não só o quê

## Card que mexe na API

- [ ] Rota, verbo, códigos de resposta e formato de erro seguem [api-contract.md](./api-contract.md) — divergência precisa estar justificada no PR
- [ ] **A consulta filtra por `organization_id` e por `deleted_at is null`**
- [ ] A empresa vem da sessão, nunca de parâmetro enviado pelo cliente
- [ ] Permissão verificada no servidor, não só escondida na UI ([ADR-0009](./adr/0009-rbac-dois-perfis.md))
- [ ] Teste de autorização: sem vínculo → `404`; perfil `usuario` em rota de escrita → `403`; recurso de outra empresa → `404`
- [ ] Se mudou schema, tem migration do Alembic no mesmo PR, e ela sobe **e desce**
- [ ] Se mudou o contrato, o client TypeScript foi regerado

## Card que mexe no front

- [ ] Confere com o [protótipo](./prototype/index.html): campos, rótulos, chips e mensagens
- [ ] Os quatro estados existem: **carregando, vazio, erro e com dados** — o estado vazio com texto útil, não uma tabela em branco
- [ ] Testado **nos dois perfis**, Admin e Usuário
- [ ] Nenhuma regra de negócio nova no `/web` ([ADR-0002](./adr/0002-frontend-nextjs-spa.md))
- [ ] Nenhum número calculado no front — agregação vem pronta da API ([metrics.md](./metrics.md))
- [ ] Funciona em tablet (o escopo pede desktop e tablet)

## Card que mexe em ingestão ou métrica

- [ ] Segue [import-spec.md](./import-spec.md) ou [metrics.md](./metrics.md), conforme o caso
- [ ] Os casos de teste listados nesses documentos estão cobertos
- [ ] Em ingestão: o invariante `total = valid + error + duplicate` é verificado por teste

## Card que toma uma decisão técnica

- [ ] Existe ADR nova, ou o ponto foi levado ao time antes de decidir sozinho
- [ ] Se resolveu um item de "Pontos em aberto" do [overview](./architecture/overview.md), o item saiu de lá

---

## Não conta como pronto

- "Funciona na minha máquina" sem subir do zero
- Card fechado com `TODO` no código, sem card de follow-up criado
- Teste comentado ou marcado como `skip` para a CI passar
- Documentação que virou mentira: se o comportamento mudou e o doc não, o card não está pronto

---

## Sobre pedir ajuda

Meio dia travado sem avisar é o limite. Chamar alguém não conta contra você em nenhum critério deste documento — e é o que impede que um problema de dez minutos vire uma semana.
