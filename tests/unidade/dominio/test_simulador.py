import pytest

from surveyor.dominio.modelos import PlanoDeVoo
from surveyor.dominio.simulador import DecisoesDeVoo, ResultadoSimulacao


def test_decisoes_guardam_rota_velocidade_de_cada_trecho_e_dias() -> None:
    decisoes = DecisoesDeVoo(rota=(2, 0, 1), velocidades_kmh=(36, 80, 44, 40), dias=(1, 3, 6))

    assert decisoes.rota == (2, 0, 1)
    assert decisoes.velocidades_kmh == (36, 80, 44, 40)
    assert decisoes.dias == (1, 3, 6)


@pytest.mark.parametrize(
    "velocidades_kmh", [(36, 36, 36), (36, 36, 36, 36, 36)], ids=["falta a volta", "sobra uma"]
)
def test_decisoes_exigem_uma_velocidade_por_trecho(velocidades_kmh: tuple[int, ...]) -> None:
    with pytest.raises(ValueError, match="4 trechos"):
        DecisoesDeVoo(rota=(2, 0, 1), velocidades_kmh=velocidades_kmh, dias=(1,))


@pytest.mark.parametrize("dias", [(3, 1), (1, 1, 2)], ids=["fora de ordem", "repetido"])
def test_decisoes_exigem_dias_em_ordem_crescente_sem_repeticao(dias: tuple[int, ...]) -> None:
    with pytest.raises(ValueError, match="ordem crescente"):
        DecisoesDeVoo(rota=(0,), velocidades_kmh=(36, 36), dias=dias)


def test_resultado_sem_motivo_e_valido() -> None:
    assert ResultadoSimulacao(PlanoDeVoo(trechos=())).valido


def test_resultado_com_motivo_e_invalido() -> None:
    resultado = ResultadoSimulacao(PlanoDeVoo(trechos=()), motivo_invalido="passou do dia 7")

    assert not resultado.valido
