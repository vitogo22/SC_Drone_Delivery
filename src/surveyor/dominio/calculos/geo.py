"""Geodésia: distância Haversine e rumo entre coordenadas (Etapa 3).

API prevista:
- distancia_km(origem, destino, regras) -> float   # Haversine, R = regras.raio_terra_km
- rumo_graus(origem, destino) -> float             # 0 a 360, a partir do Norte, sentido horário
- matrizes pré-calculadas de distância e rumo, indexadas pela posição do ponto
"""

import math

from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import Regras


def distancia_km(origem: Coordenada, destino: Coordenada, regras: Regras) -> float:
    """Distância Haversine com graus convertidos para radianos e R = regras.raio_terra_km (A19)."""
    phi1 = math.radians(origem.latitude)
    phi2 = math.radians(destino.latitude)
    delta_phi = phi2 - phi1
    delta_lambda = math.radians(destino.longitude - origem.longitude)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * regras.raio_terra_km * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def rumo_graus(origem: Coordenada, destino: Coordenada) -> float:
    """Rumo inicial de `origem` para `destino`: 0 = Norte, 90 = Leste, de 0 a 360."""
    phi1 = math.radians(origem.latitude)
    phi2 = math.radians(destino.latitude)
    delta_lambda = math.radians(destino.longitude - origem.longitude)
    theta = math.atan2(
        math.sin(delta_lambda) * math.cos(phi2),
        math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda),
    )
    return math.degrees(theta) % 360
