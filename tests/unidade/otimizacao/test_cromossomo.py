import dataclasses

import pytest

from surveyor.otimizacao.cromossomo import Cromossomo

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
