import random
from dataclasses import replace

import pytest

from surveyor.otimizacao.cromossomo import Cromossomo
from surveyor.otimizacao.operadores import Cruzamento, cruzar, erx, ox, pmx, torneio

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


# Exemplo clássico, corte nas posições 3 a 6: o segmento (3, 4, 5, 6) vem do pai 1.
PAI1 = (0, 1, 2, 3, 4, 5, 6, 7, 8)
PAI2 = (8, 2, 6, 7, 1, 5, 4, 0, 3)
CORTE = (3, 7)


def _e_permutacao(ordem: tuple[int, ...], n: int) -> bool:
    return sorted(ordem) == list(range(n))


def test_ox_copia_o_segmento_e_completa_na_ordem_do_outro_pai() -> None:
    # Depois do corte, o pai 2 lido a partir da posição 7 é 0 3 8 2 6 7 1 5 4; sem o
    # segmento fica 0 8 2 7 1, que preenche as posições 7, 8, 0, 1 e 2.
    ordem, do_pai1 = ox(PAI1, PAI2, CORTE)

    assert ordem == (2, 7, 1, 3, 4, 5, 6, 0, 8)
    assert do_pai1 == {3, 4, 5, 6}


def test_pmx_copia_o_segmento_e_resolve_os_conflitos_pelo_mapa() -> None:
    # Fora do segmento fica o gene do pai 2; o 6 já está no segmento e vira 4, que vira 1
    # (mapa 6->4->1); o 3 vira 7 (mapa 3->7).
    ordem, do_pai1 = pmx(PAI1, PAI2, CORTE)

    assert ordem == (8, 2, 1, 3, 4, 5, 6, 0, 7)
    assert do_pai1 == {3, 4, 5, 6}


def test_erx_com_pais_iguais_reproduz_o_ciclo() -> None:
    # Só existem as arestas do pai: o filho percorre o mesmo ciclo, num dos dois sentidos.
    sentidos = {(*PAI1,), (PAI1[0], *reversed(PAI1[1:]))}

    filhos = {erx(PAI1, PAI1, random.Random(semente))[0] for semente in range(20)}

    assert filhos <= sentidos


@pytest.mark.parametrize("semente", range(30))
def test_erx_sempre_gera_permutacao(semente: int) -> None:
    sorteio = random.Random(semente)
    pai1, pai2 = (tuple(sorteio.sample(range(12), 12)) for _ in range(2))

    ordem, do_pai1 = erx(pai1, pai2, sorteio)

    assert _e_permutacao(ordem, 12)
    assert do_pai1 <= set(ordem)


def _cromossomo(ordem: tuple[int, ...], velocidade: int, voa: bool) -> Cromossomo:
    return Cromossomo(ordem, (velocidade,) * (len(ordem) + 1), (voa,) * 7)


@pytest.mark.parametrize("metodo", list(Cruzamento))
def test_cruzar_gera_filho_valido_e_nao_altera_os_pais(metodo: Cruzamento) -> None:
    pai1, pai2 = _cromossomo(PAI1, 0, True), _cromossomo(PAI2, 11, False)
    copias = (replace(pai1), replace(pai2))

    filho = cruzar(pai1, pai2, metodo, random.Random(4))

    assert _e_permutacao(filho.ordem, len(PAI1))  # o Cromossomo também confere
    assert (pai1, pai2) == copias
    assert set(filho.velocidades) <= {0, 11}


def test_ox_a_velocidade_vem_do_pai_que_forneceu_o_ponto() -> None:
    # Pai 1 só com o índice 0 e pai 2 só com o 11: os pontos com 0 são o segmento do pai 1,
    # contíguo no filho e nas mesmas posições do pai 1 (bloco construtivo inteiro).
    pai1, pai2 = _cromossomo(PAI1, 0, True), _cromossomo(PAI2, 11, False)
    for semente in range(20):
        filho = cruzar(pai1, pai2, Cruzamento.OX, random.Random(semente))
        posicoes = [i for i, ponto in enumerate(filho.ordem) if filho.velocidades[ponto] == 0]

        assert posicoes == list(range(posicoes[0], posicoes[-1] + 1))
        assert [filho.ordem[i] for i in posicoes] == [PAI1[i] for i in posicoes]


def test_calendario_usa_cruzamento_uniforme() -> None:
    pai1, pai2 = _cromossomo(PAI1, 0, True), _cromossomo(PAI2, 11, False)

    calendarios = {
        cruzar(pai1, pai2, Cruzamento.OX, random.Random(s)).calendario for s in range(30)
    }

    assert len(calendarios) > 2  # dias misturados dos dois pais, não um calendário inteiro
