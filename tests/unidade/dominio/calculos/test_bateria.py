import pytest

from surveyor.dominio.calculos.bateria import autonomia_s, consumo
from surveyor.dominio.regras import Regras


@pytest.mark.parametrize(
    ("v_kmh", "esperado_s"),
    [
        (36, 5000.0),
        (48, 2812.5),  # A16: a tabela do enunciado arredonda para 2813
        (60, 1800.0),
        (72, 1250.0),
    ],
)
def test_autonomia_sem_fator_reproduz_a_tabela_do_enunciado(v_kmh: int, esperado_s: float) -> None:
    assert autonomia_s(v_kmh, Regras(fator_autonomia=1.0)) == pytest.approx(esperado_s)


@pytest.mark.parametrize(("v_kmh", "esperado_s"), [(36, 5700.0), (80, 1154.25)])
def test_autonomia_padrao_multiplica_pelo_fator_1_14(v_kmh: int, esperado_s: float) -> None:
    # A3
    assert autonomia_s(v_kmh, Regras()) == pytest.approx(esperado_s)


@pytest.mark.parametrize("v_kmh", [0, 32, 83, 84])
def test_velocidade_fora_das_ajustaveis_e_rejeitada(v_kmh: int) -> None:
    # A7: só 36, 40, ..., 80 km/h
    with pytest.raises(ValueError, match="velocidade"):
        autonomia_s(v_kmh, Regras())


@pytest.mark.parametrize(
    ("duracao_s", "v_kmh", "esperado"),
    [
        (5700, 36, 1.0),  # a autonomia inteira esvazia a bateria
        (570, 36, 0.1),
        (2850, 36, 0.5),
        (1154, 80, 1154 / 1154.25),
    ],
)
def test_consumo_e_a_fracao_da_autonomia_gasta(duracao_s: int, v_kmh: int, esperado: float) -> None:
    assert consumo(duracao_s, v_kmh, Regras()) == pytest.approx(esperado)


@pytest.mark.parametrize(("parada_s", "esperado"), [(60, 60 / 1154.25), (172, 172 / 1154.25)])
def test_parada_consome_na_taxa_da_velocidade_do_trecho_que_chega(
    parada_s: int, esperado: float
) -> None:
    # A1: depois de um trecho a 80 km/h, a parada gasta na taxa de A(80)
    assert consumo(parada_s, 80, Regras()) == pytest.approx(esperado)


def test_mesma_parada_gasta_mais_depois_de_um_trecho_mais_rapido() -> None:
    # A1: a opção mais segura, porque a autonomia cai com a velocidade
    assert consumo(60, 80, Regras()) > consumo(60, 36, Regras())


def test_consumo_rejeita_velocidade_nao_ajustavel() -> None:
    with pytest.raises(ValueError, match="velocidade"):
        consumo(60, 83, Regras())
