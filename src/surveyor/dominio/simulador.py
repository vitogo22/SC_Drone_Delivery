"""Decodificador: decisões de voo -> PlanoDeVoo sempre seguro (Etapa 6).

Recebe tipos simples (ordem dos pontos, velocidade por ponto, dias habilitados), nunca o
Cromossomo de surveyor.otimizacao: o domínio não depende do algoritmo genético.

Invariante: ao chegar a um ponto, o drone sempre tem bateria e horário para pousar ali
(ou, se for coordenada extra, para seguir até o próximo ponto onde pode pousar).
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from surveyor.dominio.calculos.bateria import consumo
from surveyor.dominio.calculos.custo import tempo_trecho_s
from surveyor.dominio.calculos.geo import matriz_distancias_km, matriz_rumos_graus
from surveyor.dominio.calculos.vento import Vento, bloco_do_horario, velocidade_solo_kmh
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import ParametrosOperacao, Regras


@dataclass(frozen=True, slots=True)
class Cenario:
    """Dados fixos de uma execução: montados uma vez e usados em todas as simulações."""

    pontos: tuple[Coordenada, ...]  # os N pontos a visitar e, no índice N, o campus
    distancias_km: tuple[tuple[float, ...], ...]  # [i][j] entre pontos[i] e pontos[j]
    rumos_graus: tuple[tuple[float, ...], ...]
    vento: Mapping[tuple[int, int], Vento]  # (dia, hora de início do bloco) -> previsão
    regras: Regras
    operacao: ParametrosOperacao

    @classmethod
    def montar(
        cls,
        campus: Coordenada,
        pontos: Sequence[Coordenada],
        vento: Mapping[tuple[int, int], Vento],
        regras: Regras,
        operacao: ParametrosOperacao,
    ) -> "Cenario":
        """Põe o campus depois dos pontos a visitar e pré-calcula distâncias e rumos."""
        todos = (*pontos, campus)
        distancias_km = matriz_distancias_km(todos, regras)
        return cls(todos, distancias_km, matriz_rumos_graus(todos), vento, regras, operacao)

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
    """Voa a rota na ordem e nas velocidades decididas, do campus de volta ao campus.

    Antes de cada trecho, confere se depois dele o drone ainda consegue pousar no destino:
    com bateria acima da reserva e terminando o pouso até o limite de operação. Se não
    consegue, ele pousa no ponto onde está (a linha anterior vira pouso e a bateria volta a
    100%; A10: os 172 s saem da bateria que chegou). Se mesmo assim o horário não dá, o voo
    segue às 06:00:00 do próximo dia habilitado; sem próximo dia, o plano é inválido.
    """
    regras = cenario.regras
    campus = cenario.indice_campus
    dias = iter(decisoes.dias)
    dia = next(dias, None)
    if dia is None:
        return ResultadoSimulacao(PlanoDeVoo(()), "nenhum dia habilitado para voar")
    saida_s = regras.inicio_voos_s
    bateria = 1.0
    origem = campus
    trechos: list[Trecho] = []
    for destino, v_kmh in zip((*decisoes.rota, campus), decisoes.velocidades_kmh, strict=True):
        voo_s = _tempo_de_voo_s(origem, destino, v_kmh, dia, saida_s, cenario)
        if not (
            _cobre_voo_e_pouso(bateria, voo_s, v_kmh, cenario)
            and _pouso_no_horario(saida_s, voo_s, cenario)
        ):
            trechos[-1] = _com_pouso(trechos[-1], regras)
            bateria = 1.0
            saida_s = trechos[-1].hora_final_s
            voo_s = _tempo_de_voo_s(origem, destino, v_kmh, dia, saida_s, cenario)
            if not _pouso_no_horario(saida_s, voo_s, cenario):
                dia = next(dias, None)
                if dia is None:
                    motivo = (
                        f"a rota não termina: não há dia habilitado depois do dia {trechos[-1].dia}"
                    )
                    return ResultadoSimulacao(PlanoDeVoo(tuple(trechos)), motivo)
                saida_s = regras.inicio_voos_s
                voo_s = _tempo_de_voo_s(origem, destino, v_kmh, dia, saida_s, cenario)
        pouso = destino == campus  # A9: o pouso final no campus conta como pouso
        parada_s = regras.parada_com_pouso_s if pouso else regras.parada_sem_pouso_s
        trechos.append(
            Trecho(
                origem=cenario.pontos[origem],
                destino=cenario.pontos[destino],
                dia=dia,
                hora_inicial_s=saida_s,
                velocidade_kmh=v_kmh,
                pouso=pouso,
                hora_final_s=saida_s + voo_s + parada_s,
            )
        )
        bateria -= consumo(voo_s + parada_s, v_kmh, regras)  # A1: a parada na taxa do trecho
        origem, saida_s = destino, trechos[-1].hora_final_s
    return ResultadoSimulacao(PlanoDeVoo(tuple(trechos)))


def _tempo_de_voo_s(
    origem: int, destino: int, v_kmh: int, dia: int, saida_s: int, cenario: Cenario
) -> int:
    """Segundos no ar de `origem` a `destino`, com o vento do bloco da SAÍDA."""
    vento = cenario.vento[(dia, bloco_do_horario(saida_s, cenario.regras))]
    v_solo_kmh = velocidade_solo_kmh(v_kmh, cenario.rumos_graus[origem][destino], vento)
    return tempo_trecho_s(cenario.distancias_km[origem][destino], v_solo_kmh)


def _cobre_voo_e_pouso(bateria: float, voo_s: int, v_kmh: int, cenario: Cenario) -> bool:
    """Invariante: depois do voo, ainda sobra bateria para pousar no destino, acima da reserva."""
    gasto = consumo(voo_s + cenario.regras.parada_com_pouso_s, v_kmh, cenario.regras)
    return bateria - gasto >= cenario.operacao.reserva_bateria


def _pouso_no_horario(saida_s: int, voo_s: int, cenario: Cenario) -> bool:
    """O pouso no destino termina até o limite de operação (17:00:00 em ponto não paga; A11)."""
    fim_do_pouso_s = saida_s + voo_s + cenario.regras.parada_com_pouso_s
    return fim_do_pouso_s <= cenario.operacao.limite_operacional_s


def _com_pouso(trecho: Trecho, regras: Regras) -> Trecho:
    """A parada de foto no destino vira pouso com troca de bateria (60 s -> 172 s)."""
    acrescimo_s = regras.parada_com_pouso_s - regras.parada_sem_pouso_s
    return replace(trecho, pouso=True, hora_final_s=trecho.hora_final_s + acrescimo_s)
