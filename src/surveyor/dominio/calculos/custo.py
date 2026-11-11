"""Tempo e custo (Etapa 5).

- `tempo_trecho_s`: segundos do trecho pela velocidade em solo, arredondados para cima;
  `TOLERANCIA_S` impede que o ruído do float suba 1 s.
- `taxa_pouso_reais`: R$ 80 por pouso, mais R$ 80 se a Hora final passar de 17:00:00;
  17:00:00 em ponto não paga a taxa adicional (A11).
- `custo_total`: horas no ar x valor da hora + R$ dos pousos (A4); a espera em solo não entra (A5).
"""

import math

from surveyor.dominio.modelos import PlanoDeVoo
from surveyor.dominio.regras import SEGUNDOS_POR_HORA, ParametrosOperacao, Regras

# Desconta o ruído do float (ex.: 120,00000000000003 s) antes do teto, para não ganhar 1 s à toa.
TOLERANCIA_S = 1e-9


def tempo_trecho_s(distancia_km: float, v_solo_kmh: float) -> int:
    """Segundos para voar `distancia_km` na velocidade em solo, arredondados para cima."""
    return math.ceil(distancia_km / v_solo_kmh * SEGUNDOS_POR_HORA - TOLERANCIA_S)


def taxa_pouso_reais(hora_final_s: int, regras: Regras) -> float:
    """R$ de um pouso pela Hora final do trecho; a taxa adicional só DEPOIS de 17:00:00 (A11)."""
    if hora_final_s > regras.inicio_taxa_adicional_s:
        return regras.taxa_pouso_reais + regras.taxa_adicional_reais
    return regras.taxa_pouso_reais


def custo_total(plano: PlanoDeVoo, regras: Regras, operacao: ParametrosOperacao) -> float:
    """Horas no ar x valor da hora + R$ dos pousos (A4); a espera em solo não entra (A5)."""
    horas_de_voo = plano.tempo_total_voo_s / SEGUNDOS_POR_HORA
    pousos_reais = sum(
        taxa_pouso_reais(trecho.hora_final_s, regras) for trecho in plano.trechos if trecho.pouso
    )
    return horas_de_voo * operacao.valor_hora_reais + pousos_reais
