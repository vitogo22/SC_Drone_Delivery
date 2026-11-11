import dataclasses

import pytest

from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho

SEIS_HORAS = 6 * 3600


def test_coordenada_preserva_o_texto_original_inclusive_zero_final() -> None:
    coordenada = Coordenada("24100140", "-25.4387124100140", "-49.2000000000000")

    assert coordenada.latitude_texto == "-25.4387124100140"  # str(float) perderia o zero final
    assert coordenada.latitude == pytest.approx(-25.438712410014)
    assert coordenada.longitude == pytest.approx(-49.2)


@pytest.mark.parametrize(
    "cep",
    [
        "8282102",  # 7 dígitos
        "828210200",  # 9 dígitos
        "8282102a",
        "8282102" + chr(0x00B2),  # "²" passa em str.isdigit()
        "".join(chr(0xFF10 + int(d)) for d in "82821020"),  # dígitos de largura total
    ],
)
def test_coordenada_rejeita_cep_que_nao_tem_8_digitos_ascii(cep: str) -> None:
    with pytest.raises(ValueError, match="CEP"):
        Coordenada(cep, "-25.4", "-49.2")


def test_coordenada_rejeita_latitude_nao_numerica() -> None:
    with pytest.raises(ValueError, match="could not convert"):
        Coordenada("82821020", "-25,4", "-49.2")


def test_coordenada_extra_nao_pode_pousar(campus: Coordenada) -> None:
    extra = Coordenada("24100142", "-25.4387124100142", "-49.2000000000000", pode_pousar=False)

    assert campus.pode_pousar
    assert not extra.pode_pousar


def test_coordenada_e_imutavel(campus: Coordenada) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        campus.cep = "00000000"  # type: ignore[misc]


def test_duracao_do_trecho_inclui_a_parada(campus: Coordenada, ponto: Coordenada) -> None:
    voo_s, parada_s = 300, 60
    trecho = Trecho(campus, ponto, 1, SEIS_HORAS, 36, False, SEIS_HORAS + voo_s + parada_s)

    assert trecho.duracao_s == voo_s + parada_s


def test_plano_soma_so_o_tempo_no_ar_e_conta_os_pousos(
    campus: Coordenada, ponto: Coordenada
) -> None:
    plano = PlanoDeVoo(
        trechos=(
            Trecho(campus, ponto, 1, SEIS_HORAS, 40, True, SEIS_HORAS + 600),
            # a noite entre o dia 1 e o dia 6 é espera em solo e não entra no tempo de voo
            Trecho(ponto, campus, 6, SEIS_HORAS, 40, True, SEIS_HORAS + 900),
        )
    )

    assert plano.tempo_total_voo_s == 1500
    assert plano.quantidade_pousos == 2


def test_plano_vazio_nao_tem_voo_nem_pouso() -> None:
    plano = PlanoDeVoo(trechos=())

    assert plano.tempo_total_voo_s == 0
    assert plano.quantidade_pousos == 0
