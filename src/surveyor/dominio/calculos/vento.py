"""Vento: direção, bloco da tabela pela hora de saída e velocidade em solo (Etapa 4).

- `direcao_em_graus(nome)`: rosa dos ventos de 16 pontos, N = 0, sentido horário.
- `Vento`: velocidade em km/h e direção de onde VEM; `sopra_para_graus` é o lado oposto.
- `blocos_de_vento` e `bloco_do_horario`: blocos de 3 h a partir das 06:00, escolhidos pela
  hora de SAÍDA do trecho; a coluna 21h nunca é usada (A15).
- `velocidade_solo_kmh`: triângulo de velocidades, com o drone corrigindo o rumo (A2).

A tabela vem de dados/vento.csv, lida por surveyor.infraestrutura.arquivos.leitor_csv.
"""

import math
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


def velocidade_solo_kmh(v_kmh: float, rumo_graus: float, vento: Vento) -> float:
    """Velocidade em solo pelo triângulo de velocidades (A2).

    O drone aponta um pouco contra o vento lateral para seguir reto até o destino:
    a parte lateral do vento é anulada e só a parte ao longo do rumo soma ou subtrai.
    """
    w = vento.velocidade_kmh
    if w >= v_kmh:
        raise ValueError(f"vento de {w} km/h não deixa o drone a {v_kmh} km/h manter o rumo")
    alfa = math.radians(vento.sopra_para_graus - rumo_graus)
    return w * math.cos(alfa) + math.sqrt(v_kmh**2 - (w * math.sin(alfa)) ** 2)
