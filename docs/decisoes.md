# Contrato: regras e decisões do UNIBRASIL Surveyor

Este arquivo registra a seção 2 do plano de desenvolvimento. As decisões abaixo devem ser seguidas sem reinterpretar o enunciado.

## Equipe e coordenadas extras
- Integrante 1: RA `2024100142`; CEP extra `24100142`.
- Integrante 2: RA `2024100467`; CEP extra `24100467`.
- Nome completo do integrante 2: preencher antes da entrega final.
- **D1:** como o RA do integrante 1 começa com 2, as regras condicionais do enunciado valem para a dupla até confirmação do professor, inclusive o caso de RAs diferentes.

## Regras fixas do enunciado
- Trajeto começa e termina no campus, CEP `82821020`; os demais CEPs são visitados uma vez cada.
- Paradas e pousos somente nas coordenadas da lista.
- Saída a partir de `06:00:00`; pouso até `19:00:00`; conclusão em até 7 dias.
- Velocidades: `36, 40, ..., 80 km/h` (múltiplos de 4).
- Autonomia: `A(v) = 5000 × FATOR × (36 / v)²` segundos, com velocidade ajustada antes do vento.
- Parada: 60 s sem pouso; 172 s com pouso e troca de bateria.
- Tempo de trecho em segundos, arredondado para cima.
- Taxas: R$ 80 por pouso, mais R$ 80 se o pouso ocorrer depois das 17:00:00.
- Vento escolhido pela coluna correspondente ao horário de saída e fixo durante o trecho; rajadas ignoradas.
- A bateria nunca pode zerar no ar; solução inválida é falta grave.

## Decisões adotadas até o professor responder

| ID | Ponto em aberto | Padrão adotado |
|---|---|---|
| D1 | Regras condicionais para matrícula/RA | Valem para a dupla porque o RA do integrante 1 começa com 2; confirmar com o professor, inclusive RAs diferentes. |
| D2 | Fator 1,14 | Multiplica a autonomia: `FATOR_AUTONOMIA = 1.14`; alternativa conservadora: dividir. |
| D3 | Função de custo única | `custo = tempo_total_h × VALOR_HORA + R$ de pousos`, com `VALOR_HORA = 80`; tempo total = trechos + paradas, sem espera em solo. |
| D4 | Bateria nas paradas | 60 s e 172 s consumidos à taxa de referência (`s / A(36)`); no pouso é preciso ter bateria para os 172 s; `RESERVA_BATERIA = 1%`. |
| D5 | Pouso final no campus | Conta como pouso: 172 s, R$ 80 (mais R$ 80 se depois das 17h) e `Pouso = SIM`. |
| D6 | Modelo de vento | Soma vetorial do exemplo do PDF (`MODELO_VENTO = "exemplo_pdf"`); alternativa com correção de rumo daria, no exemplo, aproximadamente 39,3 km/h em vez de 41,0 km/h. |
| D7 | Relógio | Hora final = saída + voo + parada (contada no destino); próxima saída é igual à hora final, ou posterior se houve pouso. |
| D8 | Fim de expediente | `FIM_EXPEDIENTE = 17:00:00` para evitar a taxa; `19:00:00` é o teto absoluto. Reavaliar se o professor contar o tempo corrido (com as noites). |

## Pendências com o professor
Levar D1 a D6 ao professor e registrar as respostas aqui. Citar também que a coluna Velocidade do CSV indica valores de 0 a 83, em contradição com os múltiplos de 4 entre 36 e 80.

## Convenções de desenvolvimento
- Python 3.10 ou superior.
- Nomes em português.
- Type hints.
- Docstrings curtas.
- Preferir funções puras.
- Unidade no nome: `_km`, `_s`, `_kmh`.
