"""População inicial: vizinho mais próximo (puro e perturbado) + rotas aleatórias."""

import random

from surveyor.dominio.calculos.vento import Vento, blocos_de_vento
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.dominio.simulador import Cenario
from surveyor.otimizacao.parametros import ParametrosGA
from surveyor.otimizacao.populacao import populacao_inicial, vizinho_mais_proximo

# Todos no meridiano do campus (-25.40): a distância é proporcional à diferença de latitude.
CAMPUS = Coordenada("82821020", "-25.4000000000000", "-49.2000000000000")
C = Coordenada("80000003", "-25.3700000000000", "-49.2000000000000")  # índice 0
A = Coordenada("80000001", "-25.3900000000000", "-49.2000000000000")  # índice 1
D = Coordenada("80000004", "-25.4150000000000", "-49.2000000000000")  # índice 2
B = Coordenada("80000002", "-25.3800000000000", "-49.2000000000000")  # índice 3


def _cenario() -> Cenario:
    regras = Regras()
    vento = {
        (dia, bloco): Vento(0, 0)
        for dia in range(1, regras.prazo_dias + 1)
        for bloco in blocos_de_vento(regras)
    }
    return Cenario.montar(CAMPUS, (C, A, D, B), vento, regras, ParametrosOperacao())


def test_vizinho_mais_proximo_sai_do_campus() -> None:
    # campus -> A (0,01°) -> B -> C, e só então D, que fica ao sul do campus.
    assert vizinho_mais_proximo(_cenario()) == (1, 3, 0, 2)


def test_vizinho_mais_proximo_a_partir_de_um_ponto() -> None:
    # Começa em D: o mais perto dele é A (o campus não entra na ordem).
    assert vizinho_mais_proximo(_cenario(), inicio=2) == (2, 1, 3, 0)


def test_populacao_tem_o_tamanho_e_comeca_pelo_vizinho_mais_proximo() -> None:
    parametros = ParametrosGA(tamanho_populacao=20, proporcao_vizinho_mais_proximo=0.15)

    populacao = populacao_inicial(_cenario(), parametros, random.Random(1))

    assert len(populacao) == 20
    assert populacao[0].ordem == (1, 3, 0, 2)
    # 15% de 20 = 3 rotas de vizinho mais próximo: a pura e 2 que começam num ponto sorteado.
    gulosas = {vizinho_mais_proximo(_cenario(), inicio=i) for i in range(4)}
    assert all(individuo.ordem in gulosas for individuo in populacao[1:3])


def test_velocidades_iniciais_de_36_a_52_e_todos_os_dias_ligados() -> None:
    populacao = populacao_inicial(_cenario(), ParametrosGA(tamanho_populacao=30), random.Random(2))

    indices = {indice for individuo in populacao for indice in individuo.velocidades}
    assert indices == {0, 1, 2, 3, 4}  # 36, 40, 44, 48 e 52 km/h
    assert all(individuo.calendario == (True,) * 7 for individuo in populacao)


def test_mesma_semente_da_a_mesma_populacao() -> None:
    parametros = ParametrosGA(tamanho_populacao=10)

    primeira = populacao_inicial(_cenario(), parametros, random.Random(5))
    segunda = populacao_inicial(_cenario(), parametros, random.Random(5))

    assert primeira == segunda
