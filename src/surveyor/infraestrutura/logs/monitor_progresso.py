"""Monitor de progresso do algoritmo genético (implementa `ObservadorDeProgresso`).

Regras:
- toda geração vira uma linha no CSV (evidência de execução e base do gráfico de convergência);
- o log recebe um resumo INFO na geração 0 e a cada `intervalo_log` gerações;
- cada melhora do melhor custo vai para o log em DEBUG (fica no arquivo, não polui o terminal).
"""

from __future__ import annotations

import csv
import logging
import math
from dataclasses import asdict, fields
from pathlib import Path
from typing import TextIO

from surveyor.otimizacao.progresso import EstatisticasDaGeracao

logger = logging.getLogger(__name__)

CAMPOS = tuple(campo.name for campo in fields(EstatisticasDaGeracao))


class MonitorDeProgresso:
    """Grava as estatísticas de cada geração em CSV e resume no log. Use dentro de `with`."""

    def __init__(self, arquivo_csv: Path, intervalo_log: int = 50) -> None:
        if intervalo_log < 1:
            raise ValueError(f"intervalo_log deve ser >= 1: {intervalo_log}")
        self._arquivo_csv = arquivo_csv
        self._intervalo_log = intervalo_log
        self._melhor_custo = math.inf
        self._arquivo: TextIO | None = None
        self._escritor: csv.DictWriter[str] | None = None

    def __enter__(self) -> MonitorDeProgresso:
        self._arquivo_csv.parent.mkdir(parents=True, exist_ok=True)
        self._arquivo = self._arquivo_csv.open("w", newline="", encoding="utf-8")
        self._escritor = csv.DictWriter(self._arquivo, fieldnames=CAMPOS)
        self._escritor.writeheader()
        return self

    def __exit__(self, *_: object) -> None:
        assert self._arquivo is not None, "o Python só chama __exit__ depois de __enter__"
        self._arquivo.close()
        self._arquivo = self._escritor = None

    def registrar(self, estatisticas: EstatisticasDaGeracao) -> None:
        """Grava a geração no CSV e decide o que vai para o log."""
        if self._escritor is None:
            raise RuntimeError("use o monitor dentro de `with MonitorDeProgresso(...) as monitor:`")
        self._escritor.writerow(asdict(estatisticas))

        if estatisticas.melhor_custo < self._melhor_custo:
            self._melhor_custo = estatisticas.melhor_custo
            logger.debug(
                "Geração %d: novo melhor custo %.2f",
                estatisticas.geracao,
                estatisticas.melhor_custo,
            )
        if estatisticas.geracao % self._intervalo_log == 0:
            logger.info(
                "Geração %d: melhor %.2f | média %.2f | %d pousos | %.2f h de voo | %.0f s",
                estatisticas.geracao,
                estatisticas.melhor_custo,
                estatisticas.custo_medio,
                estatisticas.pousos_do_melhor,
                estatisticas.tempo_voo_do_melhor_s / 3600,
                estatisticas.segundos_decorridos,
            )
