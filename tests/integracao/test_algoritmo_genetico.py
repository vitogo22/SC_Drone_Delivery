"""O GA com os dados reais: melhora a referência e é reproduzível pela linha de comando."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.dominio.simulador import Cenario
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_extras, ler_vento
from surveyor.otimizacao.algoritmo import evoluir
from surveyor.otimizacao.cromossomo import Cromossomo
from surveyor.otimizacao.fitness import avaliar
from surveyor.otimizacao.parametros import ParametrosGA
from surveyor.otimizacao.populacao import vizinho_mais_proximo
from surveyor.otimizacao.progresso import EstatisticasDaGeracao

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados"


class _Ignorar:
    def registrar(self, estatisticas: EstatisticasDaGeracao) -> None:
        """O teste só olha o resultado final."""


@pytest.mark.lento
def test_ga_termina_abaixo_do_vizinho_mais_proximo_a_36_kmh() -> None:
    regras = Regras()
    campus, *professor = ler_coordenadas(DADOS / "coordenadas.csv", regras)
    extras = ler_extras(DADOS / "extras.csv")
    vento = ler_vento(DADOS / "vento.csv", regras)
    cenario = Cenario.montar(campus, [*professor, *extras], vento, regras, ParametrosOperacao())
    n = cenario.indice_campus
    referencia = avaliar(
        Cromossomo(vizinho_mais_proximo(cenario), (0,) * (n + 1), (True,) * 7), cenario
    )

    resultado = evoluir(
        cenario, ParametrosGA(tamanho_populacao=30, max_geracoes=20, semente=42), _Ignorar()
    )

    assert referencia.valido  # R$ 2.465,42
    assert resultado.avaliacao.valido
    assert resultado.avaliacao.custo < referencia.custo


def _rodar(*argumentos: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "surveyor", *argumentos],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(RAIZ / "src")},
        check=False,
    )


@pytest.mark.lento
def test_otimizar_e_validar_pela_linha_de_comando_com_10_pontos_reais(tmp_path: Path) -> None:
    # Campus + 8 pontos do professor + as 2 extras reais, com o vento real.
    linhas = (DADOS / "coordenadas.csv").read_text(encoding="utf-8").splitlines(keepends=True)
    coordenadas = tmp_path / "coordenadas.csv"
    coordenadas.write_text("".join(linhas[:10]), encoding="utf-8")
    entradas = ["--coordenadas", str(coordenadas), "--extras", str(DADOS / "extras.csv")]
    entradas += ["--vento", str(DADOS / "vento.csv")]
    planos = []
    for execucao in ("a", "b"):
        saida = tmp_path / execucao / "plano_de_voo.csv"
        log = str(tmp_path / f"{execucao}.log")
        otimizar = _rodar(
            "--log-arquivo", log, "otimizar", "--rapido", "--semente", "7",
            "--saida", str(saida), *entradas,
        )  # fmt: skip
        assert otimizar.returncode == 0, otimizar.stderr
        planos.append(saida.read_text(encoding="utf-8"))

    validar = _rodar("--log-arquivo", str(tmp_path / "v.log"), "validar", str(saida), *entradas)

    assert validar.returncode == 0, validar.stderr
    assert planos[0] == planos[1]  # mesma semente, mesmo plano
    assert len(planos[0].splitlines()) == 1 + 11  # cabeçalho + 10 pontos + volta ao campus
