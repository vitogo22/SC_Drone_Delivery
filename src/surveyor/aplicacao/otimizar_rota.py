"""Caso de uso: gerar o melhor plano de voo (Etapa 8).

`executar(entrada, saida, config)` lê as entradas, roda o GA gravando uma linha por geração em
`progresso.csv` e o gráfico `convergencia.png` (na pasta de `saida`), confere o melhor plano
com o validador independente e só então grava o CSV do plano em `saida` e o mapa `rota.png`.
Um melhor plano inválido vira `ErroPlano`.
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
from surveyor.infraestrutura.graficos import grafico_convergencia, grafico_rota
from surveyor.infraestrutura.logs.monitor_progresso import MonitorDeProgresso
from surveyor.otimizacao.algoritmo import evoluir

logger = logging.getLogger(__name__)

ARQUIVO_PROGRESSO = "progresso.csv"
ARQUIVO_GRAFICO = "convergencia.png"
ARQUIVO_MAPA = "rota.png"


def montar_cenario(entrada: ArquivosDeEntrada, config: Configuracao) -> Cenario:
    """Lê as entradas e monta o cenário: os pontos do professor (sem o campus), as extras e,
    por último, o campus, achado pelo CEP."""
    regras = config.regras
    professor = ler_coordenadas(entrada.coordenadas, regras)
    extras = ler_extras(entrada.extras)
    vento = ler_vento(entrada.vento, regras)
    campus = next(ponto for ponto in professor if ponto.cep == regras.cep_campus)
    a_visitar = [ponto for ponto in professor if ponto is not campus] + extras
    logger.info(
        "%d pontos a visitar (%d do professor e %d extras)",
        len(a_visitar),
        len(professor) - 1,
        len(extras),
    )
    return Cenario.montar(campus, a_visitar, vento, regras, config.operacao)


def executar(entrada: ArquivosDeEntrada, saida: Path, config: Configuracao) -> PlanoDeVoo:
    """Lê as entradas, roda o GA, valida o melhor plano e grava em `saida`."""
    cenario = montar_cenario(entrada, config)

    progresso = saida.parent / ARQUIVO_PROGRESSO
    with MonitorDeProgresso(progresso) as monitor:
        resultado = evoluir(cenario, config.ga, monitor)
    grafico_convergencia(progresso, saida.parent / ARQUIVO_GRAFICO)
    avaliacao = resultado.avaliacao
    logger.info(
        "GA parou na geração %d (%s): melhor custo R$ %.2f",
        resultado.geracoes,
        resultado.parada.value,
        avaliacao.custo,
    )
    if avaliacao.motivo_invalido is not None:
        raise ErroPlano(f"o melhor plano encontrado é inválido: {avaliacao.motivo_invalido}")
    violacoes = validar_plano(
        avaliacao.plano, cenario.pontos, cenario.vento, config.regras, config.operacao
    )
    if violacoes:
        raise ErroPlano(f"o melhor plano não passou no validador: {'; '.join(violacoes)}")
    escrever_plano(avaliacao.plano, saida)
    grafico_rota(avaliacao.plano, saida.parent / ARQUIVO_MAPA)
    return avaliacao.plano
