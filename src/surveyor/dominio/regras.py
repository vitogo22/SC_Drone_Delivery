"""Regras de negócio do enunciado e política de operação da equipe.

As funções do domínio recebem estes objetos como argumento, em vez de ler constantes
globais. Assim os testes podem criar variações, como `Regras(fator_autonomia=1.0)`
para conferir os valores da tabela do enunciado. Os códigos A<n> remetem a docs/decisoes.md.
"""

from dataclasses import dataclass

from surveyor.dominio.erros import ErroConfiguracao

SEGUNDOS_POR_HORA = 3600
METROS_POR_KM = 1000


@dataclass(frozen=True)
class Regras:
    """Fatos fixos do enunciado. Não são parâmetros de ajuste."""

    cep_campus: str = "82821020"
    # A7: inteiras, múltiplas de 4, >= 10 m/s (36 km/h) e <= 83 km/h
    velocidades_kmh: tuple[int, ...] = tuple(range(36, 81, 4))
    velocidade_referencia_kmh: int = 36
    autonomia_nominal_s: float = 5000.0
    fator_autonomia: float = 1.14  # A3: multiplica a autonomia nominal
    parada_sem_pouso_s: int = 60
    parada_com_pouso_s: int = 172  # A8
    inicio_voos_s: int = 6 * SEGUNDOS_POR_HORA
    limite_pouso_s: int = 19 * SEGUNDOS_POR_HORA
    inicio_taxa_adicional_s: int = 17 * SEGUNDOS_POR_HORA  # A11: pouso depois disso paga taxa
    taxa_pouso_reais: float = 80.0
    taxa_adicional_reais: float = 80.0
    prazo_dias: int = 7
    duracao_bloco_vento_s: int = 3 * SEGUNDOS_POR_HORA  # previsão Climatempo em blocos de 3 h
    raio_terra_km: float = 6371.0  # A19
    distancia_minima_extra_m: float = 100.0
    distancia_maxima_extra_m: float = 1500.0
    casas_decimais_coordenada: int = 13
    digitos_finais_matricula: int = 8  # o CEP e o final da coordenada extra


@dataclass(frozen=True)
class ParametrosOperacao:
    """Escolhas da equipe sobre custo e segurança (não estão no enunciado)."""

    valor_hora_reais: float = 80.0  # A4: 1 h de voo equivale a 1 pouso
    reserva_bateria: float = 0.01  # fração mínima que sempre sobra na bateria
    limite_operacional_s: int = 17 * SEGUNDOS_POR_HORA  # pousar até aqui evita a taxa

    def __post_init__(self) -> None:
        exigir(self.valor_hora_reais >= 0, "valor_hora_reais não pode ser negativo")
        exigir(0 <= self.reserva_bateria < 1, "reserva_bateria deve estar em [0, 1)")
        exigir(
            Regras.inicio_voos_s < self.limite_operacional_s <= Regras.limite_pouso_s,
            "limite_operacional_s deve ficar entre 06:00:00 e 19:00:00",
        )


def exigir(condicao: bool, mensagem: str) -> None:
    """Levanta ErroConfiguracao com `mensagem` quando `condicao` é falsa."""
    if not condicao:
        raise ErroConfiguracao(mensagem)
