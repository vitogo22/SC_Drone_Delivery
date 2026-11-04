import pytest

from surveyor.dominio.calculos.relogio import para_hhmmss, para_segundos

CASOS = [
    ("00:00:00", 0),
    ("06:00:00", 6 * 3600),
    ("08:59:59", 9 * 3600 - 1),
    ("17:00:01", 17 * 3600 + 1),
    ("19:00:00", 19 * 3600),
    ("23:59:59", 24 * 3600 - 1),
]


@pytest.mark.parametrize(("texto", "segundos"), CASOS)
def test_converte_hhmmss_em_segundos(texto: str, segundos: int) -> None:
    assert para_segundos(texto) == segundos


@pytest.mark.parametrize(("texto", "segundos"), CASOS)
def test_converte_segundos_em_hhmmss(texto: str, segundos: int) -> None:
    assert para_hhmmss(segundos) == texto


@pytest.mark.parametrize(
    "texto", ["6:00:00", "06:00", "06h00m00", "24:00:00", "12:60:00", "12:00:60", "", " 06:00:00"]
)
def test_rejeita_horario_invalido(texto: str) -> None:
    with pytest.raises(ValueError, match="horário"):
        para_segundos(texto)


@pytest.mark.parametrize("segundos", [-1, 24 * 3600])
def test_rejeita_segundos_fora_do_dia(segundos: int) -> None:
    with pytest.raises(ValueError, match="fora de um dia"):
        para_hhmmss(segundos)
