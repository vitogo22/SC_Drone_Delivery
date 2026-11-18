"""Caso de uso: conferir um plano de voo em CSV de forma independente (Etapa 9).

`executar(plano_csv, entrada, config)` lê o plano e os arquivos de entrada, passa tudo pelo
validador do domínio (que não usa o simulador) e devolve as violações e um resumo do plano.
"""

from dataclasses import dataclass
from pathlib import Path

from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.dominio.calculos.custo import custo_total, taxas_pouso_reais
from surveyor.dominio.validacao.plano import validar_plano
from surveyor.infraestrutura.arquivos.leitor_csv import (
    ler_coordenadas,
    ler_extras,
    ler_plano,
    ler_vento,
)


@dataclass(frozen=True, slots=True)
class ResumoPlano:
    """Números do plano: o que a fitness minimiza (A4, A5) e o que o relatório mostra."""

    trechos: int
    pousos: int
    tempo_total_voo_s: int  # no ar, paradas incluídas; a espera em solo não entra (A5)
    taxas_reais: float
    custo_reais: float  # horas de voo x valor da hora + taxas (A4)


@dataclass(frozen=True, slots=True)
class ConferenciaPlano:
    """Violações (vazia = plano válido) e o resumo do plano conferido."""

    violacoes: tuple[str, ...]
    resumo: ResumoPlano


def executar(plano_csv: Path, entrada: ArquivosDeEntrada, config: Configuracao) -> ConferenciaPlano:
    """Confere o plano contra o professor, as extras e o vento, e resume tempo, pousos e custo."""
    regras = config.regras
    plano = ler_plano(plano_csv)
    pontos = [*ler_coordenadas(entrada.coordenadas, regras), *ler_extras(entrada.extras)]
    vento = ler_vento(entrada.vento, regras)
    violacoes = validar_plano(plano, pontos, vento, regras, config.operacao)
    resumo = ResumoPlano(
        trechos=len(plano.trechos),
        pousos=plano.quantidade_pousos,
        tempo_total_voo_s=plano.tempo_total_voo_s,
        taxas_reais=taxas_pouso_reais(plano, regras),
        custo_reais=custo_total(plano, regras, config.operacao),
    )
    return ConferenciaPlano(tuple(violacoes), resumo)
