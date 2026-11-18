"""Laço evolutivo, elitismo e critérios de parada (Etapa 8).

`evoluir(cenario, parametros, observador)` cria a população inicial e, a cada geração:
registra as estatísticas no `ObservadorDeProgresso`, confere a parada (gerações, estagnação
do melhor custo ou tempo) e monta a próxima geração. A elite (pelo menos 1) passa intacta,
então o melhor custo nunca piora; o resto vem de torneio, cruzamento e mutação. Toda a
aleatoriedade sai de um `random.Random(parametros.semente)`.
"""

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from statistics import fmean

from surveyor.dominio.simulador import Cenario
from surveyor.otimizacao.cromossomo import Cromossomo
from surveyor.otimizacao.fitness import Avaliacao, avaliar
from surveyor.otimizacao.operadores import cruzar, mutar, torneio
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
    populacao = populacao_inicial(cenario, parametros, sorteio)
    avaliacoes = [avaliar(individuo, cenario) for individuo in populacao]
    tamanho_elite = max(1, round(parametros.proporcao_elite * parametros.tamanho_populacao))
    melhor_custo = float("inf")
    sem_melhora = 0
    geracao = 0
    while True:
        custos = [avaliacao.custo for avaliacao in avaliacoes]
        ranking = sorted(range(len(populacao)), key=custos.__getitem__)
        campeao = avaliacoes[ranking[0]]
        if campeao.custo < melhor_custo:
            melhor_custo, sem_melhora = campeao.custo, 0
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
            return ResultadoGA(populacao[ranking[0]], campeao, geracao, parada)

        conhecidos = dict(zip(populacao, avaliacoes, strict=True))
        proxima = [populacao[i] for i in ranking[:tamanho_elite]]
        while len(proxima) < parametros.tamanho_populacao:
            proxima.append(_filho(populacao, custos, parametros, cenario, sorteio))
        populacao = proxima
        avaliacoes = [
            conhecidos[individuo] if individuo in conhecidos else avaliar(individuo, cenario)
            for individuo in populacao
        ]
        geracao += 1


def _filho(
    populacao: list[Cromossomo],
    custos: list[float],
    parametros: ParametrosGA,
    cenario: Cenario,
    sorteio: random.Random,
) -> Cromossomo:
    """Dois pais por torneio; cruzamento e mutação, cada um com a sua taxa."""
    pai1 = populacao[torneio(custos, parametros.tamanho_torneio, sorteio)]
    pai2 = populacao[torneio(custos, parametros.tamanho_torneio, sorteio)]
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
