import logging
import re
from pathlib import Path
from typing import Any

import pytest

from surveyor import __version__
from surveyor.aplicacao import conferir_extras, otimizar_rota, validar_plano
from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao, Integrante
from surveyor.dominio.erros import ErroDados
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo
from surveyor.interface import cli


@pytest.fixture(autouse=True)
def chamadas_ao_logging(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, Path]]:
    """Troca configurar_logging por um gravador: o caplog continua capturando o log."""
    chamadas: list[tuple[str, Path]] = []
    monkeypatch.setattr(cli, "configurar_logging", lambda *args: chamadas.append(args))
    return chamadas


@pytest.fixture
def otimizar_falso(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Substitui o caso de uso e guarda os argumentos recebidos."""
    recebido: dict[str, Any] = {}

    def executar(entrada: ArquivosDeEntrada, saida: Path, config: Configuracao) -> PlanoDeVoo:
        recebido.update(entrada=entrada, saida=saida, config=config)
        return PlanoDeVoo(trechos=())

    monkeypatch.setattr(otimizar_rota, "executar", executar)
    return recebido


def test_versao_e_exibida(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as saida:
        cli.main(["--versao"])

    assert saida.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_sem_comando_e_erro_de_uso() -> None:
    with pytest.raises(SystemExit) as saida:
        cli.main([])

    assert saida.value.code == 2


def test_cada_execucao_grava_log_em_arquivo_proprio_por_padrao(
    otimizar_falso: dict[str, Any], chamadas_ao_logging: list[tuple[str, Path]]
) -> None:
    cli.main(["otimizar"])

    [(nivel, arquivo)] = chamadas_ao_logging
    assert nivel == "INFO"
    assert re.fullmatch(r"logs/surveyor_\d{8}_\d{6}\.log", arquivo.as_posix())


def test_opcoes_de_log_sao_repassadas(
    otimizar_falso: dict[str, Any], chamadas_ao_logging: list[tuple[str, Path]]
) -> None:
    cli.main(["--log-nivel", "DEBUG", "--log-arquivo", "saida.log", "otimizar"])

    assert chamadas_ao_logging == [("DEBUG", Path("saida.log"))]


def test_otimizar_usa_entradas_e_saida_padrao(otimizar_falso: dict[str, Any]) -> None:
    assert cli.main(["otimizar"]) == cli.SAIDA_OK

    assert otimizar_falso["entrada"] == ArquivosDeEntrada()
    assert otimizar_falso["saida"] == cli.PLANO_PADRAO
    assert otimizar_falso["config"] == Configuracao.para_execucao(semente=42)


def test_otimizar_rapido_repassa_a_semente(otimizar_falso: dict[str, Any]) -> None:
    cli.main(["otimizar", "--rapido", "--semente", "7"])

    assert otimizar_falso["config"] == Configuracao.para_execucao(rapido=True, semente=7)


def test_validar_com_violacoes_retorna_erro_e_lista_cada_uma(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(
        validar_plano, "executar", lambda *_: ["bateria abaixo da reserva na linha 3"]
    )

    assert cli.main(["validar", "plano.csv"]) == cli.SAIDA_ERRO
    assert "bateria abaixo da reserva na linha 3" in caplog.text


def test_validar_sem_violacoes_retorna_ok_e_usa_o_plano_padrao(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    recebido: list[Path] = []

    def validar(plano: Path, *_: object) -> list[str]:
        recebido.append(plano)
        return []

    monkeypatch.setattr(validar_plano, "executar", validar)

    assert cli.main(["validar"]) == cli.SAIDA_OK
    assert recebido == [cli.PLANO_PADRAO]
    assert "Plano válido" in caplog.text


def test_erro_esperado_vira_mensagem_e_codigo_1(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def falhar(*_: object) -> PlanoDeVoo:
        raise ErroDados("dados/coordenadas.csv, linha 3: latitude vazia")

    monkeypatch.setattr(otimizar_rota, "executar", falhar)

    assert cli.main(["otimizar"]) == cli.SAIDA_ERRO
    assert "linha 3: latitude vazia" in caplog.text


def test_erro_inesperado_nao_e_engolido(monkeypatch: pytest.MonkeyPatch) -> None:
    def falhar(*_: object) -> PlanoDeVoo:
        raise ZeroDivisionError

    monkeypatch.setattr(otimizar_rota, "executar", falhar)

    with pytest.raises(ZeroDivisionError):
        cli.main(["otimizar"])


def _conferencia(*violacoes: str) -> conferir_extras.ConferenciaExtra:
    return conferir_extras.ConferenciaExtra(
        integrante=Integrante("Ana Souza", "2011111111"),
        extra=Coordenada("11111111", "-25.4050011111111", "-49.2000000000000", pode_pousar=False),
        mais_proximo=Coordenada("82821020", "-25.4000000000000", "-49.2000000000000"),
        distancia_m=556.0849,
        violacoes=violacoes,
    )


def test_extras_imprime_a_tabela_do_documento_e_usa_as_entradas_padrao(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    recebido: list[ArquivosDeEntrada] = []

    def conferir(entrada: ArquivosDeEntrada, _: Configuracao) -> list[Any]:
        recebido.append(entrada)
        return [_conferencia()]

    monkeypatch.setattr(conferir_extras, "executar", conferir)

    assert cli.main(["extras"]) == cli.SAIDA_OK
    assert recebido == [ArquivosDeEntrada()]
    assert capsys.readouterr().out.splitlines() == [
        "| Integrante | Matrícula | CEP | Latitude | Longitude "
        "| Ponto mais próximo (CEP) | Distância (m) |",
        "|---|---|---|---|---|---|---|",
        "| Ana Souza | 2011111111 | 11111111 | -25.4050011111111 | -49.2000000000000 "
        "| 82821020 | 556.1 |",
    ]


def test_extras_com_violacao_retorna_erro_e_aponta_o_cep(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(
        conferir_extras, "executar", lambda *_: [_conferencia("a 99.0 m do CEP 80000000")]
    )

    assert cli.main(["extras"]) == cli.SAIDA_ERRO
    assert "CEP 11111111 (Ana Souza): a 99.0 m do CEP 80000000" in caplog.text
