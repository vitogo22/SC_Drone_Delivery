"""Caso de uso: gerar o melhor plano de voo (Etapa 8).

`executar(entrada, saida, config)` lê as entradas, roda o GA gravando uma linha por geração em
`progresso.csv` (na pasta de `saida`), confere o melhor plano com o validador independente e
só então grava o CSV do plano em `saida`. Um melhor plano inválido vira `ErroPlano`.
"""

import logging
from pathlib import Path

from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.dominio.erros import ErroPlano
from surveyor.dominio.modelos import PlanoDeVoo
from surveyor.dominio.simulador import Cenario
from surveyor.dominio.validacao.plano import validar_plano
from surveyor.infraestrutura.arquivos.escritor_csv import escrever_plano
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_extras, ler_vento
from surveyor.infraestrutura.logs.monitor_progresso import MonitorDeProgresso
from surveyor.otimizacao.algoritmo import evoluir

logger = logging.getLogger(__name__)

ARQUIVO_PROGRESSO = "progresso.csv"


def executar(entrada: ArquivosDeEntrada, saida: Path, config: Configuracao) -> PlanoDeVoo:
    """Lê as entradas, roda o GA, valida o melhor plano e grava em `saida`."""
    regras = config.regras
    professor = ler_coordenadas(entrada.coordenadas, regras)
    extras = ler_extras(entrada.extras)
    vento = ler_vento(entrada.vento, regras)
    campus = next(ponto for ponto in professor if ponto.cep == regras.cep_campus)
    a_visitar = [ponto for ponto in professor if ponto is not campus] + extras
    cenario = Cenario.montar(campus, a_visitar, vento, regras, config.operacao)
    logger.info(
        "%d pontos a visitar (%d do professor e %d extras)",
        len(a_visitar),
        len(professor) - 1,
        len(extras),
    )

    with MonitorDeProgresso(saida.parent / ARQUIVO_PROGRESSO) as monitor:
        resultado = evoluir(cenario, config.ga, monitor)
    avaliacao = resultado.avaliacao
    logger.info(
        "GA parou na geração %d (%s): melhor custo R$ %.2f",
        resultado.geracoes,
        resultado.parada.value,
        avaliacao.custo,
    )
    if avaliacao.motivo_invalido is not None:
        raise ErroPlano(f"o melhor plano encontrado é inválido: {avaliacao.motivo_invalido}")
    pontos = [*professor, *extras]
    violacoes = validar_plano(avaliacao.plano, pontos, vento, regras, config.operacao)
    if violacoes:
        raise ErroPlano(f"o melhor plano não passou no validador: {'; '.join(violacoes)}")
    escrever_plano(avaliacao.plano, saida)
    return avaliacao.plano
