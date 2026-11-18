"""Laço evolutivo: elitismo, os três critérios de parada e reprodutibilidade."""

from collections.abc import Iterator

import pytest

from surveyor.dominio.calculos.vento import Vento, blocos_de_vento
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.dominio.simulador import Cenario
from surveyor.otimizacao.algoritmo import Parada, evoluir
from surveyor.otimizacao.operadores import Cruzamento, Invalidos, Selecao
from surveyor.otimizacao.parametros import ParametrosGA
from surveyor.otimizacao.progresso import EstatisticasDaGeracao

CAMPUS = Coordenada("82821020", "-25.4000000000000", "-49.2000000000000")
# Seis pontos em volta do campus, a menos de 3 km: qualquer ordem fecha no dia 1.
PONTOS = tuple(
    Coordenada(f"8000000{i}", f"{-25.40 + dlat:.13f}", f"{-49.20 + dlon:.13f}")
    for i, (dlat, dlon) in enumerate(
        [(0.01, 0.0), (0.02, 0.01), (0.0, 0.02), (-0.01, 0.01), (-0.02, -0.01), (0.0, -0.02)]
    )
)


class Lista:
    """Observador de teste: guarda as estatísticas de cada geração."""

    def __init__(self) -> None:
        self.geracoes: list[EstatisticasDaGeracao] = []

    def registrar(self, estatisticas: EstatisticasDaGeracao) -> None:
        self.geracoes.append(estatisticas)


def _cenario() -> Cenario:
    regras = Regras()
    vento = {
        (dia, bloco): Vento(5, 90)
        for dia in range(1, regras.prazo_dias + 1)
        for bloco in blocos_de_vento(regras)
    }
    return Cenario.montar(CAMPUS, PONTOS, vento, regras, ParametrosOperacao())


def _parametros(**campos: object) -> ParametrosGA:
    base: dict[str, object] = {
        "tamanho_populacao": 12,
        "max_geracoes": 15,
        "geracoes_sem_melhora": 1000,
        "tempo_limite_s": 1000.0,
        "proporcao_elite": 0.1,  # 1 indivíduo de elite em 12
        "semente": 3,
    }
    return ParametrosGA(**{**base, **campos})  # type: ignore[arg-type]  # campos de ParametrosGA


def test_para_no_numero_maximo_de_geracoes_e_registra_cada_uma() -> None:
    observador = Lista()

    resultado = evoluir(_cenario(), _parametros(max_geracoes=15), observador)

    assert resultado.parada is Parada.GERACOES
    assert [e.geracao for e in observador.geracoes] == list(range(16))  # 0 = população inicial


def test_elitismo_o_melhor_custo_nunca_piora() -> None:
    observador = Lista()

    resultado = evoluir(_cenario(), _parametros(), observador)

    melhores = [e.melhor_custo for e in observador.geracoes]
    assert melhores == sorted(melhores, reverse=True)
    assert resultado.avaliacao.custo == melhores[-1]
    assert resultado.avaliacao.valido
    ultima = observador.geracoes[-1]
    assert ultima.pousos_do_melhor == resultado.avaliacao.plano.quantidade_pousos
    assert ultima.melhor_custo <= ultima.custo_medio <= ultima.pior_custo


def test_para_por_estagnacao() -> None:
    observador = Lista()

    resultado = evoluir(
        _cenario(), _parametros(max_geracoes=500, geracoes_sem_melhora=5), observador
    )

    assert resultado.parada is Parada.ESTAGNACAO
    ultimos = [e.melhor_custo for e in observador.geracoes[-6:]]
    assert len(set(ultimos)) == 1  # 5 gerações seguidas sem melhorar o melhor


def test_para_pelo_tempo_limite() -> None:
    def relogio() -> Iterator[float]:
        segundos = 0.0
        while True:
            yield segundos
            segundos += 1.0  # cada leitura do relógio avança 1 s

    ticks = relogio()
    observador = Lista()

    resultado = evoluir(
        _cenario(), _parametros(tempo_limite_s=2.5), observador, relogio=lambda: next(ticks)
    )

    assert resultado.parada is Parada.TEMPO
    assert observador.geracoes[-1].segundos_decorridos >= 2.5


@pytest.mark.parametrize("cruzamento", list(Cruzamento))
def test_mesma_semente_da_o_mesmo_resultado(cruzamento: Cruzamento) -> None:
    parametros = _parametros(max_geracoes=8, cruzamento=cruzamento)

    primeiro = evoluir(_cenario(), parametros, Lista())
    segundo = evoluir(_cenario(), parametros, Lista())

    assert primeiro.melhor == segundo.melhor
    assert primeiro.avaliacao.custo == segundo.avaliacao.custo


@pytest.mark.parametrize("selecao", list(Selecao))
def test_sem_elitismo_devolve_o_melhor_de_todas_as_geracoes(selecao: Selecao) -> None:
    observador = Lista()

    resultado = evoluir(_cenario(), _parametros(proporcao_elite=0.0, selecao=selecao), observador)

    assert resultado.avaliacao.custo == min(e.melhor_custo for e in observador.geracoes)


@pytest.mark.parametrize("modo", list(Invalidos))
def test_cada_tratamento_de_invalidos_termina_com_plano_valido(modo: Invalidos) -> None:
    resultado = evoluir(_cenario(), _parametros(invalidos=modo), Lista())

    assert resultado.avaliacao.valido
