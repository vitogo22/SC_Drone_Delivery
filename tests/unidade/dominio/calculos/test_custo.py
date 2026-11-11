import pytest

from surveyor.dominio.calculos.custo import tempo_trecho_s


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
