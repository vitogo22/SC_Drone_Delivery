"""Lê os arquivos reais de `dados/`, como a execução final vai ler."""

from pathlib import Path

from surveyor.dominio.regras import Regras
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas

DADOS = Path(__file__).resolve().parents[2] / "dados"


def test_arquivo_do_professor_tem_374_pontos_com_o_campus_primeiro() -> None:
    regras = Regras()

    coordenadas = ler_coordenadas(DADOS / "coordenadas.csv", regras)

    assert len(coordenadas) == 374
    assert coordenadas[0].cep == regras.cep_campus
    assert all(coordenada.pode_pousar for coordenada in coordenadas)
