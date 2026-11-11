"""Fixtures usadas por mais de um arquivo de teste."""

import pytest

from surveyor.dominio.modelos import Coordenada


@pytest.fixture
def campus() -> Coordenada:
    """Campus com coordenadas fictícias (os testes não dependem do arquivo do AVA)."""
    return Coordenada("82821020", "-25.4000000000000", "-49.2000000000000")


@pytest.fixture
def ponto() -> Coordenada:
    """Um ponto qualquer da lista, com coordenadas fictícias."""
    return Coordenada("80000000", "-25.4100000000000", "-49.2100000000000")
