"""Fitness: custo do plano devolvido pelo simulador + penalidade se inválido (Etapa 8).

- `avaliar(cromossomo, cenario)`: simula e devolve a `Avaliacao` (custo da fitness e plano).
- `teto_de_custo_valido(cenario)`: o maior custo que um plano válido pode ter.

O custo é o da A4 (horas de voo x valor da hora + R$ dos pousos). Rotas sorteadas não fecham
em 7 dias (Etapa 6.7), então a fitness precisa ordenar também os planos inválidos: cada
trecho que faltou custa o teto. Assim qualquer plano válido vence qualquer inválido, e entre
dois inválidos vence o que chegou mais longe.
"""

from dataclasses import dataclass

from surveyor.dominio.calculos.custo import custo_total
from surveyor.dominio.modelos import PlanoDeVoo
from surveyor.dominio.regras import SEGUNDOS_POR_HORA
from surveyor.dominio.simulador import Cenario, simular
from surveyor.otimizacao.cromossomo import Cromossomo, decisoes_de_voo


@dataclass(frozen=True, slots=True)
class Avaliacao:
    """Resultado de um indivíduo: menor custo é melhor."""

    custo: float
    plano: PlanoDeVoo
    valido: bool


def teto_de_custo_valido(cenario: Cenario) -> float:
    """Custo de voar a janela inteira (06:00:00 a 19:00:00) nos 7 dias e pousar em todo trecho
    pagando a taxa adicional: nenhum plano válido custa mais que isso."""
    regras = cenario.regras
    horas_por_dia = (regras.limite_pouso_s - regras.inicio_voos_s) / SEGUNDOS_POR_HORA
    horas = regras.prazo_dias * horas_por_dia
    trechos = len(cenario.pontos)  # N pontos + a volta ao campus
    pouso_mais_caro = regras.taxa_pouso_reais + regras.taxa_adicional_reais
    return horas * cenario.operacao.valor_hora_reais + trechos * pouso_mais_caro


def avaliar(cromossomo: Cromossomo, cenario: Cenario) -> Avaliacao:
    """Simula o cromossomo; o plano inválido paga o teto por trecho que faltou."""
    resultado = simular(decisoes_de_voo(cromossomo, cenario.regras), cenario)
    plano = resultado.plano
    faltando = len(cenario.pontos) - len(plano.trechos)
    custo = custo_total(plano, cenario.regras, cenario.operacao)
    return Avaliacao(custo + faltando * teto_de_custo_valido(cenario), plano, resultado.valido)
