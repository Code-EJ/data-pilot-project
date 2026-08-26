# 0016. Backup: `pg_dump` diário enviado ao OneDrive em pastas datadas

Data: 2026-08-14

## Status

Aceita

## Contexto

O banco é a **única cópia** dos dados do cliente: o arquivo de planilha enviado é descartado após o processamento ([ADR-0010](./0010-sem-storage-arquivo-bruto.md)). Perder o volume do Postgres significa perder tudo o que foi importado e cadastrado. Não havia nenhuma decisão de backup registrada, o que era o item mais grave em aberto antes de qualquer dado real entrar no sistema.

## Decisão

Um serviço adicional no Compose, com a imagem do Postgres, executando diariamente:

```
pg_dump | gzip  →  /backups/AAAA-MM-DDTHH-MM.sql.gz
rclone copy     →  onedrive:Backups/<cliente>/AAAA/MM/
```

Regras que fazem parte da decisão, não são detalhe de implementação:

- **Backup lógico (`pg_dump`), não cópia de volume.** Copiar o diretório `pgdata` com o banco no ar produz um arquivo corrompido que *parece* íntegro até a hora do restore, e amarra a cópia à versão major exata do Postgres. O dump é portátil, comprime bem e no volume do piloto ([ADR-0012](./0012-dimensionamento-postgresql-piloto.md)) fica na casa de poucos MB por dia.
- **O processo nunca apaga nem sobrescreve no destino.** Sempre escreve em pasta nova datada. Isso transforma um destino sincronizado em algo efetivamente append-only, o que é o que impede um `rm` acidental (ou um ransomware no host) de propagar para a nuvem.
- **Data em formato ISO com fuso definido** (`AAAA-MM-DDTHH-MM`, horário de São Paulo), senão a pasta não ordena e dois arquivos "de 14/08" acabam sendo de horas diferentes.
- **Rotação:** 7 diários, 4 semanais, 12 mensais. Sem isso o destino enche e o backup passa a falhar em silêncio — que é pior do que não ter, porque todo mundo acha que tem.
- **O job registra sucesso ou falha em local que alguém olha.** Backup que quebra sem avisar só é descoberto no dia do desastre.
- **Procedimento de restore escrito e executado ao menos uma vez**, com dado falso, ainda durante o piloto: baixar o `.sql.gz`, restaurar em container limpo, conferir que os dados estão lá. **Enquanto ninguém tiver feito isso, o que existe é um script, não um backup.**
- **Destino:** OneDrive da empresa júnior no piloto, via `rclone` com usuário de serviço — não a conta pessoal de um membro, que some quando a pessoa sai. O dump vai criptografado (`age` ou `gpg` simétrico), porque contém dados de negócio do cliente e possivelmente pessoais (`sales_records.client_name`).

## Alternativas consideradas

- **Snapshot do volume Docker**: descartado pelos motivos de consistência e portabilidade acima. Exigiria parar o container a cada backup.
- **OneDrive do cliente em vez do da EJ**: tecnicamente melhor — o dado dele fica com ele, e a EJ deixa de ser depositária. Descartada **no piloto** por depender de credencial no tenant do cliente, mas **deve ser oferecida** como opção comercial; resolve boa parte da exposição de LGPD da EJ.
- **Bucket S3/B2 gerenciado**: mais adequado para backup (versionamento, object lock, ciclo de vida nativo), mas adiciona custo recorrente e mais uma conta a administrar. Revisitar se o número de clientes crescer.
- **Sem backup, contando com a reimportação das planilhas do cliente**: é o plano de última instância e continua valendo (o cliente ainda tem as planilhas originais dele), mas não cobre o que foi cadastrado manualmente nem as metas.

## Consequências

Recuperação possível com perda máxima de um dia de trabalho, a custo praticamente zero, sem depender da ferramenta de deploy — o container de backup funciona independente de como o deploy vier a ser feito.

**Trade-offs aceitos:**

- Perda de até 24 h entre dumps. Aceitável para um cliente que importa planilha algumas vezes por semana, mas **precisa estar dito para o cliente**, não assumido.
- Combinado com o [ADR-0010](./0010-sem-storage-arquivo-bruto.md), um desastre entre dumps perde tanto os dados quanto os arquivos do dia. O caminho de recuperação é restaurar o último dump e reimportar as planilhas do dia — que continuam com o cliente. É uma resposta legítima, e é melhor tê-la escrita do que descobri-la sob pressão.
- Guardar o dump no ambiente da EJ a torna operadora dos dados do cliente perante a LGPD. Isso precisa estar no contrato, junto com a chave de criptografia e o responsável pelo restore.

**Ponto a revisitar:** quem opera e monitora isso depois que o piloto acabar ([ADR-0015](./0015-uma-instancia-por-cliente.md)).
