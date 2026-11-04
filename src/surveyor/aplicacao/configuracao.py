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
class Configuracao:
    """Tudo o que os casos de uso precisam saber."""

    regras: Regras = field(default_factory=Regras)
    operacao: ParametrosOperacao = field(default_factory=ParametrosOperacao)
    ga: ParametrosGA = field(default_factory=ParametrosGA)

    @classmethod
    def para_execucao(cls, *, rapido: bool = False, semente: int | None = 42) -> "Configuracao":
        """Configuração padrão com o GA completo ou no modo rápido."""
        ga = ParametrosGA.rapido(semente) if rapido else ParametrosGA(semente=semente)
        return cls(ga=ga)
