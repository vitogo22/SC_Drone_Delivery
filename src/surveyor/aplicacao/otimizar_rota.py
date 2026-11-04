"""Caso de uso: gerar o melhor plano de voo."""

from pathlib import Path

from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.dominio.modelos import PlanoDeVoo


def executar(entrada: ArquivosDeEntrada, saida: Path, config: Configuracao) -> PlanoDeVoo:
    """Lê as entradas, roda o GA, valida o melhor plano e grava em `saida`."""
    raise NotImplementedError("Etapas 6 a 9: simulador, GA e CSV de saída")
