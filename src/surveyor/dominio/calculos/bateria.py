"""Bateria: autonomia e consumo (Etapa 5).

API prevista:
- autonomia_s(v_kmh, regras) -> float               # 5000 x fator x (36 / v)^2
- consumo_trecho(t_s, v_kmh, regras) -> float       # fração da bateria
- consumo_parada(parada_s, v_kmh, regras) -> float  # na taxa da velocidade do trecho (A1)
A velocidade é sempre a ajustada (antes do vento), nunca a velocidade em solo.
"""
