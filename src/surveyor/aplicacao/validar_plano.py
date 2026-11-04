"""Caso de uso: conferir um plano de voo em CSV de forma independente."""

from pathlib import Path

from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao


def executar(plano_csv: Path, entrada: ArquivosDeEntrada, config: Configuracao) -> list[str]:
    """Devolve as violações encontradas no plano (lista vazia = plano válido)."""
    raise NotImplementedError("Etapa 9: validador independente")
