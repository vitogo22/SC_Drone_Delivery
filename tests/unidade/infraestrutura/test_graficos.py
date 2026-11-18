"""Gráfico de convergência a partir do progresso.csv gravado pelo monitor."""

from pathlib import Path

import pytest

from surveyor.dominio.erros import ErroDados
from surveyor.infraestrutura.graficos import grafico_convergencia, serie_de_convergencia
from surveyor.infraestrutura.logs.monitor_progresso import MonitorDeProgresso
from surveyor.otimizacao.progresso import EstatisticasDaGeracao

MELHORES = (2495.31, 2478.02, 2478.02, 2413.51)


def _progresso(pasta: Path) -> Path:
    caminho = pasta / "progresso.csv"
    with MonitorDeProgresso(caminho) as monitor:
        for geracao, melhor in enumerate(MELHORES):
            monitor.registrar(
                EstatisticasDaGeracao(geracao, melhor, 2 * melhor, 3 * melhor, 15, 53519, 0.5)
            )
    return caminho


def test_serie_tem_a_geracao_e_o_melhor_custo_de_cada_linha(tmp_path: Path) -> None:
    geracoes, melhores = serie_de_convergencia(_progresso(tmp_path))

    assert geracoes == [0, 1, 2, 3]
    assert melhores == list(MELHORES)


def test_grava_um_png(tmp_path: Path) -> None:
    saida = tmp_path / "convergencia.png"

    grafico_convergencia(_progresso(tmp_path), saida)

    assert saida.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_progresso_sem_geracoes_e_erro(tmp_path: Path) -> None:
    vazio = tmp_path / "progresso.csv"
    with MonitorDeProgresso(vazio):
        pass

    with pytest.raises(ErroDados, match="nenhuma geração"):
        grafico_convergencia(vazio, tmp_path / "convergencia.png")
