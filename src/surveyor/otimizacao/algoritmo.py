"""Laço evolutivo, elitismo e critérios de parada (Etapa 8).

`evoluir(cenario, parametros, observador)` cria a população inicial e, a cada geração:
registra as estatísticas no `ObservadorDeProgresso`, confere a parada (gerações, estagnação
do melhor custo ou tempo) e monta a próxima geração. A elite passa intacta, então, com
elitismo, o melhor da geração nunca piora; o resto vem da seleção, do cruzamento e da mutação.
Devolve o melhor indivíduo de todas as gerações (sem elitismo, ele pode ter se perdido). Toda
a aleatoriedade sai de um `random.Random(parametros.semente)`.
"""

import random
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from statistics import fmean

from surveyor.dominio.simulador import Cenario
from surveyor.otimizacao.cromossomo import Cromossomo
from surveyor.otimizacao.fitness import Avaliacao, avaliar, tratar_invalido
from surveyor.otimizacao.operadores import cruzar, mutar, preparar_selecao
from surveyor.otimizacao.parametros import ParametrosGA
from surveyor.otimizacao.populacao import populacao_inicial
from surveyor.otimizacao.progresso import EstatisticasDaGeracao, ObservadorDeProgresso


class Parada(Enum):
    """Por que o GA parou."""

    GERACOES = "número máximo de gerações"
    ESTAGNACAO = "gerações seguidas sem melhora"
    TEMPO = "tempo limite"


@dataclass(frozen=True, slots=True)
class ResultadoGA:
    """O melhor indivíduo encontrado, a avaliação dele e por que o GA parou."""

    melhor: Cromossomo
    avaliacao: Avaliacao
    geracoes: int
    parada: Parada


def evoluir(
    cenario: Cenario,
    parametros: ParametrosGA,
    observador: ObservadorDeProgresso,
    relogio: Callable[[], float] = time.perf_counter,
) -> ResultadoGA:
    """Roda o GA até um critério de parada e devolve o melhor indivíduo."""
    sorteio = random.Random(parametros.semente)
    inicio_s = relogio()

    def avaliar_e_tratar(individuo: Cromossomo) -> tuple[Cromossomo, Avaliacao]:
        avaliacao = avaliar(individuo, cenario)
        return tratar_invalido(individuo, avaliacao, cenario, parametros.invalidos)

    populacao, avaliacoes = _separar(
        avaliar_e_tratar(individuo) for individuo in populacao_inicial(cenario, parametros, sorteio)
    )
    tamanho_elite = round(parametros.proporcao_elite * parametros.tamanho_populacao)
    melhor: tuple[Cromossomo, Avaliacao] | None = None
    sem_melhora = 0
    geracao = 0
    while True:
        custos = [avaliacao.custo for avaliacao in avaliacoes]
        ranking = sorted(range(len(populacao)), key=custos.__getitem__)
        campeao = avaliacoes[ranking[0]]
        if melhor is None or campeao.custo < melhor[1].custo:
            melhor, sem_melhora = (populacao[ranking[0]], campeao), 0
        else:
            sem_melhora += 1
        decorrido_s = relogio() - inicio_s
        observador.registrar(
            EstatisticasDaGeracao(
                geracao=geracao,
                melhor_custo=campeao.custo,
                custo_medio=fmean(custos),
                pior_custo=custos[ranking[-1]],
                pousos_do_melhor=campeao.plano.quantidade_pousos,
                tempo_voo_do_melhor_s=campeao.plano.tempo_total_voo_s,
                segundos_decorridos=decorrido_s,
            )
        )
        parada = _parada(geracao, sem_melhora, decorrido_s, parametros)
        if parada is not None:
            return ResultadoGA(*melhor, geracao, parada)

        conhecidos = dict(zip(populacao, avaliacoes, strict=True))
        selecionar = preparar_selecao(custos, parametros.selecao, parametros.tamanho_torneio)
        proxima = [populacao[i] for i in ranking[:tamanho_elite]]
        while len(proxima) < parametros.tamanho_populacao:
            pai1, pai2 = populacao[selecionar(sorteio)], populacao[selecionar(sorteio)]
            proxima.append(_filho(pai1, pai2, parametros, cenario, sorteio))
        populacao, avaliacoes = _separar(
            (individuo, conhecidos[individuo])
            if individuo in conhecidos
            else avaliar_e_tratar(individuo)
            for individuo in proxima
        )
        geracao += 1


def _separar(
    pares: Iterable[tuple[Cromossomo, Avaliacao]],
) -> tuple[list[Cromossomo], list[Avaliacao]]:
    """Indivíduos e avaliações em duas listas alinhadas."""
    individuos: list[Cromossomo] = []
    avaliacoes: list[Avaliacao] = []
    for individuo, avaliacao in pares:
        individuos.append(individuo)
        avaliacoes.append(avaliacao)
    return individuos, avaliacoes


def _filho(
    pai1: Cromossomo,
    pai2: Cromossomo,
    parametros: ParametrosGA,
    cenario: Cenario,
    sorteio: random.Random,
) -> Cromossomo:
    """Cruzamento e mutação, cada um com a sua taxa."""
    filho = pai1
    if sorteio.random() < parametros.taxa_cruzamento:
        filho = cruzar(pai1, pai2, parametros.cruzamento, sorteio)
    if sorteio.random() < parametros.taxa_mutacao:
        filho = mutar(filho, cenario.regras, sorteio)
    return filho


def _parada(
    geracao: int, sem_melhora: int, decorrido_s: float, parametros: ParametrosGA
) -> Parada | None:
    if geracao >= parametros.max_geracoes:
        return Parada.GERACOES
    if sem_melhora >= parametros.geracoes_sem_melhora:
        return Parada.ESTAGNACAO
    if decorrido_s >= parametros.tempo_limite_s:
        return Parada.TEMPO
    return None
