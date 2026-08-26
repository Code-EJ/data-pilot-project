# 0010. Sem storage de arquivo bruto na ingestão (v1)

Data: 2026-08-07

## Status

Aceita

## Contexto

O desenho original (P-02) previa guardar as planilhas enviadas em um storage de objetos (S3-compatible/MinIO), além do banco. Ao revisar o fluxo de ingestão, definiu-se que o objetivo real é transformar a planilha em dados estruturados, não preservar o arquivo em si.

## Decisão

O arquivo de planilha enviado **não é persistido** em nenhum storage. O fluxo é: upload → parse/serialização (Pandas) → validação → gravação direta dos dados estruturados no PostgreSQL. O arquivo original é descartado após o processamento.

## Alternativas consideradas

- **MinIO self-hosted**: rodaria junto no Docker Compose, API S3-compatível, zero custo de nuvem. Descartada por ora porque o caso de uso não exige guardar o arquivo original, só os dados que ele contém.
- **S3 gerenciado**: sem preocupação com backup/durabilidade, mas adiciona custo recorrente e dependência de conta cloud — descartada pelo mesmo motivo acima, e por ser prematura antes de uma decisão de infra fechada com o cliente.

## Consequências

Simplifica o fluxo de ingestão (uma etapa a menos) e reduz custo/infra. **Trade-off aceito:** não há como reprocessar ou auditar o arquivo original em caso de erro de parsing não previsto — só o que já foi estruturado e gravado fica rastreável (via log de importação / import batch id). A funcionalidade de "reverter uma importação problemática" (ver [docs/product-scope.md](../product-scope.md)) precisa ser implementada em cima do lote de importação no banco, não via reprocessamento do arquivo. Se isso se mostrar insuficiente, adicionar storage de arquivo bruto depois é uma mudança incremental, não exige redesenho.

> **Nota (2026-08-14):** como o arquivo bruto não é guardado, o banco passa a ser a única cópia dos dados do cliente. Isso é o que torna o [ADR-0016](./0016-backup-pgdump-onedrive.md) obrigatório, e não opcional. O plano de recuperação de última instância é restaurar o último dump e reimportar as planilhas do dia — que continuam de posse do cliente.
