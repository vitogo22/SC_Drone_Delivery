import pytest

from surveyor.dominio.calculos.relogio import para_segundos
from surveyor.dominio.calculos.vento import (
    Vento,
    bloco_do_horario,
    blocos_de_vento,
    direcao_em_graus,
    velocidade_solo_kmh,
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


def test_exemplo_do_enunciado_pelo_triangulo_de_velocidades() -> None:
    vento_sse = Vento(9.0, direcao_em_graus("SSE"))

    v_solo = velocidade_solo_kmh(36, 39.5, vento_sse)

    # A soma vetorial do enunciado daria 41,0026532396 km/h e desviaria o drone do destino (A2).
    assert v_solo == pytest.approx(39.3372461072, abs=1e-9)


@pytest.mark.parametrize(
    ("vento", "v_solo_esperada"),
    [
        pytest.param(Vento(0.0, 0.0), 36.0, id="sem-vento"),
        pytest.param(Vento(9.0, 180.0), 45.0, id="a-favor"),  # vem do sul, empurra para o norte
        pytest.param(Vento(9.0, 0.0), 27.0, id="contra"),  # vem do norte, segura o drone
        pytest.param(Vento(9.0, 90.0), (36**2 - 9**2) ** 0.5, id="de-lado"),  # gasta para corrigir
    ],
)
def test_velocidade_em_solo_voando_para_o_norte(vento: Vento, v_solo_esperada: float) -> None:
    assert velocidade_solo_kmh(36, 0.0, vento) == pytest.approx(v_solo_esperada)


def test_vento_tao_forte_quanto_o_drone_e_rejeitado() -> None:
    with pytest.raises(ValueError, match="não deixa o drone"):
        velocidade_solo_kmh(36, 0.0, Vento(36.0, 0.0))
