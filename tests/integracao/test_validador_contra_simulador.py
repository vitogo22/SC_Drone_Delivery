"""O validador e o simulador, escritos sem código em comum, concordam nos pontos reais.

Rotas sorteadas não fecham em 7 dias (Etapa 6.7), então o plano do simulador é parcial: as
únicas violações aceitas são as de um plano que parou no meio. Bateria, horários, Hora final,
continuidade e pousos precisam bater. Metade das rotas usa só 40 pontos, para gerar também
planos completos (que o validador só reprova por faltarem os outros CEPs).
"""

import random
from pathlib import Path

import pytest

from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.dominio.simulador import Cenario, DecisoesDeVoo, simular
from surveyor.dominio.validacao.plano import validar_plano
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_extras, ler_vento

DADOS = Path(__file__).resolve().parents[2] / "dados"
ROTAS = 100
SEMENTE = 93
PONTOS_DA_ROTA_CURTA = 40
# Violações esperadas de um plano parcial (ou de uma rota que não passa por todos os pontos).
PARCIAL = ("falta visitar", "o plano deve terminar no campus")


@pytest.mark.lento
def test_planos_do_simulador_passam_no_validador() -> None:
    regras, operacao = Regras(), ParametrosOperacao()
    campus, *professor = ler_coordenadas(DADOS / "coordenadas.csv", regras)
    extras = ler_extras(DADOS / "extras.csv")
    vento = ler_vento(DADOS / "vento.csv", regras)
    entrada: list[Coordenada] = [campus, *professor, *extras]
    cenario = Cenario.montar(campus, [*professor, *extras], vento, regras, operacao)
    quantidade = cenario.indice_campus
    sorteio = random.Random(SEMENTE)
    completos = 0
    for numero in range(ROTAS):
        rota = tuple(sorteio.sample(range(quantidade), quantidade))
        if numero % 2:
            rota = rota[:PONTOS_DA_ROTA_CURTA]
        decisoes = DecisoesDeVoo(
            rota=rota,
            velocidades_kmh=tuple(sorteio.choices(regras.velocidades_kmh, k=len(rota) + 1)),
            dias=tuple(range(1, regras.prazo_dias + 1)),
        )
        resultado = simular(decisoes, cenario)

        violacoes = validar_plano(resultado.plano, entrada, vento, regras, operacao)

        inesperadas = [v for v in violacoes if not any(texto in v for texto in PARCIAL)]
        assert inesperadas == [], f"rota {numero}"
        completos += resultado.valido
    assert completos >= ROTAS // 2  # as rotas curtas fecham: houve planos completos conferidos
