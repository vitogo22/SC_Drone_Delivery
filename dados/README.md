# Dados de entrada

| Arquivo | Origem | Conteúdo |
|---|---|---|
| `coordenadas.csv` | AVA (fornecido pelo professor). **Não editar.** | 374 pontos, com o campus `82821020` na primeira linha |
| `extras.csv` | Equipe (Etapa 2) | uma coordenada por integrante, no **mesmo formato** do arquivo do professor (`cep,longitude,latitude`), com 13 casas decimais |
| `vento.csv` | Transcrito das tabelas Climatempo do enunciado | previsão por dia e bloco de 3 h |

## `coordenadas.csv`

- Cabeçalho `cep,longitude,latitude`: a **longitude vem antes** da latitude, ao contrário do CSV de saída.
- CEPs de 8 dígitos, sem repetição. Coordenadas com 13 casas decimais e nenhuma repetida.
- 13 pares de pontos estão a menos de 100 m entre si (o menor, a 41 m). A regra dos 100 m vale só para as coordenadas extras.

## `vento.csv`

- `dia`: 1 a 7.
- `hora_bloco`: hora em que o bloco começa (6, 9, 12, 15, 18). O bloco vale para **saídas** de `hora_bloco:00:00` até o começo do próximo bloco.
- `velocidade_kmh`: linha "Velocidade do vento (km/h)" da tabela. Não se usa a linha em nós, porque a conversão não bate, nem as rajadas, que o enunciado manda ignorar.
- `direcao`: de onde o vento **vem** (rosa dos ventos de 16 pontos).

A coluna 21h foi omitida de propósito: a última saída possível é às 18:59:59. As 35 células foram conferidas contra as imagens do enunciado.
