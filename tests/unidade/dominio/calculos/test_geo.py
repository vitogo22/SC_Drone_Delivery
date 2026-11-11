import math

import pytest

from surveyor.dominio.calculos.geo import distancia_km, rumo_graus
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import Regras

# Coordenadas fictícias perto de Curitiba (os testes não dependem do arquivo do AVA).
CENTRO = Coordenada("10000000", "-25.0000000000000", "-49.0000000000000")
UM_GRAU_AO_SUL = Coordenada("20000000", "-26.0000000000000", "-49.0000000000000")
CAMPUS = Coordenada("82821020", "-25.4233146347775", "-49.2160678044742")
OUTRO_PONTO = Coordenada("81350686", "-25.4936598469491", "-49.3400481020638")


def test_distancia_de_um_grau_de_latitude() -> None:
    # 2·π·6371 / 360: só dá este valor com R = 6371 km e graus convertidos para radianos (A19).
    assert distancia_km(CENTRO, UM_GRAU_AO_SUL, Regras()) == pytest.approx(111.19492664455873)


def test_distancia_usa_o_raio_das_regras() -> None:
    regras = Regras(raio_terra_km=1.0)

    assert distancia_km(CENTRO, UM_GRAU_AO_SUL, regras) == pytest.approx(math.pi / 180)


def test_distancia_de_um_ponto_ate_ele_mesmo_e_zero() -> None:
    assert distancia_km(CAMPUS, CAMPUS, Regras()) == 0


def test_distancia_e_a_mesma_nos_dois_sentidos() -> None:
    regras = Regras()

    assert distancia_km(CAMPUS, OUTRO_PONTO, regras) == distancia_km(OUTRO_PONTO, CAMPUS, regras)


@pytest.mark.parametrize(
    ("latitude", "longitude", "rumo_esperado"),
    [
        pytest.param("-24.9000000000000", "-49.0000000000000", 0.0, id="norte"),
        pytest.param("-25.1000000000000", "-49.0000000000000", 180.0, id="sul"),
        pytest.param("-25.0000000000000", "-48.9000000000000", 90.0, id="leste"),
        pytest.param("-25.0000000000000", "-49.1000000000000", 270.0, id="oeste"),
    ],
)
def test_rumo_a_partir_do_norte_em_sentido_horario(
    latitude: str, longitude: str, rumo_esperado: float
) -> None:
    destino = Coordenada("30000000", latitude, longitude)

    # Leste e oeste não dão exatamente 90 e 270: o caminho mais curto na esfera é um arco.
    assert rumo_graus(CENTRO, destino) == pytest.approx(rumo_esperado, abs=0.05)


def test_rumo_fica_entre_0_e_360() -> None:
    # Para sudoeste, atan2 devolve um ângulo negativo, que precisa virar o equivalente em 0..360.
    destino = Coordenada("30000000", "-25.1000000000000", "-49.1000000000000")

    rumo = rumo_graus(CENTRO, destino)

    assert 180 < rumo < 270
