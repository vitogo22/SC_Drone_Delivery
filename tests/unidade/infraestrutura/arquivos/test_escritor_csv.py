from pathlib import Path

from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.infraestrutura.arquivos.escritor_csv import escrever_plano

CABECALHO = (
    "CEP inicial,Latitude inicial,Longitude inicial,Dia do vôo,Hora inicial,Velocidade,"
    "CEP final,Latitude final,Longitude final,Pouso,Hora final"
)
CAMPUS = Coordenada("82821020", "-25.4233146347775", "-49.2160678044742")
PONTO = Coordenada("01001000", "-25.4300000000000", "-49.2000000000000")  # zeros no fim
EXTRA = Coordenada("24100467", "-25.4206324100467", "-49.2191752000000", pode_pousar=False)

PLANO = PlanoDeVoo(
    (
        Trecho(CAMPUS, PONTO, 1, 6 * 3600, 40, False, 6 * 3600 + 149),
        Trecho(PONTO, EXTRA, 1, 6 * 3600 + 149, 80, False, 6 * 3600 + 250),
        Trecho(EXTRA, CAMPUS, 1, 6 * 3600 + 250, 36, True, 6 * 3600 + 480),
    )
)


def _linhas(caminho: Path) -> list[str]:
    return caminho.read_text(encoding="utf-8").splitlines()


def test_cabecalho_tem_as_11_colunas_do_enunciado(tmp_path: Path) -> None:
    caminho = tmp_path / "plano.csv"

    escrever_plano(PLANO, caminho)

    assert _linhas(caminho)[0] == CABECALHO


def test_cada_trecho_vira_uma_linha_com_latitude_antes_da_longitude(tmp_path: Path) -> None:
    caminho = tmp_path / "plano.csv"

    escrever_plano(PLANO, caminho)

    # Na entrada a longitude vem antes; na saída, a latitude. O texto sai idêntico ao lido.
    assert _linhas(caminho)[1:] == [
        "82821020,-25.4233146347775,-49.2160678044742,1,06:00:00,40,"
        "01001000,-25.4300000000000,-49.2000000000000,NÃO,06:02:29",
        "01001000,-25.4300000000000,-49.2000000000000,1,06:02:29,80,"
        "24100467,-25.4206324100467,-49.2191752000000,NÃO,06:04:10",
        "24100467,-25.4206324100467,-49.2191752000000,1,06:04:10,36,"
        "82821020,-25.4233146347775,-49.2160678044742,SIM,06:08:00",
    ]


def test_arquivo_em_utf8_com_hifen_ascii_e_fim_de_linha_unix(tmp_path: Path) -> None:
    caminho = tmp_path / "plano.csv"

    escrever_plano(PLANO, caminho)

    conteudo = caminho.read_bytes()
    assert "NÃO".encode() in conteudo
    assert "vôo".encode() in conteudo
    assert not conteudo.startswith(b"\xef\xbb\xbf")  # sem BOM
    assert b"\r" not in conteudo
    texto = conteudo.decode("utf-8")
    # fora do NÃO e do vôo, tudo é ASCII: nada de travessão ou sinal de menos tipográfico
    assert texto.replace("NÃO", "").replace("vôo", "").isascii()
    assert texto.endswith("\n")
