"""Executa o programa como o professor vai executar: `python -m surveyor`, em outro processo."""

import os
import subprocess
import sys
from pathlib import Path

from surveyor import __version__

SRC = Path(__file__).resolve().parents[2] / "src"


def _rodar(*argumentos: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "surveyor", *argumentos],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SRC)},
        check=False,
    )


def test_python_m_surveyor_responde_a_versao_sem_instalar() -> None:
    resultado = _rodar("--versao")

    assert resultado.returncode == 0
    assert __version__ in resultado.stdout


def test_ajuda_lista_os_comandos() -> None:
    resultado = _rodar("--help")

    assert resultado.returncode == 0
    assert "otimizar" in resultado.stdout
    assert "validar" in resultado.stdout
