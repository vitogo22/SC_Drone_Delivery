"""Experimentos: um fator por vez a partir da base, com o mesmo orçamento de avaliações."""

import csv
import dataclasses
from pathlib import Path

import pytest

from surveyor.aplicacao import experimentar
from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.otimizacao.parametros import ParametrosGA

CABECALHO = "cep,longitude,latitude\n"
PROFESSOR = (
    "82821020,-49.2000000000000,-25.4000000000000\n"
    "80000001,-49.2000000000000,-25.3900000000000\n"
    "80000002,-49.1900000000000,-25.3800000000000\n"
)
EXTRA = "24100467,-49.2050000000000,-25.3950000000000\n"
ORCAMENTO = 400  # avaliações por execução: população de 400 roda 1 geração


@pytest.fixture
def entrada(tmp_path: Path) -> ArquivosDeEntrada:
    coordenadas, extras, vento = (
        tmp_path / "coordenadas.csv",
        tmp_path / "extras.csv",
        tmp_path / "vento.csv",
    )
    coordenadas.write_text(CABECALHO + PROFESSOR, encoding="utf-8")
    extras.write_text(CABECALHO + EXTRA, encoding="utf-8")
    linhas = "".join(f"{d},{b},6,N\n" for d in range(1, 8) for b in (6, 9, 12, 15, 18))
    vento.write_text("dia,hora_bloco,velocidade_kmh,direcao\n" + linhas, encoding="utf-8")
    return ArquivosDeEntrada(coordenadas=coordenadas, extras=extras, vento=vento)


def _diferencas(a: object, b: object) -> set[str]:
    return {
        campo.name
        for campo in dataclasses.fields(a)  # type: ignore[arg-type]  # dataclass
        if getattr(a, campo.name) != getattr(b, campo.name)
    }


def test_cada_configuracao_muda_um_fator_da_base_com_o_mesmo_orcamento() -> None:
    base = Configuracao()

    experimentos = experimentar.configuracoes(base, orcamento=60_000)

    assert len(experimentos) == 18
    assert (experimentos[0].fator, experimentos[0].valor) == ("base", "padrão")
    orcamento_campos = {"max_geracoes", "geracoes_sem_melhora", "tempo_limite_s"}
    for experimento in experimentos:
        mudou = _diferencas(experimento.ga, base.ga) - orcamento_campos
        mudou |= _diferencas(experimento.operacao, base.operacao)
        assert len(mudou) <= 1, experimento
        assert experimento.ga.max_geracoes * experimento.ga.tamanho_populacao == 60_000
    fatores = {e.fator for e in experimentos}
    assert fatores == {
        "base", "população", "cruzamento", "mutação", "seleção", "elitismo", "semeadura",
        "valor da hora",
    }  # fmt: skip


@pytest.mark.parametrize("processos", [1, 2], ids=["no-processo", "em-paralelo"])
def test_executar_grava_uma_linha_por_execucao(
    tmp_path: Path, entrada: ArquivosDeEntrada, processos: int
) -> None:
    saida = tmp_path / "resultados" / "experimentos.csv"

    execucoes = experimentar.executar(
        entrada, saida, Configuracao(), sementes=(1, 2), processos=processos, orcamento=ORCAMENTO
    )

    assert len(execucoes) == 18 * 2
    assert all(execucao.valido for execucao in execucoes)
    with saida.open(encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    assert len(linhas) == 36
    assert {linha["semente"] for linha in linhas} == {"1", "2"}
    assert linhas[0]["fator"] == "base"


def test_mesma_semente_da_o_mesmo_custo(entrada: ArquivosDeEntrada, tmp_path: Path) -> None:
    def custos() -> list[float]:
        execucoes = experimentar.executar(
            entrada, tmp_path / "e.csv", Configuracao(), (3,), processos=1, orcamento=ORCAMENTO
        )
        return [execucao.custo_reais for execucao in execucoes]

    assert custos() == custos()


def test_tabela_resume_cada_configuracao() -> None:
    def execucao(valor: str, semente: int, custo: float) -> experimentar.Execucao:
        return experimentar.Execucao("população", valor, semente, custo, True, 15, 14.5, 300, 12.0)

    tabela = experimentar.tabela_markdown(
        [execucao("100", 1, 2400.0), execucao("100", 2, 2500.0), execucao("400", 1, 2390.5)]
    )

    linhas = tabela.splitlines()
    assert linhas[0].startswith("| Fator | Valor | Sementes | Melhor custo | Custo médio |")
    assert linhas[2] == (
        "| população | 100 | 2 | R$ 2.400,00 | R$ 2.450,00 | R$ 70,71 | 2/2 | 15 | 14,50 | 12 s |"
    )
    assert linhas[3].startswith("| população | 400 | 1 | R$ 2.390,50 | R$ 2.390,50 | - |")


def test_orcamento_menor_que_a_populacao_e_rejeitado() -> None:
    with pytest.raises(ValueError, match="orçamento"):
        experimentar.configuracoes(Configuracao(ga=ParametrosGA()), orcamento=100)
