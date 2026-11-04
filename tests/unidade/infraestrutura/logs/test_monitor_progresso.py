import csv
import logging
from pathlib import Path

import pytest

from surveyor.infraestrutura.logs.monitor_progresso import CAMPOS, MonitorDeProgresso
from surveyor.otimizacao.progresso import EstatisticasDaGeracao, ObservadorDeProgresso


def _geracao(numero: int, melhor: float) -> EstatisticasDaGeracao:
    return EstatisticasDaGeracao(
        geracao=numero,
        melhor_custo=melhor,
        custo_medio=melhor + 50,
        pior_custo=melhor + 100,
        pousos_do_melhor=12,
        tempo_voo_do_melhor_s=36000,
        segundos_decorridos=numero * 0.5,
    )


def test_toda_geracao_vira_uma_linha_do_csv(tmp_path: Path) -> None:
    arquivo = tmp_path / "resultados" / "progresso.csv"

    with MonitorDeProgresso(arquivo) as monitor:
        monitor.registrar(_geracao(0, 2000.0))
        monitor.registrar(_geracao(1, 1950.5))

    with arquivo.open(encoding="utf-8", newline="") as aberto:
        linhas = list(csv.DictReader(aberto))
    assert tuple(linhas[0]) == CAMPOS
    assert [linha["melhor_custo"] for linha in linhas] == ["2000.0", "1950.5"]


def test_log_info_so_na_geracao_zero_e_a_cada_intervalo(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)

    with MonitorDeProgresso(tmp_path / "progresso.csv", intervalo_log=10) as monitor:
        for numero in range(21):
            monitor.registrar(_geracao(numero, 2000.0 - numero))

    resumos = [registro.getMessage() for registro in caplog.records]
    assert [resumo.split(":")[0] for resumo in resumos] == ["Geração 0", "Geração 10", "Geração 20"]
    assert "| 12 pousos | 10.00 h de voo |" in resumos[0]


def test_melhora_do_melhor_custo_vai_para_o_debug(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)

    with MonitorDeProgresso(tmp_path / "progresso.csv", intervalo_log=100) as monitor:
        for numero, melhor in enumerate([2000.0, 2000.0, 1900.0]):
            monitor.registrar(_geracao(numero, melhor))

    melhoras = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
    assert melhoras == [
        "Geração 0: novo melhor custo 2000.00",
        "Geração 2: novo melhor custo 1900.00",
    ]


def test_registrar_fora_do_with_e_erro_de_uso(tmp_path: Path) -> None:
    monitor = MonitorDeProgresso(tmp_path / "progresso.csv")

    with pytest.raises(RuntimeError, match="dentro de `with"):
        monitor.registrar(_geracao(0, 1.0))


def test_intervalo_de_log_precisa_ser_positivo(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="intervalo_log"):
        MonitorDeProgresso(tmp_path / "progresso.csv", intervalo_log=0)


def test_monitor_cumpre_o_contrato_do_algoritmo(tmp_path: Path) -> None:
    """Vale para o mypy: o laço evolutivo aceita o monitor como ObservadorDeProgresso."""
    with MonitorDeProgresso(tmp_path / "progresso.csv") as monitor:
        observador: ObservadorDeProgresso = monitor
        observador.registrar(_geracao(0, 1.0))

    assert (tmp_path / "progresso.csv").exists()
