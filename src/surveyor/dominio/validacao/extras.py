"""Regras das coordenadas extras da equipe (Etapa 2, A12).

- `validar_extra(extra, matricula, base, regras)`: violações (lista vazia = válida). Confere
  13 casas na latitude e na longitude, uma delas terminando com os 8 últimos dígitos da
  matrícula, CEP igual a esses dígitos, >= 100 m de qualquer ponto e < 1500 m de algum ponto
  do arquivo do professor.
- `ponto_mais_proximo(extra, base, regras)`: ponto da base mais perto e a distância em metros,
  para a tabela de `docs/coordenadas_extras.md`.
"""

import math
from collections.abc import Sequence

from surveyor.dominio.calculos.geo import distancia_km
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import METROS_POR_KM, Regras


def validar_extra(
    extra: Coordenada, matricula: str, base: Sequence[Coordenada], regras: Regras
) -> list[str]:
    """Violações das regras da coordenada extra; lista vazia = válida.

    `base` são os outros pontos (professor + outras extras), sem a própria `extra`. Os pontos
    do professor são os que podem receber pouso (A6) e só eles contam para os 1500 m (A12).
    """
    final = matricula[-regras.digitos_finais_matricula :]
    violacoes: list[str] = []
    for nome, texto in (("latitude", extra.latitude_texto), ("longitude", extra.longitude_texto)):
        casas = len(texto.partition(".")[2])
        if casas != regras.casas_decimais_coordenada:
            violacoes.append(
                f"{nome} {texto} tem {casas} casas decimais, "
                f"e não {regras.casas_decimais_coordenada}"
            )
    if not (extra.latitude_texto.endswith(final) or extra.longitude_texto.endswith(final)):
        violacoes.append(f"nem a latitude nem a longitude terminam com {final} (matrícula)")
    if extra.cep != final:
        violacoes.append(f"CEP {extra.cep} diferente de {final} (matrícula)")

    distancias_m = [(ponto, distancia_km(extra, ponto, regras) * METROS_POR_KM) for ponto in base]
    violacoes += [
        f"a {distancia_m:.1f} m do CEP {ponto.cep}, "
        f"e o mínimo é {regras.distancia_minima_extra_m:.0f} m"
        for ponto, distancia_m in distancias_m
        if distancia_m < regras.distancia_minima_extra_m
    ]
    professor_mais_proximo_m = min(
        (distancia_m for ponto, distancia_m in distancias_m if ponto.pode_pousar),
        default=math.inf,
    )
    if professor_mais_proximo_m >= regras.distancia_maxima_extra_m:
        violacoes.append(
            f"o ponto do professor mais próximo está a {professor_mais_proximo_m:.1f} m, "
            f"e precisa ficar a menos de {regras.distancia_maxima_extra_m:.0f} m (A12)"
        )
    return violacoes


def ponto_mais_proximo(
    extra: Coordenada, base: Sequence[Coordenada], regras: Regras
) -> tuple[Coordenada, float]:
    """Ponto de `base` mais perto de `extra` e a distância até ele, em metros."""
    if not base:
        raise ValueError("base vazia: não há ponto mais próximo")
    distancias_m = ((ponto, distancia_km(extra, ponto, regras) * METROS_POR_KM) for ponto in base)
    return min(distancias_m, key=lambda par: par[1])
