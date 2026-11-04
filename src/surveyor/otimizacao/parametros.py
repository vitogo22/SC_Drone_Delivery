"""Parâmetros do algoritmo genético (ajustados nos experimentos, docs/experimentos.md)."""

from dataclasses import dataclass

from surveyor.dominio.regras import exigir


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
    tamanho_torneio: int = 3
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

    @classmethod
    def rapido(cls, semente: int | None = 42) -> "ParametrosGA":
        """Execução curta (1 a 2 min) para o professor reproduzir o resultado parcialmente."""
        return cls(
            tamanho_populacao=60,
            max_geracoes=150,
            geracoes_sem_melhora=50,
            tempo_limite_s=120,
            semente=semente,
        )
