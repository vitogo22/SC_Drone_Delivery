"""Confere as coordenadas extras reais da equipe contra o arquivo do professor."""

from pathlib import Path

import pytest

from surveyor.dominio.regras import Regras
from surveyor.dominio.validacao.extras import validar_extra
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_extras

DADOS = Path(__file__).resolve().parents[2] / "dados"
MATRICULAS = ("2024100142", "2024100467")  # Vitor e Matheus, na ordem de dados/extras.csv


def test_ha_uma_extra_por_integrante_na_ordem_das_matriculas() -> None:
    extras = ler_extras(DADOS / "extras.csv")

    assert [extra.cep for extra in extras] == [matricula[-8:] for matricula in MATRICULAS]


@pytest.mark.parametrize("posicao", range(len(MATRICULAS)))
def test_extra_real_cumpre_as_regras_contra_o_professor_e_a_outra_extra(posicao: int) -> None:
    regras = Regras()
    professor = ler_coordenadas(DADOS / "coordenadas.csv", regras)
    extras = ler_extras(DADOS / "extras.csv")
    outras_extras = extras[:posicao] + extras[posicao + 1 :]

    violacoes = validar_extra(
        extras[posicao], MATRICULAS[posicao], [*professor, *outras_extras], regras
    )

    assert violacoes == []
