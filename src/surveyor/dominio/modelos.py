"""Tipos compartilhados entre simulador, CSV de saída e validador.

Os modelos só guardam dados. As regras do enunciado (janela de horário, bateria,
velocidades permitidas) são verificadas pelo simulador e pelo validador. Assim o
validador consegue representar, e então apontar, um plano inválido lido de um CSV.
"""

import re
from dataclasses import dataclass

_PADRAO_CEP = re.compile(r"[0-9]{8}")


@dataclass(frozen=True, slots=True)
class Coordenada:
    """Ponto da lista. Latitude e longitude ficam como texto para sair idênticas no CSV."""

    cep: str
    latitude_texto: str
    longitude_texto: str
    pode_pousar: bool = True  # A6: coordenadas extras da equipe não recebem pouso

    def __post_init__(self) -> None:
        if _PADRAO_CEP.fullmatch(self.cep) is None:
            raise ValueError(f"CEP deve ter 8 dígitos: {self.cep!r}")
        for texto in (self.latitude_texto, self.longitude_texto):
            float(texto)  # levanta ValueError se não for número

    @property
    def latitude(self) -> float:
        """Latitude em graus decimais."""
        return float(self.latitude_texto)

    @property
    def longitude(self) -> float:
        """Longitude em graus decimais."""
        return float(self.longitude_texto)


@dataclass(frozen=True, slots=True)
class Trecho:
    """Uma linha do CSV de saída: voo de `origem` até `destino`, incluindo a parada."""

    origem: Coordenada
    destino: Coordenada
    dia: int
    hora_inicial_s: int
    velocidade_kmh: int  # velocidade ajustada, antes do efeito do vento
    pouso: bool
    hora_final_s: int  # chegada + parada (60 s sem pouso, 172 s com pouso)

    @property
    def duracao_s(self) -> int:
        """Tempo de voo do trecho, parada incluída."""
        return self.hora_final_s - self.hora_inicial_s


@dataclass(frozen=True, slots=True)
class PlanoDeVoo:
    """Sequência completa de trechos, do campus de volta ao campus."""

    trechos: tuple[Trecho, ...]

    @property
    def quantidade_pousos(self) -> int:
        """Total de pousos, incluindo os de fim de dia e o pouso final no campus."""
        return sum(1 for trecho in self.trechos if trecho.pouso)

    @property
    def tempo_total_voo_s(self) -> int:
        """Soma do tempo no ar (trechos + paradas); a espera em solo não entra (A5)."""
        return sum(trecho.duracao_s for trecho in self.trechos)
