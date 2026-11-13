"""Linha de comando: `python -m surveyor <comando>`.

Ponto de montagem do sistema: lê os argumentos, aplica a política de logs, chama o caso de
uso e traduz o resultado em código de saída. Não contém regra de negócio.
"""

import argparse
import logging
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path

from surveyor import __version__
from surveyor.aplicacao import conferir_extras, otimizar_rota, validar_plano
from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.dominio.erros import ErroSurveyor
from surveyor.infraestrutura.logs.configuracao import (
    NIVEIS,
    arquivo_da_execucao,
    configurar_logging,
)

logger = logging.getLogger(__name__)

SAIDA_OK = 0
SAIDA_ERRO = 1
PLANO_PADRAO = Path("resultados/plano_de_voo.csv")

Comando = Callable[[argparse.Namespace], int]


def criar_parser() -> argparse.ArgumentParser:
    """Monta o parser com os comandos `otimizar`, `validar` e `extras`."""
    parser = argparse.ArgumentParser(
        prog="surveyor",
        description="UNIBRASIL Surveyor: plano de voo de drone por algoritmo genético.",
    )
    parser.add_argument("--versao", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--log-nivel", choices=NIVEIS, default="INFO", help="nível no terminal (padrão: INFO)"
    )
    parser.add_argument(
        "--log-arquivo", type=Path, help="padrão: logs/surveyor_<data>_<hora>.log (nível DEBUG)"
    )

    comandos = parser.add_subparsers(dest="comando", required=True, metavar="COMANDO")

    otimizar = comandos.add_parser("otimizar", help="gera o melhor plano de voo")
    _adicionar_entradas(otimizar)
    otimizar.add_argument("--saida", type=Path, default=PLANO_PADRAO)
    otimizar.add_argument("--semente", type=int, default=42, help="padrão: 42")
    otimizar.add_argument("--rapido", action="store_true", help="execução curta (1 a 2 min)")
    otimizar.set_defaults(executar=_executar_otimizar)

    validar = comandos.add_parser("validar", help="confere um plano de voo em CSV")
    validar.add_argument("plano", type=Path, nargs="?", default=PLANO_PADRAO)
    _adicionar_entradas(validar)
    validar.set_defaults(executar=_executar_validar)

    extras = comandos.add_parser("extras", help="confere as coordenadas extras da equipe")
    padrao = ArquivosDeEntrada()
    extras.add_argument("--coordenadas", type=Path, default=padrao.coordenadas)
    extras.add_argument("--extras", type=Path, default=padrao.extras)
    extras.set_defaults(executar=_executar_extras)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada; devolve o código de saída do processo."""
    args = criar_parser().parse_args(argv)
    configurar_logging(args.log_nivel, args.log_arquivo or arquivo_da_execucao(datetime.now()))
    executar: Comando = args.executar
    try:
        return executar(args)
    except ErroSurveyor as erro:
        logger.error("%s", erro)
        return SAIDA_ERRO


def _adicionar_entradas(parser: argparse.ArgumentParser) -> None:
    padrao = ArquivosDeEntrada()
    parser.add_argument("--coordenadas", type=Path, default=padrao.coordenadas)
    parser.add_argument("--extras", type=Path, default=padrao.extras)
    parser.add_argument("--vento", type=Path, default=padrao.vento)


def _entrada(args: argparse.Namespace) -> ArquivosDeEntrada:
    return ArquivosDeEntrada(coordenadas=args.coordenadas, extras=args.extras, vento=args.vento)


def _executar_otimizar(args: argparse.Namespace) -> int:
    config = Configuracao.para_execucao(rapido=args.rapido, semente=args.semente)
    modo = "rápido" if args.rapido else "completo"
    logger.info("Otimizando (modo %s, semente %s)", modo, config.ga.semente)
    plano = otimizar_rota.executar(_entrada(args), args.saida, config)
    logger.info(
        "Plano gravado em %s: %d trechos, %d pousos, %d s de voo",
        args.saida,
        len(plano.trechos),
        plano.quantidade_pousos,
        plano.tempo_total_voo_s,
    )
    return SAIDA_OK


def _executar_validar(args: argparse.Namespace) -> int:
    violacoes = validar_plano.executar(args.plano, _entrada(args), Configuracao())
    for violacao in violacoes:
        logger.error("Violação: %s", violacao)
    if violacoes:
        return SAIDA_ERRO
    logger.info("Plano válido: %s", args.plano)
    return SAIDA_OK


def _executar_extras(args: argparse.Namespace) -> int:
    entrada = ArquivosDeEntrada(coordenadas=args.coordenadas, extras=args.extras)
    conferencias = conferir_extras.executar(entrada, Configuracao())
    print(_tabela_extras(conferencias))
    violacoes = [
        f"CEP {c.extra.cep} ({c.integrante.nome}): {violacao}"
        for c in conferencias
        for violacao in c.violacoes
    ]
    for violacao in violacoes:
        logger.error("Violação: %s", violacao)
    if violacoes:
        return SAIDA_ERRO
    logger.info("Coordenadas extras válidas: %s", args.extras)
    return SAIDA_OK


def _tabela_extras(conferencias: list[conferir_extras.ConferenciaExtra]) -> str:
    """Tabela Markdown de docs/coordenadas_extras.md."""
    linhas = [
        "| Integrante | Matrícula | CEP | Latitude | Longitude "
        "| Ponto mais próximo (CEP) | Distância (m) |",
        "|---|---|---|---|---|---|---|",
    ]
    linhas += [
        f"| {c.integrante.nome} | {c.integrante.matricula} | {c.extra.cep} "
        f"| {c.extra.latitude_texto} | {c.extra.longitude_texto} "
        f"| {c.mais_proximo.cep} | {c.distancia_m:.1f} |"
        for c in conferencias
    ]
    return "\n".join(linhas)
