# 0015. Uma instância por cliente (por ora), com schema preparado para compartilhar

Data: 2026-08-14

## Status

Aceita

## Contexto

Com `organizations` no schema ([ADR-0014](./0014-escopo-por-empresa-organizations.md)), o sistema passa a poder atender várias empresas no mesmo banco. Isso não obriga a fazê-lo. Era preciso decidir **onde o produto roda** e **quantos clientes dividem uma instância** — e essas são duas perguntas diferentes que costumam ser confundidas com a de tenancy.

## Decisão

**Uma stack por cliente**, em VM na nuvem gerida pela empresa júnior, via Docker Compose ([ADR-0008](./0008-deploy-docker-compose-unificado.md)). Cada cliente tem seu próprio banco, seu próprio backup e seu próprio domínio.

On-premise no servidor do cliente continua possível — o artefato é o mesmo `docker compose up` — e passa a ser oferecido quando o cliente exigir por política. Não é o padrão.

Nada específico de cliente vive em código: banco, domínio, segredo do JWT, fuso e afins vêm de variável de ambiente. Uma imagem, N configurações. O deploy é roteirizado desde o primeiro cliente (`./deploy.sh <cliente>` lendo um `.env` por cliente), mesmo havendo só um.

## Alternativas consideradas

- **Instância compartilhada entre clientes (SaaS de verdade)**: mais barato por cliente e um deploy só para corrigir bug. Descartada por ora porque o isolamento passaria a depender inteiramente do código da aplicação, sem Row-Level Security ainda implementada ([ADR-0014](./0014-escopo-por-empresa-organizations.md)) — e um filtro esquecido viraria vazamento entre clientes. Também porque, com a EJ hospedando, um banco único concentraria os dados de todos os clientes num só lugar, agravando o ponto de LGPD.
- **On-premise como padrão**: entrega o dado ao cliente e tira a EJ do papel de operadora. Descartada como padrão porque, em PME, "servidor" costuma ser um desktop sem no-break, sem IP fixo e sem caminho para certificado — e quando quebra, o time não consegue acessar para consertar. Para um time em formação, sustentar isso é bem mais caro do que parece.
- **Deploy manual por cliente**: descartada explicitamente. Se subir o segundo cliente for um processo artesanal, a arquitetura fica presa por dor operacional, não por limitação técnica — e essa é a forma mais comum de ficar preso.

## Consequências

Isolamento perfeito entre clientes sem depender de disciplina de código: dois bancos diferentes não vazam um no outro. A conversa comercial fica simples ("seus dados ficam num banco só seu"), o backup é por cliente, e encerrar um contrato é entregar o dump e desligar a stack.

**Custo aceito:** N clientes significam N deploys por correção, N backups para monitorar, N certificados. Some ~R$ 40–80/mês de VM por cliente, que abaixo de um certo valor de contrato come a margem.

**Ponto de virada:** por volta de 10 a 20 clientes ativos, ou quando o custo fixo por cliente pesar no preço, a instância compartilhada passa a valer. Antes de chegar lá, Row-Level Security precisa existir — ver o gatilho no [ADR-0014](./0014-escopo-por-empresa-organizations.md).

**Item de contrato, não de código:** quem opera a VM e o backup depois que o piloto acabar e o time se formar. Se for a EJ, é obrigação recorrente que precisa estar orçada; se for a TI do cliente, precisa ser entregue por escrito com o procedimento de restore ([ADR-0016](./0016-backup-pgdump-onedrive.md)).
