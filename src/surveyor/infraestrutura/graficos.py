"""Gráficos da execução: convergência do GA (Etapa 8.8) e mapa da rota (Etapa 10.5).

- `serie_de_convergencia(progresso_csv)`: gerações e melhor custo, lidos do CSV do monitor.
- `grafico_convergencia(progresso_csv, saida_png)`: grava o PNG do melhor custo por geração.
- `figura_rota(plano)` / `grafico_rota(plano, saida_png)`: um painel por dia de voo, com os
  trechos do dia em azul sobre todos os pontos em cinza, os pousos, o campus e as extras.
  Painéis, e não uma cor por dia: com até 7 dias, as cores não ficariam distinguíveis.

Uma série e um eixo: o custo médio fica de fora porque, com a penalidade dos planos inválidos,
chega a milhões e achataria a curva do melhor. Linha fina, grade discreta, e só o valor final
rotulado. Usa `Figure` sem `pyplot`, para não depender de janela nem de estado global.
"""

import csv
import math
from collections.abc import Iterable
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from surveyor.dominio.erros import ErroDados
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo

COR_SERIE = "#2a78d6"
SUPERFICIE = "#fcfcfb"
TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_EIXO = "#898781"
GRADE = "#e1e0d9"
COR_EXTRA = "#eb6834"
PONTO_DE_FUNDO = "#c3c2b7"
PAINEIS_POR_LINHA = 3


def serie_de_convergencia(progresso_csv: Path) -> tuple[list[int], list[float]]:
    """Coluna `geracao` e coluna `melhor_custo` do progresso.csv."""
    with progresso_csv.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if not linhas:
        raise ErroDados(f"{progresso_csv}: nenhuma geração registrada")
    return (
        [int(linha["geracao"]) for linha in linhas],
        [float(linha["melhor_custo"]) for linha in linhas],
    )


def grafico_convergencia(progresso_csv: Path, saida_png: Path) -> None:
    """Melhor custo (R$) por geração, com o valor final escrito ao lado do último ponto."""
    geracoes, melhores = serie_de_convergencia(progresso_csv)
    figura = Figure(figsize=(8, 4.5), dpi=150, facecolor=SUPERFICIE)
    eixo = figura.subplots()
    eixo.set_facecolor(SUPERFICIE)
    eixo.plot(geracoes, melhores, color=COR_SERIE, linewidth=2, solid_capstyle="round")
    eixo.annotate(
        _reais(melhores[-1]),
        (geracoes[-1], melhores[-1]),
        xytext=(6, 6),
        textcoords="offset points",
        color=TINTA_SECUNDARIA,
        fontsize=9,
    )
    eixo.set_title("Melhor custo por geração", loc="left", color=TINTA_PRIMARIA, fontsize=12)
    eixo.set_xlabel("Geração", color=TINTA_EIXO)
    eixo.yaxis.set_major_formatter(FuncFormatter(lambda valor, _: _reais(valor, casas=0)))
    eixo.grid(axis="y", color=GRADE, linewidth=0.8)
    eixo.set_axisbelow(True)
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        eixo.spines[lado].set_color(TINTA_EIXO)
    eixo.tick_params(colors=TINTA_EIXO, labelsize=9)
    figura.tight_layout()
    saida_png.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(saida_png, facecolor=SUPERFICIE)


def figura_rota(plano: PlanoDeVoo) -> Figure:
    """Um painel por dia de voo, na mesma escala, com a legenda embaixo."""
    if not plano.trechos:
        raise ValueError("plano vazio: não há rota para desenhar")
    dias = sorted({trecho.dia for trecho in plano.trechos})
    colunas = min(len(dias), PAINEIS_POR_LINHA)
    linhas = math.ceil(len(dias) / colunas)
    figura = Figure(figsize=(4.2 * colunas, 4.6 * linhas), dpi=150, facecolor=SUPERFICIE)
    eixos = figura.subplots(linhas, colunas, squeeze=False, sharex=True, sharey=True)
    pontos = {t.origem.cep: t.origem for t in plano.trechos} | {
        t.destino.cep: t.destino for t in plano.trechos
    }
    campus = plano.trechos[0].origem
    extras = [p for p in pontos.values() if not p.pode_pousar]
    for eixo, dia in zip(eixos.flat, dias, strict=False):
        do_dia = [t for t in plano.trechos if t.dia == dia]
        eixo.set_facecolor(SUPERFICIE)
        eixo.scatter(*_lon_lat(pontos.values()), s=4, color=PONTO_DE_FUNDO, linewidths=0)
        for trecho in do_dia:
            eixo.plot(*_lon_lat((trecho.origem, trecho.destino)), color=COR_SERIE, linewidth=1)
        pousos = [t.destino for t in do_dia if t.pouso]
        eixo.scatter(*_lon_lat(pousos), s=22, color=TINTA_PRIMARIA, zorder=3, label="Pouso")
        eixo.scatter(
            *_lon_lat(extras),
            s=40,
            marker="D",
            facecolors="none",
            edgecolors=COR_EXTRA,
            linewidths=1.5,
            zorder=4,
            label="Extra (só foto)",
        )
        eixo.scatter(
            *_lon_lat([campus]),
            s=70,
            marker="s",
            color=TINTA_PRIMARIA,
            edgecolors=SUPERFICIE,
            linewidths=1.5,
            zorder=5,
            label="Campus",
        )
        n_trechos, n_pousos = len(do_dia), len(pousos)
        eixo.set_title(
            f"Dia {dia}: {n_trechos} trecho{'s' if n_trechos > 1 else ''}, "
            f"{n_pousos} pouso{'s' if n_pousos > 1 else ''}",
            loc="left",
            color=TINTA_PRIMARIA,
            fontsize=10,
        )
        eixo.set_aspect(1 / math.cos(math.radians(campus.latitude)))  # graus de longitude
        eixo.tick_params(colors=TINTA_EIXO, labelsize=7)
        for lado in eixo.spines.values():
            lado.set_color(GRADE)
    for eixo in list(eixos.flat)[len(dias) :]:
        eixo.set_visible(False)
    marcas, nomes = eixos.flat[0].get_legend_handles_labels()
    figura.legend(
        marcas,
        nomes,
        loc="lower center",
        ncols=3,
        frameon=False,
        fontsize=9,
        labelcolor=TINTA_SECUNDARIA,
    )
    figura.suptitle("Rota por dia de voo", x=0.01, ha="left", color=TINTA_PRIMARIA, fontsize=12)
    figura.tight_layout(rect=(0, 0.05, 1, 1))
    return figura


def grafico_rota(plano: PlanoDeVoo, saida_png: Path) -> None:
    """Grava o mapa da rota (`figura_rota`) em PNG."""
    saida_png.parent.mkdir(parents=True, exist_ok=True)
    figura_rota(plano).savefig(saida_png, facecolor=SUPERFICIE)


def _lon_lat(pontos: Iterable[Coordenada]) -> tuple[list[float], list[float]]:
    """Longitudes (x) e latitudes (y) dos pontos."""
    lista = list(pontos)
    return [p.longitude for p in lista], [p.latitude for p in lista]


def _reais(valor: float, casas: int = 2) -> str:
    """R$ no formato brasileiro: ponto no milhar e vírgula nos centavos."""
    texto = f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"
