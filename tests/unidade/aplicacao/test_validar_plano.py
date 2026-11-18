"""Caso de uso `validar`: lê o CSV do plano e os arquivos de entrada, confere e resume.

O plano é o caso feliz de test_simulador.py (campus -> A -> B -> C -> campus, vento de
9 km/h vindo do sul), aqui com C como coordenada extra da equipe.
"""

from pathlib import Path

import pytest

from surveyor.aplicacao import validar_plano
from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.infraestrutura.arquivos.escritor_csv import escrever_plano

CABECALHO = "cep,longitude,latitude\n"
CAMPUS = Coordenada("82821020", "-25.4000000000000", "-49.2000000000000")
A = Coordenada("80000001", "-25.3900000000000", "-49.2000000000000")
B = Coordenada("80000002", "-25.3800000000000", "-49.2000000000000")
C = Coordenada("80000003", "-25.3700000000000", "-49.2000000000000", pode_pousar=False)
PLANO = PlanoDeVoo(
    (
        Trecho(CAMPUS, A, 1, 21600, 36, False, 21749),
        Trecho(A, B, 1, 21749, 40, False, 21891),
        Trecho(B, C, 1, 21891, 44, False, 22027),
        Trecho(C, CAMPUS, 1, 22027, 36, True, 22644),
    )
)


def _csv_de_pontos(*pontos: Coordenada) -> str:
    return CABECALHO + "".join(f"{p.cep},{p.longitude_texto},{p.latitude_texto}\n" for p in pontos)


@pytest.fixture
def entrada(tmp_path: Path) -> ArquivosDeEntrada:
    coordenadas = tmp_path / "coordenadas.csv"
    coordenadas.write_text(_csv_de_pontos(CAMPUS, A, B), encoding="utf-8")
    extras = tmp_path / "extras.csv"
    extras.write_text(_csv_de_pontos(C), encoding="utf-8")
    vento = tmp_path / "vento.csv"
    linhas = [f"{dia},{bloco},9,S\n" for dia in range(1, 8) for bloco in (6, 9, 12, 15, 18)]
    vento.write_text("dia,hora_bloco,velocidade_kmh,direcao\n" + "".join(linhas), encoding="utf-8")
    return ArquivosDeEntrada(coordenadas=coordenadas, extras=extras, vento=vento)


def test_plano_certo_nao_tem_violacoes_e_traz_o_resumo(
    tmp_path: Path, entrada: ArquivosDeEntrada
) -> None:
    caminho = tmp_path / "plano.csv"
    escrever_plano(PLANO, caminho)

    conferencia = validar_plano.executar(caminho, entrada, Configuracao())

    assert conferencia.violacoes == ()
    resumo = conferencia.resumo
    assert (resumo.trechos, resumo.pousos, resumo.tempo_total_voo_s) == (4, 1, 1044)
    assert resumo.taxas_reais == pytest.approx(80.0)
    assert resumo.custo_reais == pytest.approx(1044 / 3600 * 80 + 80)  # A4: R$ 103,20


def test_csv_adulterado_e_apontado(tmp_path: Path, entrada: ArquivosDeEntrada) -> None:
    caminho = tmp_path / "plano.csv"
    escrever_plano(PLANO, caminho)
    texto = caminho.read_text(encoding="utf-8")
    # Pouso na extra C: a linha B -> C passa a dizer SIM.
    caminho.write_text(texto.replace("NÃO,06:07:07", "SIM,06:07:07"), encoding="utf-8")

    conferencia = validar_plano.executar(caminho, entrada, Configuracao())

    assert "linha 4: pouso na coordenada extra 80000003 (A6)" in conferencia.violacoes
