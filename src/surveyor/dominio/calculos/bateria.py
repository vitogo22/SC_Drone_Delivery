"""Bateria: autonomia e consumo (Etapa 5).

- `autonomia_s`: segundos de voo com a bateria cheia, 5000 x fator x (36 / v)^2 (A3), pela
  fórmula exata, sem arredondar (A16).
- `consumo`: fração da bateria (0 a 1) gasta numa duração. Vale para o trecho e para a parada,
  que gasta na taxa da velocidade do trecho que chega ao ponto (A1).

A velocidade é sempre a ajustada (36, 40, ..., 80 km/h, antes do vento), nunca a velocidade em
solo; qualquer outra levanta ValueError (A7).
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
