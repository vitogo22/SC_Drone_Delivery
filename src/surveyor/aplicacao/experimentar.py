"""Caso de uso: experimentos com os parâmetros do GA (Etapa 10).

- `configuracoes(base, orcamento)`: a base e uma variação por fator (um fator por vez):
  população, cruzamento, mutação, seleção, elitismo, semeadura e valor da hora.
- `executar(entrada, saida_csv, config, sementes, processos, orcamento)`: roda cada
  configuração com cada semente, em paralelo, e grava uma linha por execução em `saida_csv`.
- `tabela_markdown(execucoes)`: resumo por configuração, para `docs/experimentos.md`.

Toda execução tem o mesmo orçamento de avaliações de fitness: a população de 100 roda o dobro
de gerações da de 200. Assim a comparação é justa e reproduzível pela semente (um limite de
tempo dependeria da carga da máquina). A estagnação não interrompe a execução.
"""

import csv
import dataclasses
import logging
import time
from collections.abc import Iterable, Iterator, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from itertools import groupby
from pathlib import Path
from statistics import fmean, stdev
from typing import Any

from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.aplicacao.otimizar_rota import montar_cenario
from surveyor.dominio.regras import SEGUNDOS_POR_HORA, ParametrosOperacao
from surveyor.otimizacao.algoritmo import evoluir
from surveyor.otimizacao.operadores import Cruzamento, Selecao
from surveyor.otimizacao.parametros import ParametrosGA
from surveyor.otimizacao.progresso import EstatisticasDaGeracao

logger = logging.getLogger(__name__)

ORCAMENTO_AVALIACOES = 60_000


@dataclass(frozen=True, slots=True)
class Experimento:
    """Uma configuração: o fator variado, o valor dele e os parâmetros completos."""

    fator: str
    valor: str
    ga: ParametrosGA
    operacao: ParametrosOperacao


@dataclass(frozen=True, slots=True)
class Execucao:
    """Resultado de uma configuração com uma semente (uma linha do CSV)."""

    fator: str
    valor: str
    semente: int
    custo_reais: float  # com o valor da hora DESTA configuração
    valido: bool
    pousos: int
    horas_voo: float
    geracoes: int
    segundos: float


def configuracoes(base: Configuracao, orcamento: int = ORCAMENTO_AVALIACOES) -> list[Experimento]:
    """A base e as variações de um fator por vez, todas com `orcamento` avaliações."""
    variacoes: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = [
        ("base", "padrão", {}, {}),
        *(("população", str(n), {"tamanho_populacao": n}, {}) for n in (100, 400)),
        *(("cruzamento", c.value, {"cruzamento": c}, {}) for c in (Cruzamento.PMX, Cruzamento.ERX)),
        *(("mutação", f"{t:.0%}", {"taxa_mutacao": t}, {}) for t in (0.05, 0.15)),
        *(("seleção", f"torneio k = {k}", {"tamanho_torneio": k}, {}) for k in (2, 5)),
        *(("seleção", s.value, {"selecao": s}, {}) for s in (Selecao.RANK, Selecao.ROLETA)),
        *(("elitismo", f"{e:.0%}", {"proporcao_elite": e}, {}) for e in (0.0, 0.05)),
        *(
            ("semeadura", f"{p:.0%}", {"proporcao_vizinho_mais_proximo": p}, {})
            for p in (0.0, 0.10, 0.20)
        ),
        *(("valor da hora", f"R$ {v:.0f}", {}, {"valor_hora_reais": v}) for v in (40.0, 160.0)),
    ]
    experimentos: list[Experimento] = []
    for fator, valor, no_ga, na_operacao in variacoes:
        ga = replace(base.ga, **no_ga)
        geracoes = orcamento // ga.tamanho_populacao
        if geracoes < 1:
            raise ValueError(
                f"orçamento de {orcamento} avaliações não dá uma geração de {ga.tamanho_populacao}"
            )
        ga = replace(
            ga, max_geracoes=geracoes, geracoes_sem_melhora=geracoes, tempo_limite_s=float("inf")
        )
        experimentos.append(Experimento(fator, valor, ga, replace(base.operacao, **na_operacao)))
    return experimentos


def executar(
    entrada: ArquivosDeEntrada,
    saida_csv: Path,
    config: Configuracao,
    sementes: Sequence[int],
    processos: int,
    orcamento: int = ORCAMENTO_AVALIACOES,
) -> list[Execucao]:
    """Roda cada configuração com cada semente e grava o CSV (na ordem das configurações)."""
    tarefas = [
        (entrada, config, experimento, semente)
        for experimento in configuracoes(config, orcamento)
        for semente in sementes
    ]
    logger.info("%d execuções em %d processo(s)", len(tarefas), processos)
    if processos == 1:
        execucoes = list(_registrar(map(_rodar, tarefas), len(tarefas)))
    else:
        with ProcessPoolExecutor(processos) as pool:
            execucoes = list(_registrar(pool.map(_rodar, tarefas), len(tarefas)))
    saida_csv.parent.mkdir(parents=True, exist_ok=True)
    with saida_csv.open("w", encoding="utf-8", newline="") as arquivo:
        campos = [campo.name for campo in dataclasses.fields(Execucao)]
        escritor = csv.DictWriter(arquivo, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(dataclasses.asdict(execucao) for execucao in execucoes)
    return execucoes


def tabela_markdown(execucoes: Sequence[Execucao]) -> str:
    """Uma linha por configuração: melhor, média e desvio do custo, e o plano do melhor."""
    linhas = [
        "| Fator | Valor | Sementes | Melhor custo | Custo médio | Desvio | Válidos "
        "| Pousos (melhor) | Horas de voo (melhor) | Tempo médio |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for (fator, valor), grupo in groupby(execucoes, key=lambda e: (e.fator, e.valor)):
        do_grupo = list(grupo)
        custos = [e.custo_reais for e in do_grupo]
        melhor = min(do_grupo, key=lambda e: e.custo_reais)
        desvio = _reais(stdev(custos)) if len(custos) > 1 else "-"
        validos = sum(e.valido for e in do_grupo)
        horas = f"{melhor.horas_voo:.2f}".replace(".", ",")
        linhas.append(
            f"| {fator} | {valor} | {len(do_grupo)} | {_reais(melhor.custo_reais)} "
            f"| {_reais(fmean(custos))} | {desvio} | {validos}/{len(do_grupo)} "
            f"| {melhor.pousos} | {horas} | {fmean(e.segundos for e in do_grupo):.0f} s |"
        )
    return "\n".join(linhas)


class _SemObservador:
    def registrar(self, estatisticas: EstatisticasDaGeracao) -> None:
        """Os experimentos só guardam o resultado final de cada execução."""


def _rodar(tarefa: tuple[ArquivosDeEntrada, Configuracao, Experimento, int]) -> Execucao:
    """Uma execução (função de módulo, para rodar em outro processo)."""
    entrada, config, experimento, semente = tarefa
    cenario = montar_cenario(entrada, replace(config, operacao=experimento.operacao))
    inicio_s = time.perf_counter()
    resultado = evoluir(cenario, replace(experimento.ga, semente=semente), _SemObservador())
    avaliacao = resultado.avaliacao
    return Execucao(
        fator=experimento.fator,
        valor=experimento.valor,
        semente=semente,
        custo_reais=avaliacao.custo,
        valido=avaliacao.valido,
        pousos=avaliacao.plano.quantidade_pousos,
        horas_voo=avaliacao.plano.tempo_total_voo_s / SEGUNDOS_POR_HORA,
        geracoes=resultado.geracoes,
        segundos=time.perf_counter() - inicio_s,
    )


def _registrar(execucoes: Iterable[Execucao], total: int) -> Iterator[Execucao]:
    """Loga cada execução assim que ela termina."""
    for numero, execucao in enumerate(execucoes, start=1):
        logger.info(
            "[%d/%d] %s = %s, semente %d: R$ %.2f (%s), %.0f s",
            numero,
            total,
            execucao.fator,
            execucao.valor,
            execucao.semente,
            execucao.custo_reais,
            "válido" if execucao.valido else "inválido",
            execucao.segundos,
        )
        yield execucao


def _reais(valor: float) -> str:
    """R$ no formato brasileiro: ponto no milhar e vírgula nos centavos."""
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"
