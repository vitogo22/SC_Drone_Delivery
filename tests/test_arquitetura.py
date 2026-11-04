"""Regras de dependência entre camadas (docs/arquitetura.md), conferidas pelo AST dos imports.

A dependência sempre aponta para dentro: interface -> aplicacao -> otimizacao/infraestrutura
-> dominio. O domínio não conhece ninguém.
"""

import ast
from pathlib import Path

import pytest

PACOTE = Path(__file__).resolve().parents[1] / "src" / "surveyor"

# pasta (relativa ao pacote) -> prefixos de import proibidos para todo módulo dentro dela
PROIBIDOS: dict[str, tuple[str, ...]] = {
    "dominio": (
        "surveyor.aplicacao",
        "surveyor.infraestrutura",
        "surveyor.interface",
        "surveyor.otimizacao",
    ),
    # o validador precisa ser independente do simulador para pegar erros dele
    "dominio/validacao": ("surveyor.dominio.simulador",),
    "otimizacao": ("surveyor.aplicacao", "surveyor.infraestrutura", "surveyor.interface"),
    "infraestrutura": ("surveyor.aplicacao", "surveyor.interface"),
    "aplicacao": ("surveyor.interface",),
}

CASOS = [
    (pasta, arquivo) for pasta in PROIBIDOS for arquivo in sorted((PACOTE / pasta).rglob("*.py"))
]


def _modulos_importados(arquivo: Path) -> set[str]:
    nomes: set[str] = set()
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
            nomes.update(f"{no.module}.{alias.name}" for alias in no.names)
    return nomes


@pytest.mark.parametrize(
    ("pasta", "arquivo"),
    CASOS,
    ids=[str(arquivo.relative_to(PACOTE)) + f" [{pasta}]" for pasta, arquivo in CASOS],
)
def test_camada_nao_importa_camadas_proibidas(pasta: str, arquivo: Path) -> None:
    violacoes = sorted(n for n in _modulos_importados(arquivo) if n.startswith(PROIBIDOS[pasta]))

    assert not violacoes, f"{arquivo.relative_to(PACOTE)} não pode importar {violacoes}"


def test_detecta_import_proibido(tmp_path: Path) -> None:
    """Garante que o próprio verificador funciona (senão os testes acima passariam sempre)."""
    modulo = tmp_path / "exemplo.py"
    modulo.write_text(
        "from surveyor.dominio import simulador\nimport surveyor.otimizacao.fitness\n"
    )

    importados = _modulos_importados(modulo)

    assert {"surveyor.dominio.simulador", "surveyor.otimizacao.fitness"} <= importados
