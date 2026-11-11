"""Leitura e validação dos CSVs de entrada (Etapas 1 e 4).

API prevista:
- ler_coordenadas(caminho) -> list[Coordenada]     # colunas: cep, longitude, latitude (nesta ordem)
- ler_extras(caminho) -> list[Coordenada]          # pode_pousar=False (A6)
- ler_vento(caminho) -> tabela por (dia, bloco)
Problemas de formato viram ErroDados com nome do arquivo e número da linha.
"""

import csv
from pathlib import Path

from surveyor.dominio.modelos import Coordenada


def ler_coordenadas(caminho: Path) -> list[Coordenada]:
    """Lê o CSV `cep,longitude,latitude` mantendo CEP e coordenadas como texto original."""
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return [
            Coordenada(
                cep=linha["cep"],
                latitude_texto=linha["latitude"],
                longitude_texto=linha["longitude"],
            )
            for linha in csv.DictReader(arquivo)
        ]
