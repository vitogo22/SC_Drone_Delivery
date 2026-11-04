"""Política de logs do projeto. É aplicada uma única vez, pela interface (CLI).

| Destino | Nível | Formato | Para quê |
|---|---|---|---|
| terminal | escolhido na CLI (padrão INFO) | curto | acompanhar a execução |
| `logs/surveyor_<data>_<hora>.log` | DEBUG | completo, com o módulo | diagnóstico e evidência |

O que registrar em cada nível:
- ERROR: a execução não pôde continuar (erro esperado) ou o plano viola uma regra.
- WARNING: situação aceitável, mas suspeita, que alguém deveria olhar.
- INFO: marcos: parâmetros da execução, dados carregados, progresso a cada N gerações,
  resultado final e arquivos gravados.
- DEBUG: detalhes de decisão (ex.: pouso inserido pelo simulador). Nunca uma linha por
  avaliação de indivíduo: o laço do GA roda centenas de milhares de vezes.

Os demais módulos só fazem `logger = logging.getLogger(__name__)` e nunca configuram nada.
"""

import logging
from datetime import datetime
from pathlib import Path

NIVEIS = ("DEBUG", "INFO", "WARNING", "ERROR")
PASTA_LOGS = Path("logs")
FORMATO_TERMINAL = "%(asctime)s %(levelname)-7s %(message)s"
FORMATO_ARQUIVO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FORMATO_HORA_TERMINAL = "%H:%M:%S"
FORMATO_DATA_ARQUIVO = "%Y-%m-%d %H:%M:%S"


def arquivo_da_execucao(inicio: datetime, pasta: Path = PASTA_LOGS) -> Path:
    """Um arquivo de log por execução, nomeado pelo horário de início."""
    return pasta / f"surveyor_{inicio:%Y%m%d_%H%M%S}.log"


def configurar_logging(nivel_terminal: str = "INFO", arquivo: Path | None = None) -> None:
    """Terminal no nível pedido e, se `arquivo` for informado, tudo (DEBUG) nele."""
    if nivel_terminal not in NIVEIS:
        raise ValueError(f"nível de log inválido: {nivel_terminal!r}; use um de {NIVEIS}")

    raiz = logging.getLogger()
    for antigo in raiz.handlers[:]:
        raiz.removeHandler(antigo)
        antigo.close()

    terminal = logging.StreamHandler()
    terminal.setLevel(nivel_terminal)
    terminal.setFormatter(logging.Formatter(FORMATO_TERMINAL, FORMATO_HORA_TERMINAL))
    raiz.addHandler(terminal)
    raiz.setLevel(nivel_terminal)

    if arquivo is not None:
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        em_arquivo = logging.FileHandler(arquivo, encoding="utf-8")
        em_arquivo.setLevel(logging.DEBUG)
        em_arquivo.setFormatter(logging.Formatter(FORMATO_ARQUIVO, FORMATO_DATA_ARQUIVO))
        raiz.addHandler(em_arquivo)
        raiz.setLevel(logging.DEBUG)
