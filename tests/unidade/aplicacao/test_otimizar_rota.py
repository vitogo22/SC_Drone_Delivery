"""Caso de uso `otimizar`: lê as entradas, roda o GA, valida e grava plano e progresso."""

import csv
from pathlib import Path

import pytest

from surveyor.aplicacao import otimizar_rota
from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao
from surveyor.dominio.erros import ErroPlano
from surveyor.dominio.modelos import Trecho
from surveyor.infraestrutura.arquivos.leitor_csv import ler_plano
from surveyor.otimizacao.parametros import ParametrosGA

CABECALHO = "cep,longitude,latitude\n"
# O campus não precisa ser a primeira linha: o caso de uso o acha pelo CEP.
PROFESSOR = (
    "80000001,-49.2000000000000,-25.3900000000000\n"
    "82821020,-49.2000000000000,-25.4000000000000\n"
    "80000002,-49.1900000000000,-25.3800000000000\n"
    "80000003,-49.2100000000000,-25.4100000000000\n"
)
EXTRA = "24100467,-49.2050000000000,-25.3950000000000\n"
LONGE = "80000009,-48.2000000000000,-25.4000000000000\n"  # ~100 km: nenhum voo alcança
GA_PEQUENO = ParametrosGA(tamanho_populacao=6, max_geracoes=5, semente=1)


def _entrada(pasta: Path, professor: str = PROFESSOR) -> ArquivosDeEntrada:
    coordenadas, extras, vento = (
        pasta / "coordenadas.csv",
        pasta / "extras.csv",
        pasta / "vento.csv",
    )
    coordenadas.write_text(CABECALHO + professor, encoding="utf-8")
    extras.write_text(CABECALHO + EXTRA, encoding="utf-8")
    linhas = "".join(f"{d},{b},6,N\n" for d in range(1, 8) for b in (6, 9, 12, 15, 18))
    vento.write_text("dia,hora_bloco,velocidade_kmh,direcao\n" + linhas, encoding="utf-8")
    return ArquivosDeEntrada(coordenadas=coordenadas, extras=extras, vento=vento)


def _linha(trecho: Trecho) -> tuple[object, ...]:
    return (
        trecho.origem.cep,
        trecho.destino.cep,
        trecho.dia,
        trecho.hora_inicial_s,
        trecho.velocidade_kmh,
        trecho.pouso,
        trecho.hora_final_s,
    )


def test_grava_o_plano_validado_e_o_progresso_ao_lado(tmp_path: Path) -> None:
    saida = tmp_path / "resultados" / "plano_de_voo.csv"

    plano = otimizar_rota.executar(_entrada(tmp_path), saida, Configuracao(ga=GA_PEQUENO))

    # O CSV não diz quais pontos são extras (ler_plano): compara o conteúdo de cada linha.
    assert [_linha(t) for t in ler_plano(saida).trechos] == [_linha(t) for t in plano.trechos]
    destinos = sorted(trecho.destino.cep for trecho in plano.trechos)
    assert destinos == ["24100467", "80000001", "80000002", "80000003", "82821020"]
    with (saida.parent / "progresso.csv").open(encoding="utf-8") as arquivo:
        geracoes = [int(linha["geracao"]) for linha in csv.DictReader(arquivo)]
    assert geracoes == list(range(6))  # geração 0 (população inicial) até a 5
    assert (saida.parent / "convergencia.png").read_bytes().startswith(b"\x89PNG")
    assert (saida.parent / "rota.png").read_bytes().startswith(b"\x89PNG")


def test_melhor_plano_invalido_nao_e_gravado(tmp_path: Path) -> None:
    saida = tmp_path / "plano_de_voo.csv"
    entrada = _entrada(tmp_path, PROFESSOR + LONGE)

    with pytest.raises(ErroPlano, match="sem decolagem possível"):
        otimizar_rota.executar(entrada, saida, Configuracao(ga=GA_PEQUENO))

    assert not saida.exists()


def test_plano_reprovado_pelo_validador_nao_e_gravado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Rede de segurança: se o simulador errar, o validador independente barra a gravação.
    monkeypatch.setattr(otimizar_rota, "validar_plano", lambda *_: ["linha 3: bateria em -1%"])
    saida = tmp_path / "plano_de_voo.csv"

    with pytest.raises(ErroPlano, match="não passou no validador: linha 3: bateria em -1%"):
        otimizar_rota.executar(_entrada(tmp_path), saida, Configuracao(ga=GA_PEQUENO))

    assert not saida.exists()
