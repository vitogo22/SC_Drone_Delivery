import pytest

from surveyor.dominio.calculos.vento import Vento, direcao_em_graus


@pytest.mark.parametrize(
    ("nome", "graus"),
    [
        ("N", 0.0),
        ("NE", 45.0),
        ("ENE", 67.5),
        ("E", 90.0),
        ("SSE", 157.5),
        ("S", 180.0),
        ("SSW", 202.5),
        ("WSW", 247.5),
        ("NNW", 337.5),
    ],
)
def test_direcao_em_graus_segue_a_rosa_dos_ventos_de_16_pontos(nome: str, graus: float) -> None:
    assert direcao_em_graus(nome) == graus


@pytest.mark.parametrize("nome", ["", "X", "NNNE", "se", "NO"])
def test_direcao_desconhecida_e_rejeitada(nome: str) -> None:
    with pytest.raises(ValueError, match="direção do vento desconhecida"):
        direcao_em_graus(nome)


@pytest.mark.parametrize(
    ("vem_de_graus", "sopra_para_graus"),
    [
        (157.5, 337.5),  # vento de SSE sopra para NNW
        (0.0, 180.0),
        (180.0, 0.0),  # e não 360
        (247.5, 67.5),
    ],
)
def test_vento_sopra_para_o_lado_oposto_de_onde_vem(
    vem_de_graus: float, sopra_para_graus: float
) -> None:
    assert Vento(9.0, vem_de_graus).sopra_para_graus == sopra_para_graus
