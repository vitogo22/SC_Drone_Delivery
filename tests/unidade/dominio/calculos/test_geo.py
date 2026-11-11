import math

import pytest

from surveyor.dominio.calculos.geo import distancia_km
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
