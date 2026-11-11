"""Bateria: autonomia e consumo (Etapa 5).

API prevista:
- autonomia_s(v_kmh, regras) -> float               # 5000 x fator x (36 / v)^2
- consumo_trecho(t_s, v_kmh, regras) -> float       # fração da bateria
- consumo_parada(parada_s, v_kmh, regras) -> float  # na taxa da velocidade do trecho (A1)
A velocidade é sempre a ajustada (antes do vento), nunca a velocidade em solo.
"""

from surveyor.dominio.regras import Regras


def autonomia_s(v_kmh: int, regras: Regras) -> float:
    """Segundos de voo com uma bateria cheia na velocidade AJUSTADA `v_kmh` (A3, A16)."""
    if v_kmh not in regras.velocidades_kmh:
        raise ValueError(f"velocidade não ajustável: {v_kmh} km/h")
    proporcao = regras.velocidade_referencia_kmh / v_kmh
    return regras.autonomia_nominal_s * regras.fator_autonomia * proporcao**2
