"""Parâmetros do algoritmo genético (ajustados nos experimentos, docs/experimentos.md)."""

from dataclasses import dataclass

from surveyor.dominio.regras import Regras, exigir
from surveyor.otimizacao.operadores import Cruzamento, Invalidos, Selecao


@dataclass(frozen=True)
class ParametrosGA:
    """Tamanho da população, taxas dos operadores e critérios de parada."""

    tamanho_populacao: int = 200
    max_geracoes: int = 3000
    geracoes_sem_melhora: int = 300
    tempo_limite_s: float = 20 * 60
    taxa_cruzamento: float = 0.9
    taxa_mutacao: float = 0.25
    proporcao_elite: float = 0.02
    selecao: Selecao = Selecao.TORNEIO  # rank e roleta são comparados nos experimentos
    tamanho_torneio: int = 3
    invalidos: Invalidos = Invalidos.PENALIDADE  # reparo e pena de morte: nos experimentos
    cruzamento: Cruzamento = Cruzamento.PMX  # empata com OX no custo e é mais rápido (Etapa 10)
    # População inicial: parte vem do vizinho mais próximo (10 a 20%), o resto é aleatório.
    proporcao_vizinho_mais_proximo: float = 0.15
    # Velocidades iniciais lentas (36 a 52 km/h): mais autonomia, menos pousos no começo.
    velocidade_inicial_maxima_kmh: int = 52
    semente: int | None = 42

    def __post_init__(self) -> None:
        exigir(self.tamanho_populacao >= 2, "tamanho_populacao deve ser >= 2")
        exigir(self.max_geracoes >= 1, "max_geracoes deve ser >= 1")
        exigir(self.geracoes_sem_melhora >= 1, "geracoes_sem_melhora deve ser >= 1")
        exigir(self.tempo_limite_s > 0, "tempo_limite_s deve ser positivo")
        exigir(0 <= self.taxa_cruzamento <= 1, "taxa_cruzamento deve estar em [0, 1]")
        exigir(0 <= self.taxa_mutacao <= 1, "taxa_mutacao deve estar em [0, 1]")
        exigir(0 <= self.proporcao_elite < 1, "proporcao_elite deve estar em [0, 1)")
        exigir(
            2 <= self.tamanho_torneio <= self.tamanho_populacao,
            "tamanho_torneio deve estar entre 2 e tamanho_populacao",
        )
        exigir(
            0 <= self.proporcao_vizinho_mais_proximo <= 1,
            "proporcao_vizinho_mais_proximo deve estar em [0, 1]",
        )
        exigir(
            self.velocidade_inicial_maxima_kmh >= Regras.velocidade_referencia_kmh,
            f"velocidade_inicial_maxima_kmh deve ser >= {Regras.velocidade_referencia_kmh}",
        )

    @classmethod
    def rapido(cls, semente: int | None = 42) -> "ParametrosGA":
        """Execução curta (menos de 1 min) para o professor reproduzir o resultado parcialmente."""
        return cls(
            tamanho_populacao=60,
            max_geracoes=150,
            geracoes_sem_melhora=50,
            tempo_limite_s=120,
            semente=semente,
        )
