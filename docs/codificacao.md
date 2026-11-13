# Codificação genética

Código: [`src/surveyor/otimizacao/cromossomo.py`](../src/surveyor/otimizacao/cromossomo.py).

## O cromossomo

São N = 375 pontos a visitar: os 373 do arquivo do professor (o campus fica de fora) e as 2 coordenadas extras da equipe. Cada ponto é identificado pelo seu índice, de 0 a N − 1. O cromossomo tem três partes:

| Parte | Genes | Valor de cada gene | Decide |
|---|---|---|---|
| `ordem` | N | permutação de 0 a N − 1 | a sequência de visita (o voo sai do campus e volta a ele) |
| `velocidades` | N + 1 | índice de 0 a 11, ou seja, `36 + 4·i` km/h | `[p]` é a velocidade do trecho que **chega** ao ponto `p`; `[N]` é a da volta ao campus |
| `calendario` | 7 | `True`/`False` | em quais dias o drone pode voar |

No total são 375 + 376 + 7 = **758 genes**. Exemplo com 4 pontos:

```
ordem       = (2, 0, 3, 1)               campus → 2 → 0 → 3 → 1 → campus
velocidades = (0, 5, 11, 2, 1)           chega ao 2 a 80 km/h (índice 11), ao 0 a 36, ao 3 a 44,
                                         ao 1 a 56 e volta ao campus a 40
calendario  = (T, F, T, T, F, T, T)      não voa nos dias 2 e 5
```

O cromossomo **não** diz onde pousar, quando trocar a bateria nem quando esperar. Quem decide isso é o simulador (`dominio/simulador.py`), que funciona como um **decodificador**. Ele percorre a ordem com as velocidades escolhidas, pousa sempre que a bateria não daria para o próximo trecho, encerra o dia no limite de operação e retoma às 06:00:00 do próximo dia habilitado. Por isso qualquer cromossomo bem formado vira um plano seguro, ou um plano marcado como inválido, que a fitness penaliza. O GA nunca precisa "consertar" pousos ou horários.

O cromossomo é imutável (tuplas). Os operadores sempre criam um filho novo, então os pais nunca são alterados.

## Comparação com as codificações sugeridas no enunciado

| Codificação | Como seria aqui | Decisão |
|---|---|---|
| Permutação (*path*) | lista dos pontos na ordem de visita | **Usada** na parte `ordem`. É a forma mais direta, e os cruzamentos próprios para permutação (OX, PMX, ERX) sempre geram uma rota válida. |
| Ordem (*ordinal*) | cada gene é a posição do próximo ponto numa lista de referência que vai encolhendo | Rejeitada. Aceita o cruzamento de um ponto sem gerar repetição, mas depois do corte o mesmo gene passa a apontar para outro ponto. O filho herda muito pouco da rota dos pais, o que quebra os blocos construtivos. |
| Adjacência | o gene `i` é o ponto visitado logo depois de `i` | Rejeitada. Preserva arestas, mas os cruzamentos simples criam subciclos que precisam de reparo. O benefício de herdar arestas vem do ERX, que usamos sobre a permutação. |
| Matriz (sequência de ordens de visita) | matriz binária N × N | Rejeitada. São 375² ≈ 140 mil bits, e quase todo cruzamento ou mutação gera uma matriz que não é uma rota. |
| Coordenadas (*real-valued*, chaves aleatórias) | um número real por ponto; a rota é a ordenação desses números | Rejeitada. Qualquer cruzamento dá um filho válido, mas uma mudança pequena num gene reordena vários pontos de uma vez, e a decodificação por ordenação esconde o que está sendo herdado. A permutação com OX é mais clara e faz o mesmo papel. |
| Árvores (caminhos hierárquicos) | regiões → sub-rotas → pontos | Rejeitada. A rota é uma única sequência que precisa passar por todos os pontos uma vez. A hierarquia só acrescentaria operadores de reparo. |
| Baseada em heurísticas (indireta) | o cromossomo guarda decisões, e um decodificador monta a solução | **Usada em parte.** Pousos, trocas de bateria, esperas e mudanças de dia não estão nos genes. O simulador os deduz das decisões do cromossomo. |

Resumo: **permutação** para a ordem, **genes diretos** para velocidade e calendário e **decodificação indireta** para pousos e horários.

## Hipótese dos blocos construtivos

Um bom bloco aqui é uma sub-rota curta de pontos vizinhos visitados em sequência, **junto com as velocidades desses trechos**. A codificação foi escolhida para que esse bloco passe inteiro de pai para filho:

- a velocidade é indexada pelo **ponto**, não pela posição na rota. Quando o OX copia o trecho `… 17 → 42 → 8 …` de um pai, as velocidades de chegada a 17, 42 e 8 vêm do mesmo pai. Se a velocidade fosse indexada pela posição, a sub-rota mudaria de lugar no filho e passaria a usar velocidades de outros pontos, desfazendo o bloco;
- os cruzamentos de permutação preservam sub-rotas (OX e PMX copiam um segmento contínuo) ou arestas (ERX);
- cada dia do calendário é um bloco independente de um gene só.

## Por que os cruzamentos clássicos não servem para a ordem

O enunciado sugere testar cruzamento de um ponto, de múltiplos pontos e uniforme. Aplicados direto na permutação, os três geram rotas inválidas. Exemplo com corte depois da segunda posição:

```
pai 1  = (0, 1 | 2, 3, 4)
pai 2  = (4, 3 | 2, 1, 0)
filho  = (0, 1 | 2, 1, 0)      pontos 0 e 1 repetidos, pontos 3 e 4 faltando
```

O plano precisa visitar cada ponto exatamente uma vez, então esse filho não é uma rota. Por isso:

- na **ordem**, usamos cruzamentos de permutação: **OX** (padrão), **PMX** e **ERX** (comparados nos experimentos, `docs/experimentos.md`);
- nas **velocidades**, a velocidade de cada ponto vem do mesmo pai que forneceu o ponto. A da volta ao campus vem de um pai sorteado;
- no **calendário**, o cruzamento é **uniforme**: cada dia vem de um pai sorteado. Aqui ele funciona, porque os 7 bits são independentes e qualquer combinação é válida.

Mutações: troca, inversão e deslocamento na ordem; ±1 no índice de velocidade; inverter um bit do calendário.

## Por que existe um calendário

A previsão de vento (`dados/vento.csv`) varia muito de um dia para o outro. Nos blocos de 6h, 9h, 12h e 15h, que são os que o voo usa porque a operação termina às 17:00:00:

| Dia | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| Vento (km/h) | 3–7 | 16–20 | 8–20 | 6–11 | 17–19 | 4–8 | 6–16 |

Numa rota fechada, que sai do campus e volta a ele, vento constante **nunca reduz** o tempo total. O que se ganha com vento a favor se perde, com sobra, com vento contra e de través. Simulamos 2.000 rotas fechadas aleatórias com os 376 pontos reais, velocidades de 36 a 80 km/h e vento de 3 a 21 km/h em 8 direções. O vento aumentou o tempo de voo em **+0,1% a +37%** e não reduziu em nenhuma delas.

Como a espera em solo não entra no custo (A5), deixar de voar num dia de vento forte não custa nada. Voar nele custa tempo e, com isso, mais pousos. O calendário deixa o GA escolher os dias. Por exemplo, evitar os dias 2 e 5 e concentrar o voo nos dias 1, 4 e 6, desde que a rota caiba no prazo de 7 dias. Junto com a velocidade por trecho, é assim que a codificação otimiza os **horários**, e não só a ordem de visita.
