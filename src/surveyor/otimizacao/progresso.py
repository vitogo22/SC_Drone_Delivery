"""Contrato de monitoramento: o que o laço evolutivo informa a cada geração.

O algoritmo só conhece a interface `ObservadorDeProgresso`. Quem grava CSV e log é
`surveyor.infraestrutura.logs.monitor_progresso`, e nos testes basta passar uma lista.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class EstatisticasDaGeracao:
    """Resumo de uma geração (os custos são os da fitness: menor é melhor)."""

    geracao: int
    melhor_custo: float
    custo_medio: float
    pior_custo: float
    pousos_do_melhor: int
    tempo_voo_do_melhor_s: int
    segundos_decorridos: float


class ObservadorDeProgresso(Protocol):
    """Recebe as estatísticas ao fim de cada geração."""

    def registrar(self, estatisticas: EstatisticasDaGeracao) -> None:
        """Processa as estatísticas de uma geração."""
        ...
