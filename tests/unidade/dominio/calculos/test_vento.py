import pytest

from surveyor.dominio.calculos.relogio import para_segundos
from surveyor.dominio.calculos.vento import (
    Vento,
    bloco_do_horario,
    blocos_de_vento,
    direcao_em_graus,
)
from surveyor.dominio.regras import Regras


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


def test_blocos_usados_comecam_as_6_9_12_15_e_18() -> None:
    # A coluna 21h existe na tabela, mas nunca é usada: a última saída possível é 18:59:59 (A15).
    assert blocos_de_vento(Regras()) == (6, 9, 12, 15, 18)


@pytest.mark.parametrize(
    ("hora_saida", "bloco"),
    [
        ("06:00:00", 6),
        ("08:59:00", 6),
        ("09:00:00", 9),
        ("09:21:00", 9),
        ("18:59:59", 18),
    ],
)
def test_bloco_do_vento_e_o_da_hora_de_saida(hora_saida: str, bloco: int) -> None:
    assert bloco_do_horario(para_segundos(hora_saida), Regras()) == bloco


@pytest.mark.parametrize("hora_saida", ["05:59:59", "19:00:00"])
def test_saida_fora_da_janela_de_voo_nao_tem_bloco(hora_saida: str) -> None:
    with pytest.raises(ValueError, match="fora da janela de voo"):
        bloco_do_horario(para_segundos(hora_saida), Regras())
