from pathlib import Path

from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.otimizacao.parametros import ParametrosGA


def test_entradas_padrao_ficam_na_pasta_dados() -> None:
    entrada = ArquivosDeEntrada()

    assert entrada.coordenadas == Path("dados/coordenadas.csv")
    assert entrada.extras == Path("dados/extras.csv")
    assert entrada.vento == Path("dados/vento.csv")


def test_execucao_completa_usa_o_ga_padrao_com_a_semente() -> None:
    assert Configuracao.para_execucao(semente=7).ga == ParametrosGA(semente=7)


def test_execucao_rapida_usa_o_ga_reduzido_com_a_semente() -> None:
    assert Configuracao.para_execucao(rapido=True, semente=7).ga == ParametrosGA.rapido(7)
