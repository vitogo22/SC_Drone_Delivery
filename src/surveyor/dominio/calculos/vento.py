"""Vento: bloco da tabela pela hora de saída e velocidade em solo (Etapa 4).

API prevista:
- bloco_do_horario(hora_saida_s) -> int            # 6, 9, 12, 15 ou 18; a coluna 21h nunca é usada
- velocidade_solo_kmh(v_kmh, rumo_graus, vento) -> float   # triângulo de velocidades (A2)
A tabela vem de dados/vento.csv, lida por surveyor.infraestrutura.arquivos.leitor_csv.
"""
