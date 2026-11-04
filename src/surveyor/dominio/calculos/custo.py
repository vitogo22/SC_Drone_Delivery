"""Tempo e custo (Etapa 5).

API prevista:
- tempo_trecho_s(distancia_km, v_solo_kmh) -> int   # teto em segundos (tolerância de float)
- taxa_pouso_reais(hora_final_s, regras) -> float   # R$ 80, + R$ 80 depois de 17:00:00 (A11)
- custo_total(plano, regras, operacao) -> float     # horas x valor_hora + R$ dos pousos (A4)
"""
