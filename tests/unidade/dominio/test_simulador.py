import pytest

from surveyor.dominio.calculos.vento import Vento, blocos_de_vento
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import Regras
from surveyor.dominio.simulador import Cenario, DecisoesDeVoo, ResultadoSimulacao, simular

# Três pontos ao norte do campus (-25.40), no mesmo meridiano, a 0,01° = 1,111949 km um do outro.
A = Coordenada("80000001", "-25.3900000000000", "-49.2000000000000")
B = Coordenada("80000002", "-25.3800000000000", "-49.2000000000000")
C = Coordenada("80000003", "-25.3700000000000", "-49.2000000000000")


def _vento_constante(velocidade_kmh: float, vem_de_graus: float) -> dict[tuple[int, int], Vento]:
    regras = Regras()
    return {
        (dia, bloco): Vento(velocidade_kmh, vem_de_graus)
        for dia in range(1, regras.prazo_dias + 1)
        for bloco in blocos_de_vento(regras)
    }


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


def test_caso_feliz_tres_pontos_sem_pouso_intermediario_calculado_a_mao(
    campus: Coordenada,
) -> None:
    # Vento de 9 km/h vindo do sul: empurra a ida (rumo 0°) e segura a volta (rumo 180°).
    #   campus -> A  36 km/h, solo 45: 1,111949 km / 45 x 3600 = 88,96 -> 89 s  + 60 s de foto
    #   A -> B       40 km/h, solo 49:                          81,69 -> 82 s  + 60 s
    #   B -> C       44 km/h, solo 53:                          75,53 -> 76 s  + 60 s
    #   C -> campus  36 km/h, solo 27: 3,335848 km / 27 x 3600 = 444,78 -> 445 s + 172 s de pouso
    # A bateria termina em ~80%: nenhum pouso no meio do caminho.
    cenario = Cenario.montar(campus, (B, C, A), _vento_constante(9, 180), Regras())
    decisoes = DecisoesDeVoo(rota=(2, 0, 1), velocidades_kmh=(36, 40, 44, 36), dias=(1,))

    resultado = simular(decisoes, cenario)

    assert resultado.valido
    assert resultado.plano.trechos == (
        Trecho(campus, A, dia=1, hora_inicial_s=21600, velocidade_kmh=36, pouso=False,
               hora_final_s=21749),  # 06:00:00 -> 06:02:29
        Trecho(A, B, dia=1, hora_inicial_s=21749, velocidade_kmh=40, pouso=False,
               hora_final_s=21891),  # 06:04:51
        Trecho(B, C, dia=1, hora_inicial_s=21891, velocidade_kmh=44, pouso=False,
               hora_final_s=22027),  # 06:07:07
        Trecho(C, campus, dia=1, hora_inicial_s=22027, velocidade_kmh=36, pouso=True,
               hora_final_s=22644),  # 06:17:24, pouso final no campus (A9)
    )  # fmt: skip
