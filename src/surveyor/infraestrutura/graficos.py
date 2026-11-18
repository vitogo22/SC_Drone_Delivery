"""Gráfico de convergência do GA (Etapa 8.8).

- `serie_de_convergencia(progresso_csv)`: gerações e melhor custo, lidos do CSV do monitor.
- `grafico_convergencia(progresso_csv, saida_png)`: grava o PNG do melhor custo por geração.

Uma série e um eixo: o custo médio fica de fora porque, com a penalidade dos planos inválidos,
chega a milhões e achataria a curva do melhor. Linha fina, grade discreta, e só o valor final
rotulado. Usa `Figure` sem `pyplot`, para não depender de janela nem de estado global.
"""

import csv
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from surveyor.dominio.erros import ErroDados

COR_SERIE = "#2a78d6"
SUPERFICIE = "#fcfcfb"
TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_EIXO = "#898781"
GRADE = "#e1e0d9"


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


def _reais(valor: float, casas: int = 2) -> str:
    """R$ no formato brasileiro: ponto no milhar e vírgula nos centavos."""
    texto = f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"
