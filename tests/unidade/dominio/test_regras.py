import dataclasses

import pytest

from surveyor.dominio.erros import ErroConfiguracao
from surveyor.dominio.regras import ParametrosOperacao, Regras


def test_velocidades_sao_multiplos_de_4_entre_10_m_s_e_83_kmh() -> None:
    velocidades = Regras().velocidades_kmh

    assert velocidades == (36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80)
    assert min(velocidades) / 3.6 == pytest.approx(10.0)
    assert max(velocidades) <= 83


def test_autonomia_nominal_equivale_a_1h23min20s() -> None:
    assert Regras().autonomia_nominal_s == 1 * 3600 + 23 * 60 + 20


def test_janela_de_voo_e_horario_da_taxa_adicional() -> None:
    regras = Regras()

    assert regras.inicio_voos_s == 6 * 3600
    assert regras.inicio_taxa_adicional_s == 17 * 3600
    assert regras.limite_pouso_s == 19 * 3600


def test_regras_sao_imutaveis() -> None:
    regras = Regras()

    with pytest.raises(dataclasses.FrozenInstanceError):
        regras.fator_autonomia = 1.0  # type: ignore[misc]


def test_operacao_padrao_evita_a_taxa_das_17h() -> None:
    assert ParametrosOperacao().limite_operacional_s == Regras().inicio_taxa_adicional_s


@pytest.mark.parametrize(
    "campos",
    [
        {"valor_hora_reais": -1},
        {"reserva_bateria": -0.01},
        {"reserva_bateria": 1.0},
        {"limite_operacional_s": 6 * 3600},
        {"limite_operacional_s": 19 * 3600 + 1},
    ],
)
def test_parametros_operacao_fora_da_faixa_sao_rejeitados(campos: dict[str, float]) -> None:
    with pytest.raises(ErroConfiguracao):
        ParametrosOperacao(**campos)  # type: ignore[arg-type]
