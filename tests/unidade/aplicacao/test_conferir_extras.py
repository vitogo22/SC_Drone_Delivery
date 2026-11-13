import math
from pathlib import Path

import pytest

from surveyor.aplicacao import conferir_extras
from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao, Integrante
from surveyor.dominio.erros import ErroDados

EQUIPE = (Integrante("Ana", "2011111111"), Integrante("Bia", "2022222222"))
# Campus e as duas extras no mesmo meridiano: as extras ficam a ~556 m e ~779 m do campus
# e a ~222 m uma da outra, então o ponto mais próximo de cada uma é a outra extra.
CAMPUS = "82821020,-49.2000000000000,-25.4000000000000\n"
EXTRA_ANA = "11111111,-49.2000000000000,-25.4050011111111\n"
EXTRA_BIA = "22222222,-49.2000000000000,-25.4070022222222\n"
CABECALHO = "cep,longitude,latitude\n"


@pytest.fixture
def entrada(tmp_path: Path) -> ArquivosDeEntrada:
    coordenadas = tmp_path / "coordenadas.csv"
    coordenadas.write_text(CABECALHO + CAMPUS, encoding="utf-8")
    extras = tmp_path / "extras.csv"
    extras.write_text(CABECALHO + EXTRA_ANA + EXTRA_BIA, encoding="utf-8")
    return ArquivosDeEntrada(coordenadas=coordenadas, extras=extras)


def test_cada_integrante_recebe_a_extra_da_mesma_posicao(entrada: ArquivosDeEntrada) -> None:
    conferencias = conferir_extras.executar(entrada, Configuracao(equipe=EQUIPE))

    assert [(c.integrante, c.extra.cep) for c in conferencias] == [
        (EQUIPE[0], "11111111"),
        (EQUIPE[1], "22222222"),
    ]
    assert all(c.violacoes == () for c in conferencias)


def test_ponto_mais_proximo_vem_da_base_consolidada(entrada: ArquivosDeEntrada) -> None:
    entre_extras_m = math.radians(0.0020011111111) * Configuracao().regras.raio_terra_km * 1000

    conferencias = conferir_extras.executar(entrada, Configuracao(equipe=EQUIPE))

    assert [c.mais_proximo.cep for c in conferencias] == ["22222222", "11111111"]
    assert [c.distancia_m for c in conferencias] == pytest.approx([entre_extras_m] * 2)


def test_extra_que_quebra_uma_regra_traz_a_violacao(entrada: ArquivosDeEntrada) -> None:
    equipe = (EQUIPE[0], Integrante("Bia", "2022222223"))

    ana, bia = conferir_extras.executar(entrada, Configuracao(equipe=equipe))

    assert ana.violacoes == ()
    assert any("CEP 22222222" in violacao for violacao in bia.violacoes)


def test_quantidade_de_extras_diferente_da_equipe_e_erro_de_dados(
    entrada: ArquivosDeEntrada,
) -> None:
    with pytest.raises(ErroDados, match=r"extras\.csv: 2 coordenadas extras para 1 integrante"):
        conferir_extras.executar(entrada, Configuracao(equipe=EQUIPE[:1]))
