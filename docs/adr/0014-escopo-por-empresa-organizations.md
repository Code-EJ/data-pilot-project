# 0014. Escopo por empresa: `organizations` como camada de isolamento

Data: 2026-08-14

## Status

Aceita

## Contexto

Até aqui o sistema assumia **single-tenant**: uma instância atendia um cliente, e nenhuma tabela tinha noção de "a quem este dado pertence". Essa premissa estava registrada apenas como nota em [data-model.md](../architecture/data-model.md), nunca como decisão.

Ao desenhar as telas de identidade do protótipo, ficou claro que o produto precisa de outra coisa: uma pessoa tem **uma conta única** na plataforma, pode estar vinculada a **mais de uma empresa**, e o que ela pode fazer **varia conforme a empresa** em que está trabalhando. Isso não cabe no modelo anterior.

Era preciso decidir se isso significa virar um SaaS multi-inquilino agora, ou apenas introduzir uma camada de escopo que deixe essa porta aberta sem obrigar a atravessá-la.

## Decisão

Introduzir `organizations` como **a unidade de escopo de todo dado do sistema**, e `memberships` como o vínculo entre pessoa e empresa, carregando o papel de acesso.

Três regras derivam disso e valem como restrição de implementação:

1. **Toda tabela de negócio tem `organization_id`.** Sem exceção, inclusive as que poderiam derivar a empresa por uma FK (ex: `import_errors` poderia chegar nela via `import_batches`). A coluna redundante existe porque é ela que uma política de Row-Level Security consegue usar diretamente — sem ela, o dia em que RLS for necessária, a migração é bem mais cara.
2. **Toda consulta de dado de negócio filtra por `organization_id`.** A empresa ativa vem da sessão, nunca de parâmetro enviado pelo cliente.
3. **Toda constraint de unicidade que era global vira única por empresa.** `business_units.name`, `product_categories.name` e a chave de `sales_goals` são únicas *dentro de uma empresa* — duas empresas podem ter, ambas, uma unidade chamada "Loja Centro". A exceção é `users.email`, que continua único globalmente: a conta é da pessoa, não da empresa.

O papel de acesso sai de `users` e passa a viver em `memberships` (ver [ADR-0009](./0009-rbac-dois-perfis.md)).

## Alternativas consideradas

- **Manter single-tenant, com uma instância por cliente e sem `organization_id`**: era o desenho anterior e continua sendo o mais simples e o mais seguro — o isolamento é garantido pelo banco ser outro, não por disciplina de código. Descartada porque não atende o requisito de produto: uma pessoa com uma conta só, vinculada a várias empresas com papéis diferentes, é impossível de representar sem essa camada.
- **Multi-tenant com Row-Level Security desde já**: é o desenho mais correto para uma instância compartilhada, porque move o isolamento para o banco e torna o filtro esquecido inofensivo. Descartada **por ora**, não por mérito: RLS é um conceito que ninguém do time viu, e enquanto cada cliente tiver a própria instância ([ADR-0015](./0015-uma-instancia-por-cliente.md)) o risco que ela cobre não existe. Ver "Consequências" para o gatilho de reversão.
- **Schema por empresa** (um schema Postgres por organização): isolamento forte sem RLS, mas migrations passam a ter que rodar N vezes e o número de schemas cresce sem controle. Desproporcional ao problema.

## Consequências

O produto ganha a estrutura de identidade que as telas exigem, e a decisão de deploy fica desacoplada do modelo de dados: o mesmo schema funciona com uma instância por cliente ou com uma instância compartilhada, e a escolha pode mudar sem migração.

**Trade-off aceito, e é o mais importante deste ADR:** o isolamento entre empresas passa a depender do código da aplicação. Enquanto cada cliente tiver a própria instância, um filtro esquecido mostra dados de outra empresa *do mesmo cliente* — constrangedor, mas contornável. No dia em que duas empresas de donos diferentes dividirem o mesmo banco, o mesmo bug vira vazamento de dado entre clientes, silencioso e grave.

**Gatilho explícito:** antes de colocar duas empresas de clientes distintos na mesma instância, Row-Level Security deixa de ser opcional. Isso deve virar um ADR próprio, não uma tarefa solta.

Como contrapeso barato, desde já: as consultas de dado de negócio ficam concentradas em uma camada de repositório, não espalhadas pelos handlers. Se um dia entrar um filtro obrigatório de empresa, existe um lugar só para colocá-lo (ver [CONTRIBUTING.md](../../CONTRIBUTING.md)).
