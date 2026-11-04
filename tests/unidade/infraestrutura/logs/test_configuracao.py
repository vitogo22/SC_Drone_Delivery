import logging
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest

from surveyor.infraestrutura.logs.configuracao import arquivo_da_execucao, configurar_logging


@pytest.fixture(autouse=True)
def _restaurar_logging_global() -> Iterator[None]:
    """configurar_logging mexe no logger raiz; devolve o estado original após cada teste."""
    raiz = logging.getLogger()
    handlers_originais, nivel_original = raiz.handlers[:], raiz.level
    yield
    for handler in raiz.handlers:
        if handler not in handlers_originais:
            handler.close()
    raiz.handlers[:] = handlers_originais
    raiz.setLevel(nivel_original)


def test_arquivo_recebe_debug_mesmo_com_terminal_em_info(tmp_path: Path) -> None:
    arquivo = tmp_path / "logs" / "execucao.log"

    configurar_logging("INFO", arquivo)
    logging.getLogger("surveyor.exemplo").info("geração 10: melhor custo 123")
    logging.getLogger("surveyor.exemplo").debug("pouso inserido no trecho 7")

    conteudo = arquivo.read_text(encoding="utf-8")
    assert "| INFO     | surveyor.exemplo | geração 10: melhor custo 123" in conteudo
    assert "| DEBUG    | surveyor.exemplo | pouso inserido no trecho 7" in conteudo


def test_terminal_mostra_so_o_nivel_pedido(capsys: pytest.CaptureFixture[str]) -> None:
    configurar_logging("WARNING")
    logging.getLogger("surveyor.exemplo").info("marco que não aparece")
    logging.getLogger("surveyor.exemplo").warning("situação suspeita")

    terminal = capsys.readouterr().err
    assert "situação suspeita" in terminal
    assert "marco que não aparece" not in terminal


def test_reconfigurar_substitui_os_handlers_em_vez_de_duplicar(tmp_path: Path) -> None:
    configurar_logging("INFO", tmp_path / "a.log")
    configurar_logging("DEBUG")

    raiz = logging.getLogger()
    assert len(raiz.handlers) == 1
    assert raiz.level == logging.DEBUG


def test_cada_execucao_tem_um_arquivo_com_data_e_hora() -> None:
    inicio = datetime(2026, 11, 3, 21, 5, 9)

    assert arquivo_da_execucao(inicio) == Path("logs/surveyor_20261103_210509.log")


def test_nivel_desconhecido_e_rejeitado() -> None:
    with pytest.raises(ValueError, match="nível de log inválido"):
        configurar_logging("VERBOSO")
