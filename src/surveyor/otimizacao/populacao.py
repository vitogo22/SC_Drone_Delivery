"""População inicial do GA (Etapa 8).

- `vizinho_mais_proximo(cenario, inicio)`: rota gulosa, sempre para o ponto mais perto ainda
  não visitado; sai do campus ou, se `inicio` for dado, desse ponto.
- `populacao_inicial(cenario, parametros, sorteio)`: o primeiro indivíduo é a referência, o
  vizinho mais próximo saindo do campus a 36 km/h: com o elitismo, o GA nunca entrega um plano
  pior que ela. Até completar `proporcao_vizinho_mais_proximo`, vizinhos mais próximos a partir
  de um ponto sorteado (a perturbação); o resto, rotas aleatórias. Fora a referência, as
  velocidades são sorteadas até `velocidade_inicial_maxima_kmh`. Todos os dias começam ligados.
"""

import random

from surveyor.dominio.simulador import Cenario
from surveyor.otimizacao.cromossomo import Cromossomo
from surveyor.otimizacao.parametros import ParametrosGA


def vizinho_mais_proximo(cenario: Cenario, inicio: int | None = None) -> tuple[int, ...]:
    """Ordem gulosa dos N pontos (empate: o de menor índice)."""
    distancias = cenario.distancias_km
    restantes = set(range(cenario.indice_campus))
    ordem: list[int] = []
    atual = cenario.indice_campus
    if inicio is not None:
        ordem.append(inicio)
        restantes.remove(inicio)
        atual = inicio
    while restantes:
        _, atual = min((distancias[atual][ponto], ponto) for ponto in restantes)
        ordem.append(atual)
        restantes.remove(atual)
    return tuple(ordem)


def populacao_inicial(
    cenario: Cenario, parametros: ParametrosGA, sorteio: random.Random
) -> list[Cromossomo]:
    """`tamanho_populacao` cromossomos: gulosos primeiro, depois aleatórios."""
    regras = cenario.regras
    n = cenario.indice_campus
    lentas = [
        indice
        for indice, v_kmh in enumerate(regras.velocidades_kmh)
        if v_kmh <= parametros.velocidade_inicial_maxima_kmh
    ]
    gulosos = round(parametros.proporcao_vizinho_mais_proximo * parametros.tamanho_populacao)
    populacao: list[Cromossomo] = []
    for numero in range(parametros.tamanho_populacao):
        if numero < gulosos:
            inicio = None if numero == 0 else sorteio.randrange(n)
            ordem = vizinho_mais_proximo(cenario, inicio)
        else:
            ordem = tuple(sorteio.sample(range(n), n))
        if numero == 0 and gulosos:
            velocidades = (lentas[0],) * (n + 1)  # a referência: tudo na menor velocidade
        else:
            velocidades = tuple(sorteio.choices(lentas, k=n + 1))
        populacao.append(Cromossomo(ordem, velocidades, (True,) * regras.prazo_dias))
    return populacao
