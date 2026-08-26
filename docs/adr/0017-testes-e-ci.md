# 0017. Testes onde o erro é caro, e CI mínima no PR

Data: 2026-08-14

## Status

Aceita

## Contexto

Não havia nenhuma decisão registrada sobre testes ou integração contínua. Com um time em formação e rotação a cada semestre, o custo de não ter é maior do que o normal: ninguém que entra depois consegue mexer com segurança em código que não avisa quando quebra.

Ao mesmo tempo, exigir cobertura ampla de um time que está aprendendo a programar produz teste ritual — código que existe para satisfazer uma métrica e não pega defeito nenhum.

## Decisão

**Testar onde o erro é caro e silencioso; não testar o que quebra alto.**

Três áreas têm teste obrigatório, e um PR que as toque sem teste não é aprovado:

1. **Autorização e escopo por empresa.** Para cada endpoint: um usuário sem vínculo recebe `404`; um `usuario` recebe `403` nas rotas de escrita; um recurso de outra empresa nunca aparece. É o defeito que não dá erro na tela — só mostra o dado errado para a pessoa errada ([ADR-0014](./0014-escopo-por-empresa-organizations.md)).
2. **Parsing e validação de planilha.** Os casos listados em [import-spec.md](../import-spec.md), seção 7. Um bug aqui grava número errado no banco sem levantar exceção nenhuma.
3. **Métricas.** As invariantes de [metrics.md](../metrics.md): soma das partes fecha com o total, exportação bate com o card, registro excluído e registro de outra empresa não entram.

Fora disso, teste é bem-vindo mas não exigido. CRUD trivial não precisa.

**Ferramentas:** `pytest` + `httpx` na `/api`, contra um Postgres real subido pelo Compose — não SQLite, porque metade do que estamos testando (constraints, `numeric`, filtros parciais) se comporta diferente.

**No `/web`:** sem testes unitários no v1. Apenas `tsc --noEmit` e ESLint. A lógica de negócio está toda na API por decisão ([ADR-0003](./0003-backend-dominio-fastapi.md)); testar componente de apresentação seria testar o protótipo.

**CI:** GitHub Actions em todo PR, rodando lint e typecheck do `/web`, lint e `pytest` da `/api`. Falhou, não mergeia. Sem deploy automático.

## Alternativas consideradas

- **Sem testes no piloto**: entregaria mais rápido nas primeiras semanas. Descartada porque os três defeitos acima são exatamente os que não aparecem em teste manual — todos produzem uma tela que parece certa.
- **Meta de cobertura (ex: 70%)**: fácil de medir e fácil de enganar. Um time aprendendo persegue a porcentagem escrevendo testes de getter, e a autorização segue sem cobertura. Descartada em favor de exigir teste em três áreas nomeadas.
- **Testes E2E com Playwright**: pegariam regressão de fluxo inteiro. Descartada no v1 por custo de manutenção e por serem lentos e instáveis nas mãos de quem nunca escreveu um. Revisitar depois do piloto, começando por um único smoke test do fluxo login → escolher empresa → importar.
- **CI com deploy automático**: prematuro antes de existir um ambiente de homologação.

## Consequências

O time aprende a escrever teste nos lugares em que teste realmente paga, em vez de aprender a preencher métrica. A CI dá um retorno objetivo em cada PR, o que reduz o número de discussões de review sobre coisa mecânica.

**Trade-offs aceitos:**

- Áreas sem teste obrigatório vão ter regressão eventualmente. É aceitável porque são as áreas em que a regressão aparece na primeira vez que alguém abre a tela.
- Rodar contra Postgres real deixa a suíte mais lenta que com banco em memória. No volume do piloto, segundos — e evita a classe de bug "passou no teste e quebrou em produção".
- Exigir Docker para rodar a suíte local adiciona um passo ao onboarding. Como o ambiente já sobe por Compose ([ADR-0008](./0008-deploy-docker-compose-unificado.md)), o passo já existia.

**Ponto a revisitar:** se a suíte passar de uns dois minutos, separar em rápida (roda sempre) e lenta (roda no merge).
