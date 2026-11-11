"""Lê os arquivos reais de `dados/`, como a execução final vai ler."""

from pathlib import Path

from surveyor.dominio.calculos.vento import Vento
from surveyor.dominio.regras import Regras
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_vento

DADOS = Path(__file__).resolve().parents[2] / "dados"


def test_arquivo_do_professor_tem_374_pontos_com_o_campus_primeiro() -> None:
    regras = Regras()

    coordenadas = ler_coordenadas(DADOS / "coordenadas.csv", regras)

    assert len(coordenadas) == 374
    assert coordenadas[0].cep == regras.cep_campus
    assert all(coordenada.pode_pousar for coordenada in coordenadas)


def test_tabela_de_vento_real_tem_os_7_dias_e_5_blocos() -> None:
    tabela = ler_vento(DADOS / "vento.csv", Regras())

    assert len(tabela) == 7 * 5
    assert tabela[(1, 6)] == Vento(3.0, 247.5)  # primeira linha: 3 km/h de WSW
