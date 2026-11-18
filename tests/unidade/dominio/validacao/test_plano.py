"""Validador independente: um plano certo passa e cada regra pega o seu plano adulterado.

O plano certo é o caso feliz do simulador, com as contas à mão em test_simulador.py:
campus -> A -> B -> C -> campus, no dia 1, com vento de 9 km/h vindo do sul.
"""

from collections.abc import Callable
from dataclasses import replace
from typing import Any

import pytest

from surveyor.dominio.calculos.vento import Vento, blocos_de_vento
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.dominio.validacao.plano import validar_plano

CAMPUS = Coordenada("82821020", "-25.4000000000000", "-49.2000000000000")
A = Coordenada("80000001", "-25.3900000000000", "-49.2000000000000")
B = Coordenada("80000002", "-25.3800000000000", "-49.2000000000000")
C = Coordenada("80000003", "-25.3700000000000", "-49.2000000000000")
PONTOS = (CAMPUS, A, B, C)

CERTO = (
    Trecho(CAMPUS, A, 1, 21600, 36, False, 21749),  # 06:00:00 -> 06:02:29
    Trecho(A, B, 1, 21749, 40, False, 21891),
    Trecho(B, C, 1, 21891, 44, False, 22027),
    Trecho(C, CAMPUS, 1, 22027, 36, True, 22644),  # pouso final no campus (A9)
)


def _vento_constante(velocidade_kmh: float) -> dict[tuple[int, int], Vento]:
    regras = Regras()
    return {
        (dia, bloco): Vento(velocidade_kmh, 180)  # vem do sul
        for dia in range(1, regras.prazo_dias + 1)
        for bloco in blocos_de_vento(regras)
    }


def _validar(
    trechos: tuple[Trecho, ...],
    pontos: tuple[Coordenada, ...] = PONTOS,
    vento_kmh: float = 9,
    operacao: ParametrosOperacao | None = None,
) -> list[str]:
    return validar_plano(
        PlanoDeVoo(trechos),
        pontos,
        _vento_constante(vento_kmh),
        Regras(),
        operacao or ParametrosOperacao(),
    )


def _trocar(posicao: int, **campos: Any) -> tuple[Trecho, ...]:
    """O plano certo com a linha `posicao` alterada."""
    return tuple(
        replace(trecho, **campos) if i == posicao else trecho for i, trecho in enumerate(CERTO)
    )


def _adiantar(segundos: int, a_partir_de: int = 0, **campos: Any) -> tuple[Trecho, ...]:
    """O plano certo com as linhas a partir de `a_partir_de` deslocadas no tempo."""
    return tuple(
        replace(
            trecho,
            hora_inicial_s=trecho.hora_inicial_s + segundos,
            hora_final_s=trecho.hora_final_s + segundos,
            **campos,
        )
        if i >= a_partir_de
        else trecho
        for i, trecho in enumerate(CERTO)
    )


def test_plano_certo_nao_tem_violacoes() -> None:
    assert _validar(CERTO) == []


def test_plano_vazio_e_invalido() -> None:
    assert _validar(()) == ["plano vazio"]


def test_pairar_mais_que_um_minuto_sem_pousar_e_permitido() -> None:
    # A21: o drone espera 60 s a mais em B antes de seguir; a bateria paga a espera.
    assert _validar(_adiantar(60, a_partir_de=2)) == []


Adulteracao = Callable[[], list[str]]


@pytest.mark.parametrize(
    ("adulterar", "motivo"),
    [
        pytest.param(
            lambda: _validar(CERTO[1:]),
            "linha 2: o plano deve começar no campus 82821020",
            id="nao-comeca-no-campus",
        ),
        pytest.param(
            lambda: _validar(CERTO[:-1]),
            "linha 4: o plano deve terminar no campus 82821020",
            id="nao-termina-no-campus",
        ),
        pytest.param(
            lambda: _validar(_trocar(3, pouso=False, hora_final_s=22644 - 112)),
            "linha 5: a última linha deve ter Pouso = SIM (A9)",
            id="ultima-linha-sem-pouso",
        ),
        pytest.param(
            lambda: _validar(_trocar(2, origem=A)),
            "linha 4: começa em 80000001, mas a linha anterior termina em 80000002",
            id="continuidade",
        ),
        pytest.param(
            lambda: _validar((*CERTO[:2], Trecho(B, A, 1, 21891, 44, False, 22027), *CERTO[3:])),
            "CEP 80000001 aparece 2 vezes como destino",
            id="cep-repetido",
        ),
        pytest.param(
            lambda: _validar(CERTO, pontos=(*PONTOS, replace(A, cep="80000004"))),
            "falta visitar 1 CEP: 80000004",
            id="cep-faltando",
        ),
        pytest.param(
            lambda: _validar(CERTO, pontos=(CAMPUS, replace(A, latitude_texto="-25.39"), B, C)),
            "linha 2: coordenadas do CEP 80000001 diferentes da entrada",
            id="coordenadas-diferentes",
        ),
        pytest.param(
            lambda: _validar(CERTO, pontos=(CAMPUS, A, B)),
            "linha 4: CEP 80000003 não está na entrada",
            id="cep-fora-da-entrada",
        ),
        pytest.param(
            lambda: _validar(_trocar(1, velocidade_kmh=38)),
            "linha 3: velocidade 38 km/h não permitida",
            id="velocidade-nao-permitida",
        ),
        pytest.param(
            lambda: _validar(_adiantar(0, dia=8)),
            "linha 2: dia 8 fora de 1 a 7",
            id="dia-fora-do-prazo",
        ),
        pytest.param(
            lambda: _validar(_adiantar(-3600)),
            "linha 2: Hora inicial 05:00:00 antes de 06:00:00",
            id="antes-da-janela",
        ),
        pytest.param(
            lambda: _validar(_adiantar(46200)),  # sai às 18:50:00 e pousa às 19:07:24
            "linha 5: Hora final 19:07:24 depois de 19:00:00",
            id="depois-da-janela",
        ),
        pytest.param(
            lambda: _validar(_trocar(1, hora_final_s=21892)),
            "linha 3: Hora final 06:04:52 difere da calculada em +1 s",
            id="hora-final-errada",
        ),
        pytest.param(
            lambda: _validar(CERTO, vento_kmh=40),
            "linha 2: vento de 40 km/h não deixa o drone a 36 km/h manter o rumo",
            id="vento-mais-forte-que-o-drone",
        ),
        pytest.param(
            lambda: _validar(_trocar(2, hora_inicial_s=21890)),
            "linha 4: Hora inicial 06:04:50 antes da Hora final da linha anterior (06:04:51)",
            id="linhas-sobrepostas",
        ),
        pytest.param(
            lambda: _validar(CERTO, operacao=ParametrosOperacao(reserva_bateria=0.9)),
            "abaixo da reserva de 90%",
            id="bateria-abaixo-da-reserva",
        ),
        pytest.param(
            lambda: _validar(
                _trocar(0, pouso=True, hora_final_s=21749 + 112),
                pontos=(CAMPUS, replace(A, pode_pousar=False), B, C),
            ),
            "linha 2: pouso na coordenada extra 80000001 (A6)",
            id="pouso-em-extra",
        ),
        pytest.param(
            lambda: _validar(_adiantar(0, a_partir_de=1, dia=2)),
            "linha 3: o dia 1 termina sem pouso",
            id="dia-termina-sem-pouso",
        ),
        pytest.param(
            lambda: _validar(_trocar(0, dia=2)),
            "linha 3: dia 1 depois do dia 2",
            id="dia-volta-para-tras",
        ),
    ],
)
def test_plano_adulterado_e_apontado(adulterar: Adulteracao, motivo: str) -> None:
    violacoes = adulterar()

    assert any(motivo in violacao for violacao in violacoes), violacoes
