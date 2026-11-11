import math

import pytest

from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import Regras
from surveyor.dominio.validacao.extras import validar_extra

MATRICULA = "2024100467"
LATITUDE = "-25.4387124100467"  # 13 casas, terminando com os 8 últimos dígitos da matrícula
LONGITUDE = "-49.2000000000000"


def _extra(
    cep: str = "24100467", latitude: str = LATITUDE, longitude: str = LONGITUDE
) -> Coordenada:
    return Coordenada(cep, latitude, longitude, pode_pousar=False)


def _ao_norte(metros: float, *, do_professor: bool = True) -> Coordenada:
    """Ponto `metros` ao norte de LATITUDE, na mesma longitude (meridiano: Haversine = R x dφ)."""
    delta_graus = math.degrees(metros / 1000 / Regras().raio_terra_km)
    latitude = f"{float(LATITUDE) + delta_graus:.13f}"
    return Coordenada("80000000", latitude, LONGITUDE, pode_pousar=do_professor)


@pytest.mark.parametrize(
    ("extra", "base"),
    [
        pytest.param(_extra(), [_ao_norte(101)], id="a 101 m do professor"),
        pytest.param(_extra(), [_ao_norte(1499)], id="a 1499 m do professor"),
        pytest.param(
            _extra(), [_ao_norte(300, do_professor=False), _ao_norte(500)], id="outra extra a 300 m"
        ),
        pytest.param(
            _extra(latitude="-25.4387100000000", longitude="-49.2000024100467"),
            [_ao_norte(500)],
            id="matrícula no final da longitude",
        ),
    ],
)
def test_extra_que_cumpre_todas_as_regras_nao_tem_violacoes(
    extra: Coordenada, base: list[Coordenada]
) -> None:
    assert validar_extra(extra, MATRICULA, base, Regras()) == []


@pytest.mark.parametrize(
    ("extra", "base", "motivo"),
    [
        pytest.param(
            _extra(latitude="-25.438724100467"), [_ao_norte(500)], "12 casas", id="latitude 12"
        ),
        pytest.param(
            _extra(longitude="-49.200000000000"), [_ao_norte(500)], "12 casas", id="longitude 12"
        ),
        pytest.param(
            _extra(longitude="-49.20000000000000"), [_ao_norte(500)], "14 casas", id="longitude 14"
        ),
        pytest.param(
            _extra(latitude="-25.4387124100468"), [_ao_norte(500)], "24100467", id="final errado"
        ),
        pytest.param(_extra(cep="24100468"), [_ao_norte(500)], "CEP 24100468", id="CEP errado"),
        pytest.param(_extra(), [_ao_norte(99)], "99.0 m", id="a 99 m do professor"),
        pytest.param(
            _extra(),
            [_ao_norte(99, do_professor=False), _ao_norte(500)],
            "99.0 m",
            id="a 99 m de outra extra",
        ),
        pytest.param(_extra(), [_ao_norte(1501)], "1501.0 m", id="a 1501 m do professor"),
        pytest.param(  # A12: só os pontos do professor contam para os 1500 m
            _extra(),
            [_ao_norte(300, do_professor=False), _ao_norte(1501)],
            "1501.0 m",
            id="perto só de outra extra",
        ),
    ],
)
def test_extra_que_quebra_uma_regra_e_rejeitada(
    extra: Coordenada, base: list[Coordenada], motivo: str
) -> None:
    violacoes = validar_extra(extra, MATRICULA, base, Regras())

    assert len(violacoes) == 1
    assert motivo in violacoes[0]


def test_todas_as_violacoes_sao_listadas_juntas() -> None:
    extra = _extra(cep="24100468", latitude="-25.438724100467")

    assert len(validar_extra(extra, MATRICULA, [_ao_norte(1501)], Regras())) == 3
