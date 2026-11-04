# Contrato: regras e decisões do UNIBRASIL Surveyor

Fonte da verdade da equipe para as regras do enunciado e as interpretações adotadas.
Os códigos **A1–A21** aparecem nos comentários do código (`# A3`) e nos testes.
Toda hipótese nova recebe um código novo aqui **antes** de virar código.

## 1. Regras do enunciado

**Trajeto**
- Começa e termina no campus, CEP `82821020`. Cada outro CEP aparece uma única vez como destino.
- O drone só para ou pousa em coordenadas da lista. A recarga só acontece em pontos do arquivo do professor (A6).

**Velocidade e bateria**
- Velocidades ajustáveis: 36, 40, …, 80 km/h (inteiras, múltiplas de 4, ≥ 10 m/s, ≤ 83 km/h) (A7).
- Autonomia: `A(v) = 5000 × 1,14 × (36 / v)²` s, com `v` = velocidade ajustada, **antes** do vento (A3, A16).
- Paradas: 60 s para foto sem pouso; 172 s com pouso e troca de bateria (A8). Todo pouso troca a bateria.
- A bateria nunca pode zerar no ar.

**Tempo**
- O tempo de cada trecho é calculado em segundos e **arredondado para cima**.
- `Hora final = Hora inicial + tempo do trecho + parada` (A17).
- Voos de 06:00:00 a 19:00:00. Cada trecho começa e termina no mesmo dia. Todo dia de voo termina com pouso.
- Tudo termina até o dia 7.

**Distância e vento**
- Distância por Haversine com R = 6371 km, coordenadas convertidas de graus para radianos (A19).
- O vento vale pelo bloco de 3 h da **hora de saída** e fica fixo até a chegada.
- A direção do vento é de onde ele vem. Usa-se a velocidade em km/h; as rajadas são ignoradas (A14, A15). Tabela em `dados/vento.csv`.

**Custos**
- R$ 80 por pouso. Mais R$ 80 se o pouso acontecer depois de 17:00:00 (A11).
- Objetivo: minimizar o custo, medido pelo tempo total de voo e pelos pousos (A4, A5).

**Coordenadas extras** (uma por integrante; ver `docs/coordenadas_extras.md`)
- CEP = os 8 últimos dígitos da matrícula.
- Latitude **e** longitude com exatamente 13 casas decimais. A latitude **ou** a longitude termina com os 8 últimos dígitos da matrícula.
- Pelo menos 100 m de qualquer outro ponto. Menos de 1500 m de algum ponto do arquivo do professor (A12).

## 2. Decisões provisórias (pendentes de confirmação do professor)

| # | Ponto | Decisão adotada | Por quê |
|---|---|---|---|
| A1 | Taxa de consumo nas paradas de 60/172 s | Taxa da **velocidade do trecho que chega** ao ponto | A opção mais segura: se a outra leitura for a correta, o plano continua válido |
| A2 | Modelo de vento | **Triângulo de velocidades** (o drone corrige o rumo para chegar ao destino) | Somar o vetor do drone, apontado para o destino, com o vento desvia a trajetória (28,3° em vez de 39,5° no exemplo) e superestima a velocidade, ou seja, subestima o consumo. O exemplo dá 41,0026532396 km/h pela soma e 39,3372461072 km/h pelo triângulo |
| A3 | Fator 1,14 | **Multiplica** a autonomia: A(36) = 5700 s | Em Curitiba o ar é mais denso e a temperatura é maior que nas condições de laboratório (3000 m, 5 °C) |
| A4 | Como somar tempo e R$ | `custo = horas de voo × VALOR_HORA + R$ dos pousos`, com `VALOR_HORA = 80` | O enunciado não dá a conversão; o valor é avaliado nos experimentos (40/80/160) |
| A5 | "Tempo total de voo" | Soma do tempo no ar (trechos + paradas), sem a espera em solo | Leitura literal de "tempo de voo" |
| A6 | Pouso nas coordenadas extras | **Proibido**: nelas o drone só fotografa | "Só pode recarregar em uma das coordenadas do arquivo fornecido pelo professor" |
| A7 | Coluna Velocidade do CSV diz "0 a 83" | Válidas: 36 a 80, de 4 em 4 | Regras de 10 m/s mínimos e múltiplos de 4 |
| A8 | "A cada troca de bateria [...] 60 s se não houver pouso" | Lido como "a cada parada" | Sem pouso não existe troca de bateria |
| A9 | Pouso final no campus | Conta como pouso: 172 s, R$ 80 (+R$ 80 depois das 17h), Pouso = SIM | "Qualquer pouso gera uma recarga" |
| A10 | Bateria que paga os 172 s do pouso | A que chega; o drone decola com 100% | Opção mais segura, e coerente com a Hora final da linha que chega |
| A11 | Instante do pouso para a taxa das 17h | A Hora final do trecho; 17:00:00 em ponto não paga taxa | "Após as 17:00:00" |
| A12 | "Base" na regra dos 1500 m | Pontos do arquivo do professor | Leitura mais restrita, que atende às duas interpretações |
| A13 | Data de entrega | — | Não consta no enunciado |

## 3. Cuidados de implementação (não dependem do professor)

| # | Ponto | Como tratar |
|---|---|---|
| A14 | Na tabela de vento, nós e km/h não batem | Usar a linha em km/h |
| A15 | Coluna 21h | Nunca é usada (a última saída possível é 18:59:59) |
| A16 | A tabela de exemplos arredonda a autonomia (2813 s) | Usar a fórmula exata (2812,5 s) |
| A17 | O exemplo "chega 9:20, parte 9:21" | No CSV, a Hora final já inclui a parada |
| A18 | As faixas do enunciado usam "–" (travessão) | O CSV usa hífen ASCII `-`; o ruff (RUF001) acusa caracteres ambíguos |
| A19 | "6.371 km" | Separador de milhar: R = 6371 km |
| A20 | O campus pode ser revisitado | Não usamos isso: o campus fica só no início e no fim |
| A21 | Pairar "um minuto **ou mais**" | Permitido, mas opcional |

## 4. Respostas do professor

| Data | Pergunta (A#) | Resposta | Impacto no código |
|---|---|---|---|
| | | | |
