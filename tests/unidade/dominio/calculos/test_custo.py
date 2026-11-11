import pytest

from surveyor.dominio.calculos.custo import custo_total, taxa_pouso_reais, tempo_trecho_s
from surveyor.dominio.calculos.relogio import para_segundos
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import ParametrosOperacao, Regras


@pytest.mark.parametrize(
    ("distancia_km", "v_solo_kmh", "esperado_s"),
    [
        (1.204, 36.0, 121),  # 120,4 s sobe para 121
        (1.2, 36.0, 120),  # 120 s exatos não sobem
    ],
)
def test_tempo_do_trecho_e_arredondado_para_cima(
    distancia_km: float, v_solo_kmh: float, esperado_s: int
) -> None:
    assert tempo_trecho_s(distancia_km, v_solo_kmh) == esperado_s


def test_ruido_de_ponto_flutuante_nao_sobe_um_segundo() -> None:
    distancia_km, v_solo_kmh = 1.2032, 36.096
    assert distancia_km / v_solo_kmh * 3600 == 120.00000000000003  # o ruído existe mesmo
    assert tempo_trecho_s(distancia_km, v_solo_kmh) == 120


@pytest.mark.parametrize(
    ("hora_final", "esperado_reais"),
    [
        ("06:02:52", 80.0),
        ("16:59:59", 80.0),
        ("17:00:00", 80.0),  # A11: 17:00:00 em ponto não é "após as 17:00:00"
        ("17:00:01", 160.0),
        ("19:00:00", 160.0),
    ],
)
def test_pouso_depois_das_17h_cobra_taxa_adicional(hora_final: str, esperado_reais: float) -> None:
    assert taxa_pouso_reais(para_segundos(hora_final), Regras()) == esperado_reais


@pytest.fixture
def plano_de_dois_trechos(campus: Coordenada, ponto: Coordenada) -> PlanoDeVoo:
    """Campus → ponto (foto sem pouso, 20 min) → campus (pouso às 17:30:00, 40 min)."""
    ida = Trecho(
        campus, ponto, dia=1, hora_inicial_s=para_segundos("16:30:00"),
        velocidade_kmh=36, pouso=False, hora_final_s=para_segundos("16:50:00"),
    )  # fmt: skip
    volta = Trecho(
        ponto, campus, dia=1, hora_inicial_s=para_segundos("16:50:00"),
        velocidade_kmh=36, pouso=True, hora_final_s=para_segundos("17:30:00"),
    )  # fmt: skip
    return PlanoDeVoo((ida, volta))


def test_custo_total_soma_as_horas_de_voo_e_os_pousos(plano_de_dois_trechos: PlanoDeVoo) -> None:
    # A4: 20 min + 40 min = 1 h no ar → 1 x R$ 80
    #     a foto sem pouso não paga taxa; o pouso às 17:30:00 paga R$ 80 + R$ 80 (A11)
    #     total = 80 + 160 = R$ 240
    operacao = ParametrosOperacao()
    assert custo_total(plano_de_dois_trechos, Regras(), operacao) == pytest.approx(240.0)


def test_custo_total_usa_o_valor_da_hora_da_operacao(plano_de_dois_trechos: PlanoDeVoo) -> None:
    # A4: 1 h x R$ 40 + R$ 160 do pouso
    operacao = ParametrosOperacao(valor_hora_reais=40.0)
    assert custo_total(plano_de_dois_trechos, Regras(), operacao) == pytest.approx(200.0)
