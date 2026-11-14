"""Escrita do CSV do plano de voo com as 11 colunas do enunciado (Etapa 9).

`escrever_plano(plano, caminho)` grava uma linha por trecho. CEP e coordenadas saem com o
texto lido da entrada (13 casas, zeros no fim, hífen ASCII), com a latitude ANTES da longitude
(na entrada é o contrário). Horas em `HH:MM:SS`, pouso como SIM/NÃO, UTF-8 sem BOM, separador
vírgula e fim de linha `\\n`, como os arquivos de `dados/`.
"""

import csv
from pathlib import Path

from surveyor.dominio.calculos.relogio import para_hhmmss
from surveyor.dominio.modelos import PlanoDeVoo, Trecho

COLUNAS_PLANO = (
    "CEP inicial",
    "Latitude inicial",
    "Longitude inicial",
    "Dia do vôo",
    "Hora inicial",
    "Velocidade",
    "CEP final",
    "Latitude final",
    "Longitude final",
    "Pouso",
    "Hora final",
)


def escrever_plano(plano: PlanoDeVoo, caminho: Path) -> None:
    """Grava o plano em `caminho`, com o cabeçalho e uma linha por trecho."""
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, lineterminator="\n")
        escritor.writerow(COLUNAS_PLANO)
        escritor.writerows(_linha(trecho) for trecho in plano.trechos)


def _linha(trecho: Trecho) -> tuple[str, ...]:
    return (
        trecho.origem.cep,
        trecho.origem.latitude_texto,
        trecho.origem.longitude_texto,
        str(trecho.dia),
        para_hhmmss(trecho.hora_inicial_s),
        str(trecho.velocidade_kmh),
        trecho.destino.cep,
        trecho.destino.latitude_texto,
        trecho.destino.longitude_texto,
        "SIM" if trecho.pouso else "NÃO",
        para_hhmmss(trecho.hora_final_s),
    )
