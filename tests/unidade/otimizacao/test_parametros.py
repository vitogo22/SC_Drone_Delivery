import pytest

from surveyor.dominio.erros import ErroConfiguracao
from surveyor.otimizacao.parametros import ParametrosGA


def test_modo_rapido_e_mais_curto_e_preserva_a_semente() -> None:
    rapido, completo = ParametrosGA.rapido(semente=7), ParametrosGA()

    assert rapido.max_geracoes < completo.max_geracoes
    assert rapido.tempo_limite_s < completo.tempo_limite_s
    assert rapido.semente == 7


@pytest.mark.parametrize(
    "campos",
    [
        {"tamanho_populacao": 1},
        {"max_geracoes": 0},
        {"geracoes_sem_melhora": 0},
        {"tempo_limite_s": 0},
        {"taxa_cruzamento": -0.1},
        {"taxa_mutacao": 1.5},
        {"proporcao_elite": 1.0},
        {"tamanho_torneio": 1},
        {"tamanho_populacao": 10, "tamanho_torneio": 11},
    ],
)
def test_parametros_fora_da_faixa_sao_rejeitados(campos: dict[str, float]) -> None:
    with pytest.raises(ErroConfiguracao):
        ParametrosGA(**campos)  # type: ignore[arg-type]
