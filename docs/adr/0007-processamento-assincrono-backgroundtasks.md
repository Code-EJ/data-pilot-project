# 0007. Processamento assíncrono de importações via BackgroundTasks (sem fila dedicada)

Data: 2026-08-07

## Status

Aceita

## Contexto

Parsing e validação de planilhas não podem travar a resposta HTTP nem a UI. A pergunta é qual mecanismo de execução em segundo plano usar, dado o volume esperado: milhares a poucas centenas de milhares de linhas no total, com até dezenas de milhares de linhas por importação (ver [ADR-0012](./0012-dimensionamento-postgresql-piloto.md)).

## Decisão

Usar `BackgroundTasks`, do próprio FastAPI. O fluxo é:

1. A requisição de upload cria o `import_batch` com `status = 'processing'` e devolve o id imediatamente
2. O processamento (Pandas → validação → inserção em lote no Postgres) roda em segundo plano, no mesmo processo da API
3. A tela de Ingestão consulta o batch por polling até o status mudar

Não há fila, broker nem processo worker separado no v1.

## Alternativas consideradas

- **RQ + Redis, com worker em processo separado**: era o desenho inicial. Descartada por desproporção ao volume — nessa escala o processamento leva segundos, não minutos. O custo é concreto: mais um container, mais um serviço no compose e três conceitos novos (fila, job, estado e retry de job) para um time em formação. Volta a fazer sentido quando houver medição mostrando importações longas o bastante para justificar, ou necessidade real de retry automático e agendamento.
- **Celery + Redis**: mais robusto (múltiplas filas, retries sofisticados, agendamento via Beat, monitoramento com Flower). Descartada pelos mesmos motivos, com peso maior. É a opção certa se e quando a fila voltar a ser necessária **e** o RQ se mostrar insuficiente.
- **Processamento síncrono dentro da própria requisição**: mais simples ainda, mas com dezenas de milhares de linhas o request pode estourar o timeout do proxy e a tela ficaria parada sem feedback. Descartada.

## Consequências

Um container a menos, um deployable a menos e nenhum conceito de fila para aprender. O caminho de ingestão inteiro cabe em um arquivo Python legível de ponta a ponta.

**Trade-offs aceitos:**

- Uma importação em andamento morre se o processo da API reiniciar (deploy, crash), deixando o `import_batch` preso em `'processing'`. Isso exige tratamento explícito: na subida da API, marcar como `'failed'` todo batch em `'processing'` há mais de N minutos.
- O processamento compete por CPU com o atendimento de requisições no mesmo processo. Aceitável no volume do piloto — e é justamente o sintoma que indica quando chegou a hora de reintroduzir a fila.
- Sem retry automático: um erro de processamento exige reenviar o arquivo, que não fica guardado (ver [ADR-0010](./0010-sem-storage-arquivo-bruto.md)).

Migrar para RQ ou Celery depois é uma mudança isolada: a função de processamento já existe e passa a ser enfileirada em vez de chamada diretamente.
