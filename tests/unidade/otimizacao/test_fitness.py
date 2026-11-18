"""Fitness: custo do plano + penalidade pelos trechos que faltaram (plano inválido).

O cenário é o caso feliz de test_simulador.py: campus -> A -> B -> C -> campus, vento de
9 km/h vindo do sul, 1044 s no ar e um pouso (R$ 103,20).
"""

import pytest

from surveyor.dominio.calculos.custo import custo_total
from surveyor.dominio.calculos.vento import Vento, blocos_de_vento
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.dominio.simulador import Cenario
from surveyor.otimizacao.cromossomo import Cromossomo
from surveyor.otimizacao.fitness import avaliar, teto_de_custo_valido, tratar_invalido
from surveyor.otimizacao.operadores import Invalidos

CAMPUS = Coordenada("82821020", "-25.4000000000000", "-49.2000000000000")
A = Coordenada("80000001", "-25.3900000000000", "-49.2000000000000")
B = Coordenada("80000002", "-25.3800000000000", "-49.2000000000000")
C = Coordenada("80000003", "-25.3700000000000", "-49.2000000000000")
# Chega a A a 36 km/h (índice 0), a B a 40 (1), a C a 44 (2) e volta a 36 (0); voa só no dia 1.
SO_DIA_1 = (True, False, False, False, False, False, False)
CERTO = Cromossomo((0, 1, 2), (0, 1, 2, 0), SO_DIA_1)


def _cenario(operacao: ParametrosOperacao | None = None) -> Cenario:
    regras = Regras()
    vento = {
        (dia, bloco): Vento(9, 180)
        for dia in range(1, regras.prazo_dias + 1)
        for bloco in blocos_de_vento(regras)
    }
    return Cenario.montar(CAMPUS, (A, B, C), vento, regras, operacao or ParametrosOperacao())


def test_teto_e_o_custo_maximo_de_um_plano_valido() -> None:
    # 7 dias x 13 h no ar x R$ 80 + 4 trechos x (R$ 80 + R$ 80 depois das 17h)
    assert teto_de_custo_valido(_cenario()) == pytest.approx(7 * 13 * 80 + 4 * 160)


def test_plano_valido_tem_fitness_igual_ao_custo() -> None:
    avaliacao = avaliar(CERTO, _cenario())

    assert avaliacao.valido
    assert avaliacao.custo == pytest.approx(1044 / 3600 * 80 + 80)  # A4: R$ 103,20


def test_plano_invalido_paga_o_teto_por_trecho_que_faltou() -> None:
    # Operação até 06:06:40: depois de A já não dá para pousar em B; sem outro dia, para ali.
    cenario = _cenario(ParametrosOperacao(limite_operacional_s=22000))

    avaliacao = avaliar(CERTO, cenario)

    assert not avaliacao.valido
    assert len(avaliacao.plano.trechos) == 1  # campus -> A, com pouso
    esperado = custo_total(avaliacao.plano, cenario.regras, cenario.operacao)
    assert avaliacao.custo == pytest.approx(esperado + 3 * teto_de_custo_valido(cenario))


def test_valido_vence_invalido_e_invalido_que_vai_mais_longe_vence_o_outro() -> None:
    cenario = _cenario(ParametrosOperacao(limite_operacional_s=22000))
    nenhum_dia = Cromossomo((0, 1, 2), (0, 1, 2, 0), (False,) * 7)

    valido = avaliar(CERTO, _cenario()).custo
    parou_em_a = avaliar(CERTO, cenario).custo
    nem_saiu = avaliar(nenhum_dia, cenario).custo

    assert valido < parou_em_a < nem_saiu


def test_penalidade_nao_muda_nada() -> None:
    cenario = _cenario(ParametrosOperacao(limite_operacional_s=22000))
    avaliacao = avaliar(CERTO, cenario)

    assert tratar_invalido(CERTO, avaliacao, cenario, Invalidos.PENALIDADE) == (CERTO, avaliacao)


def test_pena_de_morte_da_a_todo_invalido_o_mesmo_pior_custo() -> None:
    cenario = _cenario(ParametrosOperacao(limite_operacional_s=22000))
    nenhum_dia = Cromossomo((0, 1, 2), (0, 1, 2, 0), (False,) * 7)
    pior = 4 * teto_de_custo_valido(cenario)  # todos os trechos faltando

    custos = [
        tratar_invalido(c, avaliar(c, cenario), cenario, Invalidos.MORTE)[1].custo
        for c in (CERTO, nenhum_dia)
    ]

    assert custos == [pytest.approx(pior), pytest.approx(pior)]


def test_valido_passa_intacto_por_qualquer_tratamento() -> None:
    cenario = _cenario()
    avaliacao = avaliar(CERTO, cenario)

    for modo in Invalidos:
        assert tratar_invalido(CERTO, avaliacao, cenario, modo) == (CERTO, avaliacao)


def test_reparo_liga_os_dias_e_refaz_o_resto_da_rota_pelo_vizinho_mais_proximo() -> None:
    # Nenhum dia ligado: o plano nem sai do campus. O reparo liga os 7 dias e refaz a rota
    # de forma gulosa a partir de onde o plano parou (aqui, o campus): A, B e C.
    cenario = _cenario()
    parado = Cromossomo((2, 0, 1), (0, 1, 2, 0), (False,) * 7)
    avaliacao = avaliar(parado, cenario)
    assert avaliacao.plano.trechos == ()

    reparado, nova = tratar_invalido(parado, avaliacao, cenario, Invalidos.REPARO)

    assert reparado.ordem == (0, 1, 2)
    assert reparado.calendario == (True,) * 7
    assert reparado.velocidades == parado.velocidades  # a velocidade é do ponto: não muda
    assert nova == avaliar(reparado, cenario)
    assert nova.valido


def test_reparo_mantem_o_que_ja_foi_voado() -> None:
    # Operação até 06:06:40 e só o dia 1: o plano pousa em A e para ali (inválido).
    cenario = _cenario(ParametrosOperacao(limite_operacional_s=22000))
    cromossomo = Cromossomo((0, 2, 1), (0, 1, 2, 0), SO_DIA_1)
    avaliacao = avaliar(cromossomo, cenario)
    voados = len(avaliacao.plano.trechos)

    reparado, _ = tratar_invalido(cromossomo, avaliacao, cenario, Invalidos.REPARO)

    assert voados == 1
    assert reparado.ordem == (0, 1, 2)  # A fica; de A, o mais perto é B, depois C
