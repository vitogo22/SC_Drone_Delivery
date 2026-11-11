from pathlib import Path

import pytest

from surveyor.dominio.erros import ErroDados
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.regras import Regras
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_extras

CABECALHO = "cep,longitude,latitude\n"  # mesmo formato do arquivo do professor
CAMPUS = "82821020,-49.2160678044742,-25.4233146347775\n"
PONTO = "81350686,-49.3400481020638,-25.4936598469491\n"


def _gravar_csv(pasta: Path, conteudo: str) -> Path:
    caminho = pasta / "coordenadas.csv"
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def test_ler_coordenadas_poe_latitude_e_longitude_nos_campos_certos(tmp_path: Path) -> None:
    caminho = _gravar_csv(
        tmp_path,
        CABECALHO + CAMPUS + PONTO + "82530380,-49.2336060009616,-25.4300625729625\n",
    )

    coordenadas = ler_coordenadas(caminho, Regras())

    # No arquivo a longitude vem ANTES da latitude; no modelo, cada uma no seu campo.
    assert coordenadas == [
        Coordenada("82821020", "-25.4233146347775", "-49.2160678044742"),
        Coordenada("81350686", "-25.4936598469491", "-49.3400481020638"),
        Coordenada("82530380", "-25.4300625729625", "-49.2336060009616"),
    ]


def test_ler_coordenadas_preserva_o_texto_original(tmp_path: Path) -> None:
    caminho = _gravar_csv(
        tmp_path, CABECALHO + CAMPUS + "01001000,-49.2000000000000,-25.4387124100140\n"
    )

    [_, coordenada] = ler_coordenadas(caminho, Regras())

    assert coordenada.cep == "01001000"  # como número, perderia o zero à esquerda
    assert coordenada.latitude_texto == "-25.4387124100140"  # como float, perderia o zero final
    assert coordenada.longitude_texto == "-49.2000000000000"


@pytest.mark.parametrize(
    ("conteudo", "motivo"),
    [
        pytest.param(
            CABECALHO + CAMPUS + PONTO + PONTO,
            "linha 4: CEP 81350686 repetido (já aparece na linha 3)",
            id="cep-duplicado",
        ),
        pytest.param(
            CABECALHO + CAMPUS + "8135068,-49.3400481020638,-25.4936598469491\n",
            "linha 3: CEP deve ter 8 dígitos",
            id="cep-invalido",
        ),
        pytest.param(
            "cep,longitude\n82821020,-49.2160678044742\n",
            "linha 1: falta a coluna 'latitude'",
            id="coluna-faltando",
        ),
        pytest.param(
            CABECALHO + CAMPUS + "81350686,-49.3400481020638\n",
            "linha 3: esperava 3 valores (cep, longitude, latitude)",
            id="valor-faltando-na-linha",
        ),
        pytest.param(
            CABECALHO + PONTO,
            "campus 82821020 ausente",
            id="campus-ausente",
        ),
    ],
)
def test_ler_coordenadas_rejeita_arquivo_com_problema_apontando_arquivo_e_linha(
    tmp_path: Path, conteudo: str, motivo: str
) -> None:
    caminho = _gravar_csv(tmp_path, conteudo)

    with pytest.raises(ErroDados) as erro:
        ler_coordenadas(caminho, Regras())

    mensagem = str(erro.value)
    assert mensagem.startswith(str(caminho))  # o usuário sabe qual arquivo corrigir
    assert motivo in mensagem


def test_ler_extras_marca_todos_os_pontos_como_sem_pouso(tmp_path: Path) -> None:
    # Sem o campus: o arquivo de extras só tem as coordenadas da equipe.
    caminho = _gravar_csv(
        tmp_path,
        CABECALHO
        + "24100142,-49.2200000000000,-25.4387124100142\n"
        + "24100467,-49.2400000000000,-25.4412324100467\n",
    )

    extras = ler_extras(caminho)

    assert extras == [
        Coordenada("24100142", "-25.4387124100142", "-49.2200000000000", pode_pousar=False),
        Coordenada("24100467", "-25.4412324100467", "-49.2400000000000", pode_pousar=False),
    ]  # A6: nas extras o drone só fotografa


def test_ler_extras_rejeita_arquivo_com_problema(tmp_path: Path) -> None:
    extra = "24100142,-49.2200000000000,-25.4387124100142\n"
    caminho = _gravar_csv(tmp_path, CABECALHO + extra + extra)

    with pytest.raises(ErroDados, match="linha 3: CEP 24100142 repetido"):
        ler_extras(caminho)
