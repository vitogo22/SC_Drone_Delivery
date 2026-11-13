"""Executa o programa como o professor vai executar: `python -m surveyor`, em outro processo."""

import os
import subprocess
import sys
from pathlib import Path

from surveyor import __version__

RAIZ = Path(__file__).resolve().parents[2]
SRC = RAIZ / "src"


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
    assert "extras" in resultado.stdout


def test_extras_reais_sao_validas_e_saem_na_tabela(tmp_path: Path) -> None:
    resultado = _rodar(
        "--log-arquivo",
        str(tmp_path / "extras.log"),
        "extras",
        "--coordenadas",
        str(RAIZ / "dados" / "coordenadas.csv"),
        "--extras",
        str(RAIZ / "dados" / "extras.csv"),
    )

    assert resultado.returncode == 0, resultado.stderr
    linhas = resultado.stdout.splitlines()
    assert len(linhas) == 4  # cabeçalho, separador e um integrante por linha
    assert "| 2024100142 | 24100142 |" in linhas[2]
    assert "| 2024100467 | 24100467 |" in linhas[3]
