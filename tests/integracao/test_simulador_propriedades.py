"""Propriedades do simulador com os pontos reais e 1.000 rotas sorteadas (Etapa 6.7).

As propriedades são conferidas de novo a partir das linhas do plano, sem usar o código interno
do simulador. Valem também para o plano parcial de uma simulação inválida.
"""

import random
from pathlib import Path

import pytest

from surveyor.dominio.calculos.bateria import consumo
from surveyor.dominio.modelos import PlanoDeVoo
from surveyor.dominio.regras import ParametrosOperacao, Regras
from surveyor.dominio.simulador import Cenario, DecisoesDeVoo, simular
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_extras, ler_vento

DADOS = Path(__file__).resolve().parents[2] / "dados"
ROTAS = 1000
SEMENTE = 67


@pytest.fixture(scope="module")
def cenario() -> Cenario:
    regras = Regras()
    campus, *professor = ler_coordenadas(DADOS / "coordenadas.csv", regras)  # campus é o 1º
    extras = ler_extras(DADOS / "extras.csv")
    vento = ler_vento(DADOS / "vento.csv", regras)
    return Cenario.montar(campus, [*professor, *extras], vento, regras, ParametrosOperacao())


def _menor_bateria(plano: PlanoDeVoo, regras: Regras) -> float:
    """Menor carga ao fim de cada linha, trocando a bateria a cada pouso."""
    bateria = menor = 1.0
    for trecho in plano.trechos:
        bateria -= consumo(trecho.duracao_s, trecho.velocidade_kmh, regras)
        menor = min(menor, bateria)
        if trecho.pouso:
            bateria = 1.0
    return menor


@pytest.mark.lento
def test_rotas_sorteadas_respeitam_bateria_horario_e_extras(cenario: Cenario) -> None:
    regras = cenario.regras
    quantidade = cenario.indice_campus  # os pontos a visitar são 0..N-1
    sorteio = random.Random(SEMENTE)
    for numero in range(ROTAS):
        decisoes = DecisoesDeVoo(
            rota=tuple(sorteio.sample(range(quantidade), quantidade)),
            velocidades_kmh=tuple(sorteio.choices(regras.velocidades_kmh, k=quantidade + 1)),
            dias=tuple(range(1, regras.prazo_dias + 1)),
        )

        plano = simular(decisoes, cenario).plano

        assert plano.trechos, f"rota {numero}: plano vazio"
        assert _menor_bateria(plano, regras) >= cenario.operacao.reserva_bateria, f"rota {numero}"
        assert max(t.hora_final_s for t in plano.trechos) <= regras.limite_pouso_s, f"rota {numero}"
        assert all(t.destino.pode_pousar for t in plano.trechos if t.pouso), f"rota {numero}"
