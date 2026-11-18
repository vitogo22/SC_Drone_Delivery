"""Operadores: seleção, cruzamento e mutação (Etapa 8). Nunca alteram os pais.

- `torneio(custos, k, sorteio)`: índice do vencedor de um torneio de `k` indivíduos.
"""

import random
from collections.abc import Sequence


def torneio(custos: Sequence[float], k: int, sorteio: random.Random) -> int:
    """Sorteia `k` indivíduos distintos e devolve o índice do de MENOR custo.

    O custo é minimizado, e o torneio só compara custos: não precisa convertê-los em aptidão,
    como a roleta precisaria. Empate: vence o primeiro sorteado.
    """
    if not 2 <= k <= len(custos):
        raise ValueError(f"torneio precisa de entre 2 e {len(custos)} participantes, e não {k}")
    participantes = sorteio.sample(range(len(custos)), k)
    return min(participantes, key=lambda indice: custos[indice])
