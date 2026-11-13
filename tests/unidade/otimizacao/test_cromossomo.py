import dataclasses

import pytest

from surveyor.dominio.regras import Regras
from surveyor.dominio.simulador import DecisoesDeVoo
from surveyor.otimizacao.cromossomo import Cromossomo, decisoes_de_voo

CALENDARIO = (True, False, True, True, True, False, True)


def test_cromossomo_valido_guarda_ordem_velocidades_e_calendario() -> None:
    cromossomo = Cromossomo(ordem=(2, 0, 1), velocidades=(0, 11, 5, 3), calendario=CALENDARIO)

    assert cromossomo.ordem == (2, 0, 1)
    assert cromossomo.velocidades == (0, 11, 5, 3)
    assert cromossomo.calendario == CALENDARIO


@pytest.mark.parametrize(
    ("ordem", "velocidades", "calendario", "motivo"),
    [
        pytest.param((0, 0, 2), (0, 0, 0, 0), CALENDARIO, "permutação", id="ponto repetido"),
        pytest.param((0, 1, 3), (0, 0, 0, 0), CALENDARIO, "permutação", id="índice fora"),
        pytest.param((0, 1, 2), (0, 0, 0), CALENDARIO, "4 genes", id="sem a volta ao campus"),
        pytest.param((0, 1, 2), (0, 0, 0, 0, 0), CALENDARIO, "4 genes", id="gene sobrando"),
        pytest.param((0, 1, 2), (0, -1, 0, 0), CALENDARIO, "negativo", id="velocidade negativa"),
        pytest.param((0, 1, 2), (0, 0, 0, 0), (), "calendário vazio", id="sem dias"),
    ],
)
def test_cromossomo_mal_formado_e_rejeitado(
    ordem: tuple[int, ...],
    velocidades: tuple[int, ...],
    calendario: tuple[bool, ...],
    motivo: str,
) -> None:
    with pytest.raises(ValueError, match=motivo):
        Cromossomo(ordem, velocidades, calendario)


def test_cromossomo_e_imutavel_entao_o_filho_nunca_altera_o_pai() -> None:
    pai = Cromossomo(ordem=(1, 0), velocidades=(0, 1, 2), calendario=CALENDARIO)

    filho = dataclasses.replace(pai, velocidades=(3, 1, 2))

    with pytest.raises(dataclasses.FrozenInstanceError):
        pai.ordem = (0, 1)  # type: ignore[misc]  # o teste é justamente a atribuição proibida
    assert pai.velocidades == (0, 1, 2)
    assert filho.velocidades == (3, 1, 2)


def test_conversao_leva_a_velocidade_de_cada_ponto_para_o_trecho_que_chega_nele() -> None:
    # velocidade por ponto: 0 -> 36, 1 -> 56, 2 -> 80; volta ao campus -> 44
    cromossomo = Cromossomo(ordem=(2, 0, 1), velocidades=(0, 5, 11, 2), calendario=CALENDARIO)

    decisoes = decisoes_de_voo(cromossomo, Regras())

    assert decisoes == DecisoesDeVoo(
        rota=(2, 0, 1), velocidades_kmh=(80, 36, 56, 44), dias=(1, 3, 4, 5, 7)
    )


def test_conversao_rejeita_indice_de_velocidade_acima_do_ultimo() -> None:
    cromossomo = Cromossomo(ordem=(0,), velocidades=(0, 12), calendario=CALENDARIO)

    with pytest.raises(ValueError, match="0 a 11"):
        decisoes_de_voo(cromossomo, Regras())


def test_conversao_exige_um_bit_por_dia_do_prazo() -> None:
    cromossomo = Cromossomo(ordem=(0,), velocidades=(0, 0), calendario=CALENDARIO[:6])

    with pytest.raises(ValueError, match="7 dias"):
        decisoes_de_voo(cromossomo, Regras())
