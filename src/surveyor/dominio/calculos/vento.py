"""Vento: bloco da tabela pela hora de saída e velocidade em solo (Etapa 4).

API prevista:
- bloco_do_horario(hora_saida_s) -> int            # 6, 9, 12, 15 ou 18; a coluna 21h nunca é usada
- velocidade_solo_kmh(v_kmh, rumo_graus, vento) -> float   # triângulo de velocidades (A2)
A tabela vem de dados/vento.csv, lida por surveyor.infraestrutura.arquivos.leitor_csv.
"""

from dataclasses import dataclass

from surveyor.dominio.calculos.relogio import para_hhmmss
from surveyor.dominio.regras import SEGUNDOS_POR_HORA, Regras

# Rosa dos ventos de 16 pontos, a partir do Norte em sentido horário (como na tabela Climatempo).
ROSA_DOS_VENTOS = (
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
)  # fmt: skip


def direcao_em_graus(nome: str) -> float:
    """Converte um ponto da rosa dos ventos (ex.: "SSE") em graus: N = 0, E = 90."""
    if nome not in ROSA_DOS_VENTOS:
        raise ValueError(f"direção do vento desconhecida: {nome!r}")
    return ROSA_DOS_VENTOS.index(nome) * 360 / len(ROSA_DOS_VENTOS)


@dataclass(frozen=True, slots=True)
class Vento:
    """Previsão de um bloco: velocidade em km/h e direção de onde o vento VEM, em graus."""

    velocidade_kmh: float
    vem_de_graus: float

    @property
    def sopra_para_graus(self) -> float:
        """Para onde o vento empurra o drone: o lado oposto de onde vem."""
        return (self.vem_de_graus + 180) % 360


def blocos_de_vento(regras: Regras) -> tuple[int, ...]:
    """Horas de início dos blocos da tabela que podem ser usados: 6, 9, 12, 15 e 18 (A15)."""
    inicios_s = range(regras.inicio_voos_s, regras.limite_pouso_s, regras.duracao_bloco_vento_s)
    return tuple(inicio_s // SEGUNDOS_POR_HORA for inicio_s in inicios_s)


def bloco_do_horario(hora_saida_s: int, regras: Regras) -> int:
    """Bloco da tabela pela hora de SAÍDA do trecho; o vento fica fixo até a chegada."""
    if not regras.inicio_voos_s <= hora_saida_s < regras.limite_pouso_s:
        raise ValueError(f"saída fora da janela de voo: {para_hhmmss(hora_saida_s)}")
    blocos_completos = (hora_saida_s - regras.inicio_voos_s) // regras.duracao_bloco_vento_s
    inicio_s = regras.inicio_voos_s + blocos_completos * regras.duracao_bloco_vento_s
    return inicio_s // SEGUNDOS_POR_HORA
