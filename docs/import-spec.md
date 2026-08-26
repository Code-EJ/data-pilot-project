# Especificação de ingestão de planilha

Regras de leitura, conversão e validação de arquivos importados. É o documento que torna o módulo de ingestão implementável e revisável: sem ele, cada pessoa inventa a própria regra para `1.204,50` e o PR não tem como ser avaliado.

Complementa o [contrato da API](./api-contract.md) (área 7) e o [modelo de dados](./architecture/data-model.md).

> **Status: proposta.** Derivada do protótipo e da realidade de planilhas brasileiras, não validada com o cliente. Os pontos marcados **[a validar]** são escolhas minhas onde havia mais de uma resposta defensável.

---

## 1. Arquivo

| Regra | Valor |
|---|---|
| Formatos aceitos | `.xlsx`, `.csv` |
| Tamanho máximo | 20 MB |
| Linhas máximas | 50 000 (acima disso, `422` pedindo para dividir o arquivo) |
| Aba lida (xlsx) | a **primeira**, sempre — **[a validar]**: escolher aba tornaria o passo 1 do fluxo mais complexo sem caso de uso conhecido |
| Cabeçalho | primeira linha não vazia do arquivo |

### Encoding (só CSV)

Tentar nesta ordem e parar na primeira que decodificar o arquivo inteiro:

1. `utf-8-sig` (cobre UTF-8 com e sem BOM)
2. `cp1252` (é o que o Excel brasileiro gera ao "Salvar como CSV")

Se nenhuma funcionar, rejeitar o arquivo inteiro com mensagem clara. **Não** usar detecção estatística de encoding: em arquivos pequenos ela erra, e um erro aqui corrompe acentos silenciosamente em vez de falhar.

### Delimitador (só CSV)

Contar `;` e `,` na linha de cabeçalho. Vence o mais frequente; empate ou zero ocorrências de ambos → `;`.

O padrão brasileiro é `;`, justamente porque a vírgula é separador decimal. Assumir `,` como no resto do mundo é a causa número um de "importei e veio tudo numa coluna só".

---

## 2. Planilha modelo

Arquivo estático servido por `GET /imports/template`. Colunas, nesta ordem:

| Coluna | Obrigatória | Exemplo |
|---|---|---|
| `Data` | sim | `05/08/2026` |
| `Valor` | sim | `1.204,50` |
| `Categoria` | sim | `Eletrônicos` |
| `Unidade de Negócio` | sim | `Loja Centro` |
| `Cliente` | não | `Fernanda Lima` |
| `Observações` | não | `Venda balcão` |

Mesma ordem e mesmos nomes dos campos do Cadastro manual — é o que faz o mapeamento automático acertar sem intervenção quando o cliente usa o modelo.

---

## 3. Mapeamento de colunas

O passo 2 do fluxo sugere um mapeamento e o usuário confirma ou corrige.

**Normalização para comparar:** minúsculas, sem acentos, sem espaços nas pontas, espaços internos colapsados em um só.

**Sinônimos aceitos** (após normalização):

| Campo | Aceita também |
|---|---|
| `Data` | `data da venda`, `dt`, `dt venda`, `data venda`, `emissao` |
| `Valor` | `valor total`, `total`, `vlr`, `preco`, `receita` |
| `Categoria` | `categoria do produto`, `cat`, `produto`, `linha` |
| `Unidade de Negócio` | `unidade`, `filial`, `loja`, `un`, `centro de custo` |
| `Cliente` | `nome do cliente`, `razao social`, `nome`, `comprador` |
| `Observações` | `obs`, `observacao`, `descricao`, `notas` |

Coluna do arquivo que não casar com nada fica **não mapeada** e é ignorada — não é erro. Campo obrigatório sem nenhuma coluna mapeada bloqueia o avanço do passo 2, com mensagem dizendo qual campo falta.

---

## 4. Conversão por campo

### Data

Formatos aceitos, nesta ordem de tentativa:

1. `dd/mm/aaaa` e `dd-mm-aaaa`
2. `aaaa-mm-dd` (ISO)
3. `dd/mm/aa` — ano de dois dígitos: `00–49` → `20xx`, `50–99` → `19xx`
4. Data nativa do Excel (`.xlsx` costuma trazer a célula já como data; usar o valor, não o texto)
5. Serial numérico do Excel (número inteiro entre 1 e 60 000, contado a partir de 30/12/1899)

**Nunca interpretar como `mm/dd/aaaa`.** `03/04/2026` é 3 de abril, sempre. Aceitar os dois formatos tornaria impossível saber se `05/06` é maio ou junho, e o erro seria silencioso — os números do dashboard ficariam errados sem nenhuma linha rejeitada.

**[a validar]** Datas futuras são aceitas sem restrição. Venda com data futura pode ser pedido programado; rejeitar bloquearia um caso legítimo. Se o cliente disser que não faz sentido no negócio dele, vira validação.

### Valor

Aceita, após remover `R$`, espaços e espaços não-quebráveis:

| Entrada | Resultado |
|---|---|
| `1.204,50` | `1204.50` |
| `1204,50` | `1204.50` |
| `1204.50` | `1204.50` |
| `1,204.50` | `1204.50` |
| `1204` | `1204.00` |
| `R$ 1.204,50` | `1204.50` |

**Regra de desambiguação** — resolve o caso em que só há um separador e não se sabe se é milhar ou decimal:

1. Se houver **ambos** `.` e `,`: o que aparecer **por último** é o decimal; o outro é milhar e é descartado.
2. Se houver **apenas um** separador: se tiver **exatamente 3 dígitos depois**, é milhar (`1.204` → `1204`); caso contrário é decimal (`1204,5` → `1204.50`).
3. Mais de duas casas decimais: arredondar para 2, meio-para-cima. Não é erro.

O caso `1.204` merece atenção: pela regra 2 vira mil duzentos e quatro, não um real e vinte centavos. É a leitura correta em planilha brasileira, mas é bom saber que a regra existe e por quê.

**Rejeitado:** vazio, texto não numérico, e **valores negativos**. Devolução e estorno não estão no escopo do v1 — o schema não tem como representá-los, e importá-los como negativo distorceria toda a receita sem que ninguém percebesse. **[a validar]** com o cliente.

### Categoria e Unidade de Negócio

Comparação com o cadastro **daquela empresa**, normalizada (minúsculas, sem acento, sem espaços nas pontas).

**A importação nunca cria categoria nem unidade.** Valor que não existir rejeita a linha ([data-model.md](./architecture/data-model.md)). Criar cadastro a partir de planilha é como uma base vira lixo: um erro de digitação viraria "Loja Cetro" ao lado de "Loja Centro", e o filtro do dashboard passaria a listar as duas para sempre.

Unidade **inativa** é aceita na importação — dado histórico precisa poder entrar mesmo depois de a loja fechar.

### Cliente

Opcional. Espaços das pontas removidos, string vazia vira `null`. Máximo 200 caracteres; acima disso, truncar e **não** rejeitar a linha.

### Observações

Opcional. Mesmo tratamento; máximo 1 000 caracteres.

---

## 5. Linhas e ordem de validação

**Linha totalmente vazia** é ignorada: não conta em `total_records` nem gera rejeição. Planilha real quase sempre tem linhas em branco no fim.

**Ordem por linha:** obrigatórios presentes → conversão de tipo → existência de categoria e unidade → duplicata.

**Uma rejeição por linha.** Ao encontrar o primeiro problema, registrar e passar para a próxima linha. Listar todos os erros de uma linha inundaria a tela e não ajuda: o usuário corrige a planilha e reenvia de qualquer forma.

**Duplicata é a última verificação**, e só roda se a linha for válida em tudo o mais. A chave natural está definida no [data-model.md](./architecture/data-model.md).

**Contagens:** `total_records` = linhas não vazias; `valid_records` = importadas; `error_records` = rejeições com `kind = 'error'`; `duplicate_records` = rejeições com `kind = 'duplicate'`. Sempre `total = valid + error + duplicate`. **Esse invariante deve ser testado.**

---

## 6. Mensagens de rejeição

Texto exato gravado em `import_errors.error_message`. Padronizar aqui evita que cada dev escreva a sua e a tela fique inconsistente.

| Situação | Mensagem |
|---|---|
| Obrigatório vazio | `Coluna {campo} está vazia` |
| Data inválida | `Coluna data em formato inválido: "{valor}"` |
| Valor inválido | `Coluna valor em formato inválido: "{valor}"` |
| Valor negativo | `Coluna valor não pode ser negativa: "{valor}"` |
| Categoria inexistente | `Coluna categoria não corresponde a nenhuma categoria cadastrada: "{valor}"` |
| Unidade inexistente | `Coluna unidade não corresponde a nenhuma unidade cadastrada: "{valor}"` |
| Duplicata | `Registro idêntico já existe na base — {data} · {categoria} · {unidade} · {valor}` |

`raw_value` guarda o valor bruto que causou o problema, quando existir.

---

## 7. Casos de teste obrigatórios

Um card de teste do parser deve cobrir, no mínimo:

- CSV em `cp1252` com `;` e acentos — o caso mais comum do mundo real
- CSV em UTF-8 com BOM e `,`
- `.xlsx` com data nativa e com data como texto
- Os seis formatos de valor da tabela da seção 4, mais `1.204` e `1204,5`
- Data `03/04/2026` resultando em 3 de abril
- Linha vazia no meio e no fim do arquivo
- Categoria com acento diferente do cadastro (`Eletronicos` casando com `Eletrônicos`)
- Unidade inexistente
- Duplicata exata e quase-duplicata (mesmo dia, um centavo de diferença → **não** é duplicata)
- Arquivo cujo cabeçalho não tem coluna de valor
- `total = valid + error + duplicate` em todos os cenários acima
