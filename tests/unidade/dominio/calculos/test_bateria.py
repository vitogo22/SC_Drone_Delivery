import pytest

from surveyor.dominio.calculos.bateria import autonomia_s
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
