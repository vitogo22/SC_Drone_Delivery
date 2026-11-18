"""Gráfico de convergência a partir do progresso.csv gravado pelo monitor."""

from pathlib import Path

import pytest

from surveyor.dominio.erros import ErroDados
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.infraestrutura.graficos import (
    figura_rota,
    grafico_convergencia,
    grafico_rota,
    serie_de_convergencia,
)
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


CAMPUS = Coordenada("82821020", "-25.4000000000000", "-49.2000000000000")
A = Coordenada("80000001", "-25.3900000000000", "-49.2000000000000")
B = Coordenada("80000002", "-25.3800000000000", "-49.1900000000000")
EXTRA = Coordenada("24100467", "-25.3950000000000", "-49.2050000000000", pode_pousar=False)
# Dia 2: campus -> A (pouso no fim do dia); dia 5: A -> extra -> B -> campus.
PLANO = PlanoDeVoo(
    (
        Trecho(CAMPUS, A, 2, 21600, 36, True, 21900),
        Trecho(A, EXTRA, 5, 21600, 36, False, 21800),
        Trecho(EXTRA, B, 5, 21800, 36, False, 22000),
        Trecho(B, CAMPUS, 5, 22000, 36, True, 22500),
    )
)


def test_mapa_tem_um_painel_por_dia_de_voo() -> None:
    figura = figura_rota(PLANO)

    titulos = [eixo.get_title(loc="left") for eixo in figura.axes]
    assert titulos == ["Dia 2: 1 trecho, 1 pouso", "Dia 5: 3 trechos, 1 pouso"]


def test_mapa_grava_um_png(tmp_path: Path) -> None:
    saida = tmp_path / "rota.png"

    grafico_rota(PLANO, saida)

    assert saida.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_mapa_de_plano_vazio_e_erro() -> None:
    with pytest.raises(ValueError, match="plano vazio"):
        figura_rota(PlanoDeVoo(()))


def test_mapa_com_4_dias_esconde_os_paineis_que_sobram_na_grade() -> None:
    # 3 painéis por linha: 4 dias ocupam 2 linhas, e os 2 últimos espaços ficam vazios.
    ida_e_volta = [Trecho(CAMPUS, A, dia, 21600, 36, True, 21900) for dia in (1, 2, 3)]
    plano = PlanoDeVoo((*ida_e_volta, Trecho(A, CAMPUS, 4, 21600, 36, True, 21900)))

    figura = figura_rota(plano)

    assert len(figura.axes) == 6
    assert sum(eixo.get_visible() for eixo in figura.axes) == 4
