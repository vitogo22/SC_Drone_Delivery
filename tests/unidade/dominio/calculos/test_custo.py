import pytest

from surveyor.dominio.calculos.custo import taxa_pouso_reais, tempo_trecho_s
from surveyor.dominio.calculos.relogio import para_segundos
from surveyor.dominio.regras import Regras


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
