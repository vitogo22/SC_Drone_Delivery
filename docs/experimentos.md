# Experimentos

Comparação dos parâmetros do algoritmo genético. O resultado definiu a configuração padrão de `ParametrosGA`.

## Método

- **Um fator por vez.** Cada linha muda só um parâmetro em relação à base. Os demais ficam iguais.
- **Base:** população 200, cruzamento OX (taxa 90%), mutação 25%, torneio com k = 3, elitismo 2%, semeadura de 15% (indivíduos gerados pelo vizinho mais próximo), inválidos por penalidade e valor da hora de R$ 80.
- **Mesmo orçamento para todos:** 60 mil avaliações de fitness por execução. A população de 100 roda o dobro de gerações da de 200, e a de 400 roda a metade. Um limite de tempo deixaria a comparação dependente da carga da máquina.
- **3 sementes** (1, 2 e 3) por configuração, totalizando 60 execuções.
- **Custo:** horas de voo × valor da hora + R$ 80 por pouso, mais R$ 80 se o pouso for depois das 17h (A4 e A11 em `docs/decisoes.md`). Cada configuração usa o seu próprio valor da hora.

Para reproduzir (leva de 40 a 60 min com 11 processos; **não é preciso rodar para avaliar o trabalho**):

```bash
python -m surveyor --log-arquivo resultados/experimentos.log experimentos
```

Cada execução vira uma linha de `resultados/experimentos.csv`, e o log da rodada entregue está em `resultados/experimentos.log`.

## Resultados

| Fator | Valor | Sementes | Melhor custo | Custo médio | Desvio | Válidos | Pousos (melhor) | Horas de voo (melhor) | Tempo médio |
|---|---|---|---|---|---|---|---|---|---|
| base | padrão | 3 | R$ 2.177,31 | R$ 2.198,10 | R$ 18,00 | 3/3 | 12 | 15,22 | 322 s |
| população | 100 | 3 | R$ 2.221,93 | R$ 2.254,84 | R$ 28,88 | 3/3 | 12 | 15,77 | 188 s |
| população | 400 | 3 | R$ 2.232,62 | R$ 2.261,42 | R$ 46,76 | 3/3 | 12 | 15,91 | 404 s |
| cruzamento | PMX | 3 | R$ 2.173,62 | R$ 2.194,26 | R$ 19,78 | 3/3 | 12 | 15,17 | 297 s |
| cruzamento | ERX | 3 | R$ 2.189,60 | R$ 2.201,92 | R$ 11,82 | 3/3 | 12 | 15,37 | 631 s |
| mutação | 5% | 3 | R$ 2.217,09 | R$ 2.223,16 | R$ 6,68 | 3/3 | 12 | 15,71 | 119 s |
| mutação | 15% | 3 | R$ 2.215,56 | R$ 2.225,44 | R$ 10,76 | 3/3 | 12 | 15,69 | 213 s |
| seleção | torneio k = 2 | 3 | R$ 2.314,60 | R$ 2.337,80 | R$ 20,87 | 3/3 | 12 | 16,93 | 449 s |
| seleção | torneio k = 5 | 3 | R$ 2.203,02 | R$ 2.203,71 | R$ 1,02 | 3/3 | 12 | 15,54 | 224 s |
| seleção | rank | 3 | R$ 2.294,91 | R$ 2.322,24 | R$ 44,34 | 3/3 | 12 | 16,69 | 458 s |
| seleção | roleta | 3 | R$ 2.351,84 | R$ 2.416,56 | R$ 57,86 | 3/3 | 12 | 17,40 | 560 s |
| elitismo | 0% | 3 | R$ 2.465,42 | R$ 2.465,42 | R$ 0,00 | 3/3 | 13 | 17,82 | 502 s |
| elitismo | 5% | 3 | R$ 2.190,29 | R$ 2.202,04 | R$ 12,48 | 3/3 | 12 | 15,38 | 198 s |
| semeadura | 0% | 3 | R$ 9.204,04 | R$ 9.323,27 | R$ 113,03 | 3/3 | 60 | 55,05 | 610 s |
| semeadura | 10% | 3 | R$ 2.201,36 | R$ 2.288,70 | R$ 75,87 | 3/3 | 12 | 15,52 | 309 s |
| semeadura | 20% | 3 | R$ 2.197,24 | R$ 2.243,80 | R$ 71,84 | 3/3 | 12 | 15,47 | 285 s |
| inválidos | reparo | 3 | R$ 2.170,16 | R$ 2.205,09 | R$ 31,94 | 3/3 | 11 | 16,13 | 429 s |
| inválidos | pena de morte | 3 | R$ 2.174,00 | R$ 2.197,64 | R$ 21,67 | 3/3 | 12 | 15,18 | 487 s |
| valor da hora | R$ 40 | 3 | R$ 1.585,52 | R$ 1.599,85 | R$ 18,81 | 3/3 | 12 | 15,64 | 416 s |
| valor da hora | R$ 160 | 3 | R$ 3.484,98 | R$ 3.528,37 | R$ 58,15 | 3/3 | 15 | 14,28 | 302 s |

"Tempo médio" é o tempo de uma execução, com 11 execuções rodando em paralelo na mesma máquina. Serve só para comparar as linhas entre si.

## Análise

Com 3 sementes, o desvio fica em torno de R$ 20. Diferenças de custo médio menores que isso não indicam que uma configuração seja melhor que a outra.

- **População:** 200 é a melhor. Com o mesmo orçamento, 100 perde diversidade e 400 tem poucas gerações para evoluir. As duas ficam cerca de R$ 60 acima.
- **Cruzamento:** PMX e OX empatam no custo (R$ 2.194 contra R$ 2.198), mas PMX é um pouco mais rápido e achou o menor custo. ERX empata no custo e leva o dobro do tempo, porque monta a tabela de arestas a cada filho.
- **Mutação:** 25% supera 5% e 15% em cerca de R$ 25. A mutação também mexe nas velocidades e nos pousos, que o cruzamento de rota não altera.
- **Seleção:** torneio com k = 3 é a melhor. Com k = 5 o custo é parecido, mas as três sementes convergem para quase o mesmo ponto (desvio de R$ 1), o que é sinal de pressão de seleção alta. Torneio com k = 2, rank e roleta têm pressão baixa demais e ficam entre R$ 120 e R$ 220 acima.
- **Elitismo:** sem elitismo, o GA perde o melhor indivíduo a cada geração e nunca supera a semente do vizinho mais próximo (R$ 2.465,42, o mesmo valor nas três sementes). Com 2% ou 5% os resultados empatam.
- **Semeadura:** é o fator de maior efeito. Sem indivíduos do vizinho mais próximo, a população aleatória não encontra uma rota boa no orçamento (R$ 9,3 mil, 60 pousos e 55 h de voo). Com 10% a 20% de semeadura o custo cai para cerca de R$ 2,2 mil, e 15% (base) tem a melhor média.
- **Inválidos** (o enunciado pede a comparação): penalidade, reparo e pena de morte empatam no custo. A semeadura já garante indivíduos válidos desde o início, por isso o mecanismo pesa pouco. A penalidade foi mantida porque é a mais simples e a mais rápida: o reparo refaz o resto da rota a cada avaliação, e a pena de morte descarta filhos e precisa gerar outros.
- **Valor da hora:** muda o equilíbrio entre tempo e pousos, como esperado. Com R$ 160 o GA voa mais rápido (14,3 h) e aceita mais pousos (15). Com R$ 40 o tempo pesa menos e o custo cai quase pela metade.

### Configuração escolhida

A base com **cruzamento PMX**. Foi a única variação com média igual ou melhor que a base e tempo menor. As outras variações empataram com a base ou ficaram piores. O padrão de `ParametrosGA` usa essa configuração.

## Ordens de grandeza

Referência sem vento e sem extras, pela rota do vizinho mais próximo (340,8 km, 375 paradas de 60 s ≈ 6,25 h): a 36 km/h, ≈ 15,7 h de voo e ≈ 10 baterias.

As melhores execuções têm de 15,2 a 15,9 h de voo e 11 ou 12 pousos, dentro da faixa. O GA reduz o custo em cerca de 12% em relação à rota do vizinho mais próximo a 36 km/h (R$ 2.465,42 → R$ 2.173,62). A única linha fora da faixa é a semeadura de 0%, que é a configuração ruim sendo testada, e não um erro: o plano é válido, só é longo.
