"""Leitura e validação dos CSVs de entrada (Etapas 1 e 4).

API prevista:
- ler_coordenadas(caminho, regras) -> list[Coordenada]  # cep, longitude, latitude (nesta ordem)
- ler_extras(caminho) -> list[Coordenada]          # pode_pousar=False (A6)
- ler_vento(caminho) -> tabela por (dia, bloco)
Problemas de formato viram ErroDados com nome do arquivo e número da linha.
"""

import csv
from pathlib import Path

from surveyor.dominio.erros import ErroDados
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import Regras

COLUNAS_COORDENADAS = ("cep", "longitude", "latitude")


def ler_coordenadas(caminho: Path, regras: Regras) -> list[Coordenada]:
    """Lê o CSV do professor; o campus precisa estar na lista."""
    coordenadas = _ler_pontos(caminho, pode_pousar=True)
    if all(coordenada.cep != regras.cep_campus for coordenada in coordenadas):
        raise ErroDados(f"{caminho}: campus {regras.cep_campus} ausente")
    return coordenadas


def ler_extras(caminho: Path) -> list[Coordenada]:
    """Lê as coordenadas extras da equipe, no mesmo formato do CSV do professor."""
    return _ler_pontos(caminho, pode_pousar=False)  # A6: nas extras o drone só fotografa


def _ler_pontos(caminho: Path, *, pode_pousar: bool) -> list[Coordenada]:
    """Lê um CSV `cep,longitude,latitude` mantendo CEP e coordenadas como texto original."""
    pontos: list[Coordenada] = []
    linha_do_cep: dict[str, int] = {}
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for coluna in COLUNAS_COORDENADAS:
            if coluna not in (leitor.fieldnames or ()):
                raise ErroDados(f"{caminho}, linha 1: falta a coluna {coluna!r}")

        for linha in leitor:
            onde = f"{caminho}, linha {leitor.line_num}"
            if None in linha or None in linha.values():
                raise ErroDados(
                    f"{onde}: esperava {len(COLUNAS_COORDENADAS)} valores "
                    f"({', '.join(COLUNAS_COORDENADAS)})"
                )
            try:
                ponto = Coordenada(
                    cep=linha["cep"],
                    latitude_texto=linha["latitude"],
                    longitude_texto=linha["longitude"],
                    pode_pousar=pode_pousar,
                )
            except ValueError as erro:
                raise ErroDados(f"{onde}: {erro}") from erro
            if ponto.cep in linha_do_cep:
                raise ErroDados(
                    f"{onde}: CEP {ponto.cep} repetido "
                    f"(já aparece na linha {linha_do_cep[ponto.cep]})"
                )
            linha_do_cep[ponto.cep] = leitor.line_num
            pontos.append(ponto)
    return pontos
