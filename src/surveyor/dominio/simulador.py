"""Decodificador: decisões de voo -> PlanoDeVoo sempre seguro (Etapa 6).

Recebe tipos simples (ordem dos pontos, velocidade por ponto, dias habilitados), nunca o
Cromossomo de surveyor.otimizacao: o domínio não depende do algoritmo genético.

Invariante: ao chegar a um ponto, o drone sempre tem bateria e horário para pousar ali
(ou, se for coordenada extra, para seguir até o próximo ponto onde pode pousar).
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from surveyor.dominio.calculos.custo import tempo_trecho_s
from surveyor.dominio.calculos.geo import matriz_distancias_km, matriz_rumos_graus
from surveyor.dominio.calculos.vento import Vento, bloco_do_horario, velocidade_solo_kmh
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import Regras


@dataclass(frozen=True, slots=True)
class Cenario:
    """Dados fixos de uma execução: montados uma vez e usados em todas as simulações."""

    pontos: tuple[Coordenada, ...]  # os N pontos a visitar e, no índice N, o campus
    distancias_km: tuple[tuple[float, ...], ...]  # [i][j] entre pontos[i] e pontos[j]
    rumos_graus: tuple[tuple[float, ...], ...]
    vento: Mapping[tuple[int, int], Vento]  # (dia, hora de início do bloco) -> previsão
    regras: Regras

    @classmethod
    def montar(
        cls,
        campus: Coordenada,
        pontos: Sequence[Coordenada],
        vento: Mapping[tuple[int, int], Vento],
        regras: Regras,
    ) -> "Cenario":
        """Põe o campus depois dos pontos a visitar e pré-calcula distâncias e rumos."""
        todos = (*pontos, campus)
        return cls(
            todos, matriz_distancias_km(todos, regras), matriz_rumos_graus(todos), vento, regras
        )

    @property
    def indice_campus(self) -> int:
        """Índice do campus em `pontos` (o último)."""
        return len(self.pontos) - 1


@dataclass(frozen=True, slots=True)
class DecisoesDeVoo:
    """O que o GA decide. O resto (pousos, esperas, troca de dia) o simulador deduz."""

    rota: tuple[int, ...]  # índices dos pontos a visitar, na ordem de visita (sem o campus)
    # Velocidade ajustada de cada trecho: [i] é o que chega a rota[i]; o último é a volta ao campus.
    velocidades_kmh: tuple[int, ...]
    dias: tuple[int, ...]  # dias em que o drone pode voar (1 a 7), em ordem crescente

    def __post_init__(self) -> None:
        trechos = len(self.rota) + 1
        if len(self.velocidades_kmh) != trechos:
            raise ValueError(
                f"{trechos} trechos (ida a cada ponto + volta ao campus), "
                f"mas {len(self.velocidades_kmh)} velocidades"
            )
        if list(self.dias) != sorted(set(self.dias)):
            raise ValueError(f"dias devem estar em ordem crescente, sem repetição: {self.dias}")


@dataclass(frozen=True, slots=True)
class ResultadoSimulacao:
    """Plano montado pelo simulador e, se ele não fecha no prazo, o motivo."""

    plano: PlanoDeVoo
    motivo_invalido: str | None = None

    @property
    def valido(self) -> bool:
        """O plano visita tudo e volta ao campus dentro das regras."""
        return self.motivo_invalido is None


def simular(decisoes: DecisoesDeVoo, cenario: Cenario) -> ResultadoSimulacao:
    """Voa a rota na ordem e nas velocidades decididas, do campus de volta ao campus."""
    campus = cenario.indice_campus
    dia = decisoes.dias[0]
    saida_s = cenario.regras.inicio_voos_s
    origem = campus
    trechos: list[Trecho] = []
    for destino, v_kmh in zip((*decisoes.rota, campus), decisoes.velocidades_kmh, strict=True):
        trecho = _voar(origem, destino, v_kmh, dia, saida_s, destino == campus, cenario)
        trechos.append(trecho)
        origem, saida_s = destino, trecho.hora_final_s
    return ResultadoSimulacao(PlanoDeVoo(tuple(trechos)))


def _voar(
    origem: int, destino: int, v_kmh: int, dia: int, saida_s: int, pouso: bool, cenario: Cenario
) -> Trecho:
    """Um trecho: vento pelo bloco da SAÍDA, tempo com teto e a parada no destino (A17)."""
    regras = cenario.regras
    vento = cenario.vento[(dia, bloco_do_horario(saida_s, regras))]
    v_solo_kmh = velocidade_solo_kmh(v_kmh, cenario.rumos_graus[origem][destino], vento)
    voo_s = tempo_trecho_s(cenario.distancias_km[origem][destino], v_solo_kmh)
    parada_s = regras.parada_com_pouso_s if pouso else regras.parada_sem_pouso_s
    return Trecho(
        origem=cenario.pontos[origem],
        destino=cenario.pontos[destino],
        dia=dia,
        hora_inicial_s=saida_s,
        velocidade_kmh=v_kmh,
        pouso=pouso,
        hora_final_s=saida_s + voo_s + parada_s,
    )
