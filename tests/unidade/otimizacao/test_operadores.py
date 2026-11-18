import random

import pytest

from surveyor.otimizacao.operadores import torneio

CUSTOS = (50.0, 10.0, 90.0, 30.0, 70.0, 20.0, 80.0, 40.0, 60.0, 100.0)  # o melhor é o índice 1


def test_torneio_com_todos_escolhe_o_de_menor_custo() -> None:
    # Minimização: vence o MENOR custo, não o maior.
    assert torneio(CUSTOS, len(CUSTOS), random.Random(1)) == 1


def test_o_pior_nunca_vence_um_torneio() -> None:
    # Os k participantes são distintos: o pior sempre perde para algum outro.
    sorteio = random.Random(2)

    vencedores = {torneio(CUSTOS, 2, sorteio) for _ in range(2000)}

    assert CUSTOS.index(max(CUSTOS)) not in vencedores


def test_torneio_de_3_da_ao_melhor_a_chance_de_3_em_n() -> None:
    # O melhor vence sempre que é sorteado: 1 - C(9, 3) / C(10, 3) = 3/10.
    sorteio = random.Random(3)

    vitorias = sum(torneio(CUSTOS, 3, sorteio) == 1 for _ in range(5000))

    assert vitorias / 5000 == pytest.approx(0.3, abs=0.03)


def test_mesma_semente_da_os_mesmos_vencedores() -> None:
    primeira = [torneio(CUSTOS, 3, random.Random(7)) for _ in range(5)]
    segunda = [torneio(CUSTOS, 3, random.Random(7)) for _ in range(5)]

    assert primeira == segunda


@pytest.mark.parametrize("k", [1, 11], ids=["menos de 2", "maior que a populacao"])
def test_torneio_exige_entre_2_e_n_participantes(k: int) -> None:
    with pytest.raises(ValueError, match="entre 2 e 10"):
        torneio(CUSTOS, k, random.Random(0))
