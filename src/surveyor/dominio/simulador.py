"""Decodificador: decisões de voo -> PlanoDeVoo sempre seguro (Etapa 6).

Recebe tipos simples (ordem dos pontos, velocidade por ponto, dias habilitados), nunca o
Cromossomo de surveyor.otimizacao: o domínio não depende do algoritmo genético.

Invariante: ao chegar a um ponto, o drone sempre tem bateria e horário para pousar ali
(ou, se for coordenada extra, para seguir até o próximo ponto onde pode pousar).
"""

from dataclasses import dataclass

from surveyor.dominio.modelos import PlanoDeVoo


@dataclass(frozen=True, slots=True)
class DecisoesDeVoo:
    """O que o GA decide. O resto (pousos, esperas, troca de dia) o simulador deduz."""

    rota: tuple[int, ...]  # índices dos pontos a visitar, na ordem de visita (sem o campus)
    # Velocidade ajustada de cada trecho: [i] é o que chega a rota[i]; o último é a volta ao campus.
    velocidades_kmh: tuple[int, ...]
    dias: tuple[int, ...]  # dias em que o drone pode voar (1 a 7), em ordem crescente

    def __post_init__(self) -> None:
        trechos = len(self.rota) + 1
        if len(self.velocidades_kmh) != trechos:
            raise ValueError(
                f"{trechos} trechos (ida a cada ponto + volta ao campus), "
                f"mas {len(self.velocidades_kmh)} velocidades"
            )
        if list(self.dias) != sorted(set(self.dias)):
            raise ValueError(f"dias devem estar em ordem crescente, sem repetição: {self.dias}")


@dataclass(frozen=True, slots=True)
class ResultadoSimulacao:
    """Plano montado pelo simulador e, se ele não fecha no prazo, o motivo."""

    plano: PlanoDeVoo
    motivo_invalido: str | None = None

    @property
    def valido(self) -> bool:
        """O plano visita tudo e volta ao campus dentro das regras."""
        return self.motivo_invalido is None
