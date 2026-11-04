"""Conversão entre `HH:MM:SS` e segundos desde a meia-noite.

Convenção do projeto: internamente todo horário é um `int` de segundos desde 00:00:00
do dia de voo. O texto `HH:MM:SS` só aparece nas bordas (leitura e escrita de CSV, log).
"""

import re

SEGUNDOS_POR_DIA = 24 * 3600
_PADRAO_HHMMSS = re.compile(r"([0-9]{2}):([0-9]{2}):([0-9]{2})")


def para_segundos(hhmmss: str) -> int:
    """Converte `"HH:MM:SS"` (com dois dígitos em cada parte) em segundos desde 00:00:00."""
    encontrado = _PADRAO_HHMMSS.fullmatch(hhmmss)
    if encontrado is None:
        raise ValueError(f"horário fora do formato HH:MM:SS: {hhmmss!r}")
    horas, minutos, segundos = (int(parte) for parte in encontrado.groups())
    if horas > 23 or minutos > 59 or segundos > 59:
        raise ValueError(f"horário inexistente: {hhmmss!r}")
    return horas * 3600 + minutos * 60 + segundos


def para_hhmmss(segundos: int) -> str:
    """Converte segundos desde 00:00:00 em `"HH:MM:SS"`."""
    if not 0 <= segundos < SEGUNDOS_POR_DIA:
        raise ValueError(f"segundos fora de um dia: {segundos}")
    horas, resto = divmod(segundos, 3600)
    minutos, segundos_restantes = divmod(resto, 60)
    return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"
