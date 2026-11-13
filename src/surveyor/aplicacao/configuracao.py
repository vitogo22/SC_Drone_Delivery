"""Configuração de uma execução: arquivos de entrada e parâmetros de todas as camadas."""

from dataclasses import dataclass, field
from pathlib import Path

from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.otimizacao.parametros import ParametrosGA


@dataclass(frozen=True)
class ArquivosDeEntrada:
    """Arquivos lidos por uma execução."""

    coordenadas: Path = Path("dados/coordenadas.csv")
    extras: Path = Path("dados/extras.csv")
    vento: Path = Path("dados/vento.csv")


@dataclass(frozen=True)
class Integrante:
    """Integrante da equipe: a matrícula define o CEP e o final da coordenada extra."""

    nome: str
    matricula: str


@dataclass(frozen=True)
class Configuracao:
    """Tudo o que os casos de uso precisam saber."""

    regras: Regras = field(default_factory=Regras)
    operacao: ParametrosOperacao = field(default_factory=ParametrosOperacao)
    ga: ParametrosGA = field(default_factory=ParametrosGA)
    # Na mesma ordem das linhas de dados/extras.csv.
    equipe: tuple[Integrante, ...] = (
        Integrante("Vitor Hugo Viana Mondequi", "2024100142"),
        Integrante("Matheus Dominguez Biesek", "2024100467"),
    )

    @classmethod
    def para_execucao(cls, *, rapido: bool = False, semente: int | None = 42) -> "Configuracao":
        """Configuração padrão com o GA completo ou no modo rápido."""
        ga = ParametrosGA.rapido(semente) if rapido else ParametrosGA(semente=semente)
        return cls(ga=ga)
