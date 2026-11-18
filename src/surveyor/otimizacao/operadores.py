"""Operadores: seleção, cruzamento e mutação (Etapa 8). Nunca alteram os pais.

- `torneio(custos, k, sorteio)`: índice do vencedor de um torneio de `k` indivíduos.
- `ox`, `pmx` (com o corte dado) e `erx` (sorteado): cruzamentos de permutação. Devolvem a
  ordem do filho e os pontos que vieram do pai 1 (docs/codificacao.md).
- `cruzar(pai1, pai2, metodo, sorteio)`: um filho. A ordem usa o cruzamento escolhido; a
  velocidade de cada ponto vem do pai que forneceu o ponto; a da volta ao campus vem de um pai
  sorteado; o calendário usa cruzamento uniforme.
- `troca`, `inversao`, `deslocamento` (ordem), `mutar_velocidade` (±1 num índice) e
  `inverter_dia` (calendário): mutações de uma parte.
- `mutar(cromossomo, regras, sorteio)`: sorteia a parte (ordem, velocidade ou calendário) e,
  na ordem, o tipo de mutação.
"""

import random
from collections.abc import Sequence
from dataclasses import replace
from enum import Enum

from surveyor.dominio.regras import Regras
from surveyor.otimizacao.cromossomo import Cromossomo

Ordem = tuple[int, ...]


class Cruzamento(Enum):
    """Cruzamento da ordem: OX é o padrão; PMX e ERX entram nos experimentos."""

    OX = "OX"
    PMX = "PMX"
    ERX = "ERX"


def torneio(custos: Sequence[float], k: int, sorteio: random.Random) -> int:
    """Sorteia `k` indivíduos distintos e devolve o índice do de MENOR custo.

    O custo é minimizado, e o torneio só compara custos: não precisa convertê-los em aptidão,
    como a roleta precisaria. Empate: vence o primeiro sorteado.
    """
    if not 2 <= k <= len(custos):
        raise ValueError(f"torneio precisa de entre 2 e {len(custos)} participantes, e não {k}")
    participantes = sorteio.sample(range(len(custos)), k)
    return min(participantes, key=lambda indice: custos[indice])


def ox(pai1: Ordem, pai2: Ordem, corte: tuple[int, int]) -> tuple[Ordem, frozenset[int]]:
    """Order crossover: copia `pai1[a:b]` e completa, a partir de b, na ordem de `pai2`."""
    a, b = corte
    segmento = pai1[a:b]
    no_segmento = set(segmento)
    resto = [ponto for ponto in (*pai2[b:], *pai2[:b]) if ponto not in no_segmento]
    filho = list(pai1)
    for posicao, ponto in zip((*range(b, len(pai1)), *range(a)), resto, strict=True):
        filho[posicao] = ponto
    return tuple(filho), frozenset(segmento)


def pmx(pai1: Ordem, pai2: Ordem, corte: tuple[int, int]) -> tuple[Ordem, frozenset[int]]:
    """Partially mapped crossover: copia `pai1[a:b]`; fora dele, o gene de `pai2`, trocado
    pelo mapa do segmento (pai1[i] -> pai2[i]) enquanto já estiver no segmento."""
    a, b = corte
    no_segmento = set(pai1[a:b])
    mapa = {pai1[i]: pai2[i] for i in range(a, b)}
    filho = list(pai2)
    filho[a:b] = pai1[a:b]
    for posicao in (*range(a), *range(b, len(pai1))):
        ponto = pai2[posicao]
        while ponto in no_segmento:
            ponto = mapa[ponto]
        filho[posicao] = ponto
    return tuple(filho), frozenset(no_segmento)


def erx(pai1: Ordem, pai2: Ordem, sorteio: random.Random) -> tuple[Ordem, frozenset[int]]:
    """Edge recombination: segue as arestas dos pais, preferindo o vizinho com menos arestas
    livres. Começa no primeiro ponto do pai 1; cada ponto seguinte vem do pai que tem a aresta
    usada para chegar a ele (se os dois têm, ou nenhum, o pai é sorteado)."""
    arestas = [_arestas(pai1), _arestas(pai2)]
    vizinhos: dict[int, set[int]] = {ponto: set() for ponto in pai1}
    for aresta in arestas[0] | arestas[1]:
        a, b = tuple(aresta)
        vizinhos[a].add(b)
        vizinhos[b].add(a)
    atual = pai1[0]
    filho = [atual]
    do_pai1 = {atual}
    restantes = set(pai1) - {atual}
    while restantes:
        for vizinho in vizinhos[atual]:
            vizinhos[vizinho].discard(atual)
        candidatos = vizinhos.pop(atual)
        if candidatos:
            menor = min(len(vizinhos[c]) for c in candidatos)
            opcoes = sorted(c for c in candidatos if len(vizinhos[c]) == menor)
        else:
            opcoes = sorted(restantes)  # sem aresta livre: salta para um ponto qualquer
        proximo = sorteio.choice(opcoes)
        aresta = frozenset((atual, proximo))
        no_pai1, no_pai2 = aresta in arestas[0], aresta in arestas[1]
        if no_pai1 == no_pai2:
            no_pai1 = sorteio.random() < 0.5
        if no_pai1:
            do_pai1.add(proximo)
        filho.append(proximo)
        restantes.remove(proximo)
        atual = proximo
    return tuple(filho), frozenset(do_pai1)


def _arestas(ordem: Ordem) -> set[frozenset[int]]:
    """Arestas da rota vista como ciclo (as pontas se ligam pelo campus)."""
    return {frozenset((ordem[i - 1], ordem[i])) for i in range(len(ordem))}


def cruzar(
    pai1: Cromossomo, pai2: Cromossomo, metodo: Cruzamento, sorteio: random.Random
) -> Cromossomo:
    """Um filho de `pai1` e `pai2` (para o outro filho, chame com os pais trocados)."""
    n = len(pai1.ordem)
    if metodo is Cruzamento.ERX:
        ordem, do_pai1 = erx(pai1.ordem, pai2.ordem, sorteio)
    else:
        a, b = sorted(sorteio.sample(range(n + 1), 2))  # segmento [a, b) nunca vazio
        operador = ox if metodo is Cruzamento.OX else pmx
        ordem, do_pai1 = operador(pai1.ordem, pai2.ordem, (a, b))
    velocidades = (
        *((pai1 if ponto in do_pai1 else pai2).velocidades[ponto] for ponto in range(n)),
        sorteio.choice((pai1, pai2)).velocidades[n],
    )
    calendario = tuple(
        sorteio.choice(dia) for dia in zip(pai1.calendario, pai2.calendario, strict=True)
    )
    return Cromossomo(ordem, velocidades, calendario)


def troca(ordem: Ordem, sorteio: random.Random) -> Ordem:
    """Troca dois pontos de lugar."""
    i, j = sorteio.sample(range(len(ordem)), 2)
    nova = list(ordem)
    nova[i], nova[j] = nova[j], nova[i]
    return tuple(nova)


def inversao(ordem: Ordem, sorteio: random.Random) -> Ordem:
    """Inverte o trecho entre duas posições (inclusive): desfaz um cruzamento de caminho."""
    a, b = sorted(sorteio.sample(range(len(ordem)), 2))
    return (*ordem[:a], *reversed(ordem[a : b + 1]), *ordem[b + 1 :])


def deslocamento(ordem: Ordem, sorteio: random.Random) -> Ordem:
    """Tira um ponto da rota e o põe em outra posição."""
    de, para = sorteio.sample(range(len(ordem)), 2)
    nova = list(ordem)
    nova.insert(para, nova.pop(de))
    return tuple(nova)


def mutar_velocidade(
    velocidades: tuple[int, ...], ultimo_indice: int, sorteio: random.Random
) -> tuple[int, ...]:
    """Soma ou subtrai 1 no índice de velocidade de um gene; nos limites, vai para o outro lado."""
    gene = sorteio.randrange(len(velocidades))
    passo = sorteio.choice((-1, 1))
    novo = velocidades[gene] + passo
    if not 0 <= novo <= ultimo_indice:
        novo = velocidades[gene] - passo
    return (*velocidades[:gene], novo, *velocidades[gene + 1 :])


def inverter_dia(calendario: tuple[bool, ...], sorteio: random.Random) -> tuple[bool, ...]:
    """Liga ou desliga um dia do calendário."""
    dia = sorteio.randrange(len(calendario))
    return (*calendario[:dia], not calendario[dia], *calendario[dia + 1 :])


def mutar(cromossomo: Cromossomo, regras: Regras, sorteio: random.Random) -> Cromossomo:
    """Um filho com uma mutação numa das três partes, sorteada com a mesma chance."""
    parte = sorteio.randrange(3)
    if parte == 0:
        mutacao = sorteio.choice((troca, inversao, deslocamento))
        return replace(cromossomo, ordem=mutacao(cromossomo.ordem, sorteio))
    if parte == 1:
        ultimo = len(regras.velocidades_kmh) - 1
        velocidades = mutar_velocidade(cromossomo.velocidades, ultimo, sorteio)
        return replace(cromossomo, velocidades=velocidades)
    return replace(cromossomo, calendario=inverter_dia(cromossomo.calendario, sorteio))
