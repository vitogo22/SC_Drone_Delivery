"""Tempo e custo (Etapa 5).

API prevista:
- tempo_trecho_s(distancia_km, v_solo_kmh) -> int   # teto em segundos (tolerância de float)
- taxa_pouso_reais(hora_final_s, regras) -> float   # R$ 80, + R$ 80 depois de 17:00:00 (A11)
- custo_total(plano, regras, operacao) -> float     # horas x valor_hora + R$ dos pousos (A4)
"""

import math

from surveyor.dominio.regras import SEGUNDOS_POR_HORA

# Desconta o ruído do float (ex.: 120,00000000000003 s) antes do teto, para não ganhar 1 s à toa.
TOLERANCIA_S = 1e-9


def tempo_trecho_s(distancia_km: float, v_solo_kmh: float) -> int:
    """Segundos para voar `distancia_km` na velocidade em solo, arredondados para cima."""
    return math.ceil(distancia_km / v_solo_kmh * SEGUNDOS_POR_HORA - TOLERANCIA_S)
