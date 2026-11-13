import pytest

from surveyor.dominio.calculos.vento import Vento, blocos_de_vento
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import ParametrosOperacao, Regras
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
    cenario = Cenario.montar(
        campus, (B, C, A), _vento_constante(9, 180), Regras(), ParametrosOperacao()
    )
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


def _ao_norte(graus: float, cep: str) -> Coordenada:
    return Coordenada(cep, f"{-25.40 + graus:.13f}", "-49.2000000000000")


def test_sem_bateria_para_pousar_no_destino_a_linha_anterior_vira_pouso(
    campus: Coordenada,
) -> None:
    # 80 km/h sem vento: autonomia de 1154,25 s. Pontos a cada 0,05° (5,5597 km = 251 s).
    # Antes de cada trecho, a bateria precisa cobrir o voo + 172 s de pouso no destino.
    #   campus -> P1: 1 - 423/1154,25 = 0,63 ok;  fica 1 - 311/1154,25 = 0,7306
    #   P1 -> P2:     0,7306 - 0,3665 = 0,36 ok;  fica 0,4611
    #   P2 -> P3:     0,4611 - 0,3665 = 0,09 ok;  fica 0,1917
    #   P3 -> campus: 16,679 km = 751 s; 0,1917 - 923/1154,25 < 0 -> pousa em P3, bateria 100%
    p1, p2, p3 = (_ao_norte(0.05 * i, f"8000001{i}") for i in (1, 2, 3))
    cenario = Cenario.montar(
        campus, (p1, p2, p3), _vento_constante(0, 0), Regras(), ParametrosOperacao()
    )
    decisoes = DecisoesDeVoo(rota=(0, 1, 2), velocidades_kmh=(80, 80, 80, 80), dias=(1,))

    resultado = simular(decisoes, cenario)

    assert resultado.valido
    assert resultado.plano.trechos == (
        Trecho(campus, p1, dia=1, hora_inicial_s=21600, velocidade_kmh=80, pouso=False,
               hora_final_s=21911),  # 251 + 60
        Trecho(p1, p2, dia=1, hora_inicial_s=21911, velocidade_kmh=80, pouso=False,
               hora_final_s=22222),
        Trecho(p2, p3, dia=1, hora_inicial_s=22222, velocidade_kmh=80, pouso=True,
               hora_final_s=22645),  # 251 + 172: a parada virou pouso
        Trecho(p3, campus, dia=1, hora_inicial_s=22645, velocidade_kmh=80, pouso=True,
               hora_final_s=23568),  # 751 + 172
    )  # fmt: skip


def _cenario_do_caso_feliz(campus: Coordenada, limite_operacional_s: int) -> Cenario:
    operacao = ParametrosOperacao(limite_operacional_s=limite_operacional_s)
    return Cenario.montar(campus, (B, C, A), _vento_constante(9, 180), Regras(), operacao)


DECISOES_DO_CASO_FELIZ = {"rota": (2, 0, 1), "velocidades_kmh": (36, 40, 44, 36)}


def test_pouso_que_termina_exatamente_no_limite_de_operacao_e_permitido(
    campus: Coordenada,
) -> None:
    cenario = _cenario_do_caso_feliz(campus, limite_operacional_s=22644)  # 06:17:24
    decisoes = DecisoesDeVoo(**DECISOES_DO_CASO_FELIZ, dias=(1, 3))

    resultado = simular(decisoes, cenario)

    assert [trecho.dia for trecho in resultado.plano.trechos] == [1, 1, 1, 1]
    assert resultado.plano.trechos[-1].hora_final_s == 22644


def test_fim_de_expediente_pousa_e_segue_no_proximo_dia_habilitado_as_6h(
    campus: Coordenada,
) -> None:
    # Limite de 06:15:00 (22500). Voltar ao campus saindo de C às 06:07:07 terminaria o pouso
    # às 06:17:24: não cabe. O drone pousa em C (06:07:07 + 112 s = 06:08:59), e mesmo assim
    # não cabe (06:08:59 + 617 s = 06:19:16). Segue no dia 3 (o 2 está desabilitado), às
    # 06:00:00, com a bateria nova: 445 s + 172 s -> 06:10:17.
    cenario = _cenario_do_caso_feliz(campus, limite_operacional_s=22500)
    decisoes = DecisoesDeVoo(**DECISOES_DO_CASO_FELIZ, dias=(1, 3))

    resultado = simular(decisoes, cenario)

    assert resultado.valido
    assert resultado.plano.trechos[2:] == (
        Trecho(B, C, dia=1, hora_inicial_s=21891, velocidade_kmh=44, pouso=True,
               hora_final_s=22139),  # pouso de fim de dia em C
        Trecho(C, campus, dia=3, hora_inicial_s=21600, velocidade_kmh=36, pouso=True,
               hora_final_s=22217),
    )  # fmt: skip


def test_sem_proximo_dia_habilitado_o_plano_e_invalido(campus: Coordenada) -> None:
    cenario = _cenario_do_caso_feliz(campus, limite_operacional_s=22500)
    decisoes = DecisoesDeVoo(**DECISOES_DO_CASO_FELIZ, dias=(1,))

    resultado = simular(decisoes, cenario)

    assert not resultado.valido
    assert "dia 1" in (resultado.motivo_invalido or "")
    assert len(resultado.plano.trechos) == 3  # o plano parcial termina com o pouso em C
    assert resultado.plano.trechos[-1].pouso


def test_sem_nenhum_dia_habilitado_o_plano_e_invalido(campus: Coordenada) -> None:
    cenario = _cenario_do_caso_feliz(campus, limite_operacional_s=22500)

    resultado = simular(DecisoesDeVoo(**DECISOES_DO_CASO_FELIZ, dias=()), cenario)

    assert not resultado.valido
    assert resultado.plano.trechos == ()
