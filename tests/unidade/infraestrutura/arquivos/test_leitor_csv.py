from pathlib import Path

from surveyor.dominio.modelos import Coordenada
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas

CABECALHO = "cep,longitude,latitude\n"  # mesmo formato do arquivo do professor


def _gravar_csv(pasta: Path, conteudo: str) -> Path:
    caminho = pasta / "coordenadas.csv"
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def test_ler_coordenadas_poe_latitude_e_longitude_nos_campos_certos(tmp_path: Path) -> None:
    caminho = _gravar_csv(
        tmp_path,
        CABECALHO
        + "82821020,-49.2160678044742,-25.4233146347775\n"
        + "81350686,-49.3400481020638,-25.4936598469491\n"
        + "82530380,-49.2336060009616,-25.4300625729625\n",
    )

    coordenadas = ler_coordenadas(caminho)

    # No arquivo a longitude vem ANTES da latitude; no modelo, cada uma no seu campo.
    assert coordenadas == [
        Coordenada("82821020", "-25.4233146347775", "-49.2160678044742"),
        Coordenada("81350686", "-25.4936598469491", "-49.3400481020638"),
        Coordenada("82530380", "-25.4300625729625", "-49.2336060009616"),
    ]


def test_ler_coordenadas_preserva_o_texto_original(tmp_path: Path) -> None:
    caminho = _gravar_csv(tmp_path, CABECALHO + "01001000,-49.2000000000000,-25.4387124100140\n")

    [coordenada] = ler_coordenadas(caminho)

    assert coordenada.cep == "01001000"  # como número, perderia o zero à esquerda
    assert coordenada.latitude_texto == "-25.4387124100140"  # como float, perderia o zero final
    assert coordenada.longitude_texto == "-49.2000000000000"
