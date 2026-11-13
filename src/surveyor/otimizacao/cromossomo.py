"""Cromossomo: ordem (permutação) + velocidade por ponto + calendário de dias (Etapa 7).

Os genes são índices; o significado (km/h e dias) vem das `Regras` na conversão para a entrada
do simulador. O cromossomo é imutável: um operador sempre cria um filho novo, então os pais
nunca mudam e não é preciso copiar nada.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cromossomo:
    """Um indivíduo da população, com N pontos a visitar (o campus não entra na ordem)."""

    ordem: tuple[int, ...]  # permutação de 0 a N - 1: a sequência de visita
    # Índice em Regras.velocidades_kmh do trecho que CHEGA a cada ponto: [p] é o do ponto p
    # (a velocidade viaja junto com o ponto) e [N] é o da volta ao campus. N + 1 genes.
    velocidades: tuple[int, ...]
    calendario: tuple[bool, ...]  # um bit por dia do prazo: True = o drone pode voar

    def __post_init__(self) -> None:
        quantidade = len(self.ordem)
        if sorted(self.ordem) != list(range(quantidade)):
            raise ValueError(f"ordem não é uma permutação de 0 a {quantidade - 1}: {self.ordem}")
        if len(self.velocidades) != quantidade + 1:
            raise ValueError(
                f"velocidades precisa de {quantidade + 1} genes "
                f"({quantidade} pontos + volta ao campus), e tem {len(self.velocidades)}"
            )
        if any(indice < 0 for indice in self.velocidades):
            raise ValueError(f"índice de velocidade negativo: {self.velocidades}")
        if not self.calendario:
            raise ValueError("calendário vazio")
