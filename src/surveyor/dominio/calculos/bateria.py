"""Bateria: autonomia e consumo (Etapa 5).

API prevista:
- autonomia_s(v_kmh, regras) -> float               # 5000 x fator x (36 / v)^2
- consumo(duracao_s, v_kmh, regras) -> float        # fração da bateria, em trecho ou parada
A parada gasta na taxa da velocidade do trecho que chega ao ponto (A1).
A velocidade é sempre a ajustada (antes do vento), nunca a velocidade em solo.
"""

from surveyor.dominio.regras import Regras


def autonomia_s(v_kmh: int, regras: Regras) -> float:
    """Segundos de voo com uma bateria cheia na velocidade AJUSTADA `v_kmh` (A3, A16)."""
    if v_kmh not in regras.velocidades_kmh:
        raise ValueError(f"velocidade não ajustável: {v_kmh} km/h")
    proporcao = regras.velocidade_referencia_kmh / v_kmh
    return regras.autonomia_nominal_s * regras.fator_autonomia * proporcao**2


def consumo(duracao_s: int, v_kmh: int, regras: Regras) -> float:
    """Fração da bateria gasta em `duracao_s` segundos na velocidade ajustada `v_kmh`.

    Vale para o trecho e para a parada; na parada, `v_kmh` é a do trecho que chega (A1).
    """
    return duracao_s / autonomia_s(v_kmh, regras)
