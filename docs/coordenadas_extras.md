# Coordenadas extras

Uma coordenada por integrante, validada pelas regras de `docs/decisoes.md` (seção 1): 13 casas decimais; final com os 8 últimos dígitos da matrícula; pelo menos 100 m de qualquer ponto; menos de 1500 m de algum ponto do arquivo do professor. A distância é medida até o ponto mais próximo da base consolidada (professor + extras).

| Integrante | Matrícula | CEP | Latitude | Longitude | Ponto mais próximo (CEP) | Distância (m) |
|---|---|---|---|---|---|---|
| Vitor Hugo Viana Mondequi | 2024100142 | 24100142 | -25.4206324100142 | -49.2191752000000 | 82821020 | 431.7 |
| Matheus Dominguez Biesek | 2024100467 | 24100467 | -25.4252024100467 | -49.2127867000000 | 82821016 | 389.9 |

A tabela acima é a saída de `python -m surveyor extras`, que também valida as regras e termina com código 1 se alguma extra as quebrar. O CEP 82821020 é o campus UniBrasil, que também é um ponto do arquivo do professor.
