"""Geodésia: distância Haversine e rumo entre coordenadas (Etapa 3).

API prevista:
- distancia_km(origem, destino, regras) -> float   # Haversine, R = regras.raio_terra_km
- rumo_graus(origem, destino) -> float             # 0 a 360, a partir do Norte, sentido horário
- matrizes pré-calculadas de distância e rumo, indexadas pela posição do ponto
"""
