"""Decodificador: decisões de voo -> PlanoDeVoo sempre seguro (Etapa 6).

Recebe tipos simples (ordem dos pontos, velocidade por ponto, dias habilitados), nunca o
Cromossomo de surveyor.otimizacao: o domínio não depende do algoritmo genético.

Invariante: ao chegar a um ponto, o drone sempre tem bateria e horário para pousar ali
(ou, se for coordenada extra, para seguir até o próximo ponto onde pode pousar).
"""

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import Enum

from surveyor.dominio.calculos.bateria import consumo
from surveyor.dominio.calculos.custo import tempo_trecho_s
from surveyor.dominio.calculos.geo import matriz_distancias_km, matriz_rumos_graus
from surveyor.dominio.calculos.vento import Vento, bloco_do_horario, velocidade_solo_kmh
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import SEGUNDOS_POR_HORA, ParametrosOperacao, Regras


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


# (origem, destino, velocidade ajustada em km/h), com índices de Cenario.pontos
Passo = tuple[int, int, int]


class _Falta(Enum):
    """O que impede o drone de chegar ao próximo pouso."""

    BATERIA = "bateria"
    HORARIO = "horário"


def simular(decisoes: DecisoesDeVoo, cenario: Cenario) -> ResultadoSimulacao:
    """Voa a rota na ordem e nas velocidades decididas, do campus de volta ao campus.

    Antes de cada trecho, confere se o drone consegue chegar ao próximo ponto onde pode pousar
    (o próprio destino ou, se ele for coordenada extra, o primeiro ponto do professor depois
    dela; A6) e pousar lá, com bateria acima da reserva e até o limite de operação. Se não
    consegue, ele pousa no ponto onde está: a linha anterior vira pouso e a bateria volta a
    100% (A10: os 172 s saem da bateria que chegou). Com a bateria cheia, `_decolagem` escolhe
    quando e a que velocidade sair; se não houver como, o plano é inválido.
    """
    regras = cenario.regras
    campus = cenario.indice_campus
    paradas = (*decisoes.rota, campus)
    trajeto = tuple(zip((campus, *decisoes.rota), paradas, decisoes.velocidades_kmh, strict=True))
    dias = iter(decisoes.dias)
    dia = next(dias, None)
    if dia is None:
        return ResultadoSimulacao(PlanoDeVoo(()), "nenhum dia habilitado para voar")
    saida_s = regras.inicio_voos_s
    bateria = 1.0
    trechos: list[Trecho] = []
    for posicao in range(len(trajeto)):
        caminho = _ate_o_proximo_pouso(trajeto, posicao, cenario)
        if _falta_no_caminho(bateria, saida_s, dia, caminho, cenario) is not None:
            if trechos and not trechos[-1].pouso:
                trechos[-1] = _com_pouso(trechos[-1], regras)
                saida_s = trechos[-1].hora_final_s
            bateria = 1.0
            dia, saida_s, possivel = _decolagem(caminho, dia, saida_s, dias, cenario)
            if possivel is None:
                cep_origem, cep_destino = (cenario.pontos[i].cep for i in caminho[0][:2])
                motivo = (
                    f"sem decolagem possível de {cep_origem} para {cep_destino} até o dia {dia}"
                )
                return ResultadoSimulacao(PlanoDeVoo(tuple(trechos)), motivo)
            caminho = possivel
        origem, destino, v_kmh = caminho[0]
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
        saida_s = trechos[-1].hora_final_s
    return ResultadoSimulacao(PlanoDeVoo(tuple(trechos)))


def _decolagem(
    caminho: Sequence[Passo], dia: int, saida_s: int, dias: Iterator[int], cenario: Cenario
) -> tuple[int, int, Sequence[Passo] | None]:
    """Com a bateria cheia, a primeira decolagem possível a partir de `saida_s` do `dia`.

    Se falta horário, o voo segue às 06:00:00 do próximo dia habilitado, na velocidade
    decidida. Se falta bateria, tenta as outras velocidades (da mais próxima da decidida para
    a mais distante), depois espera o próximo bloco de vento e, por fim, o próximo dia.
    Devolve (dia, saída, caminho), com o caminho None quando nada serve.
    """
    regras = cenario.regras
    while True:
        falta = _falta_no_caminho(1.0, saida_s, dia, caminho, cenario)
        if falta is None:
            return dia, saida_s, caminho
        if falta is _Falta.BATERIA:
            for alternativo in _com_outras_velocidades(caminho, regras):
                if _falta_no_caminho(1.0, saida_s, dia, alternativo, cenario) is None:
                    return dia, saida_s, alternativo
            bloco_atual_s = bloco_do_horario(saida_s, regras) * SEGUNDOS_POR_HORA
            proximo_bloco_s = bloco_atual_s + regras.duracao_bloco_vento_s
            if proximo_bloco_s < cenario.operacao.limite_operacional_s:
                saida_s = proximo_bloco_s
                continue
        proximo_dia = next(dias, None)
        if proximo_dia is None:
            return dia, saida_s, None
        dia, saida_s = proximo_dia, regras.inicio_voos_s


def _com_outras_velocidades(caminho: Sequence[Passo], regras: Regras) -> Iterable[Sequence[Passo]]:
    """O caminho com o primeiro passo em cada outra velocidade, da mais próxima da decidida."""
    origem, destino, decidida = caminho[0]
    outras = sorted(
        (v for v in regras.velocidades_kmh if v != decidida),
        key=lambda v: (abs(v - decidida), v),  # empate: a mais lenta, que gasta menos bateria
    )
    return (((origem, destino, v), *caminho[1:]) for v in outras)


def _ate_o_proximo_pouso(
    trajeto: Sequence[Passo], posicao: int, cenario: Cenario
) -> Sequence[Passo]:
    """Passos de `trajeto[posicao]` até o primeiro que chega a um ponto que aceita pouso (A6)."""
    fim = posicao
    while not cenario.pontos[trajeto[fim][1]].pode_pousar:  # o campus, no fim, sempre aceita
        fim += 1
    return trajeto[posicao : fim + 1]


def _falta_no_caminho(
    bateria: float, saida_s: int, dia: int, caminho: Sequence[Passo], cenario: Cenario
) -> _Falta | None:
    """Voa o caminho (foto nas extras, pouso no último): o que falta, ou None se dá."""
    regras = cenario.regras
    for numero, (origem, destino, v_kmh) in enumerate(caminho, start=1):
        voo_s = _tempo_de_voo_s(origem, destino, v_kmh, dia, saida_s, cenario)
        ultimo = numero == len(caminho)
        parada_s = regras.parada_com_pouso_s if ultimo else regras.parada_sem_pouso_s
        bateria -= consumo(voo_s + parada_s, v_kmh, regras)
        saida_s += voo_s + parada_s
        if bateria < cenario.operacao.reserva_bateria:
            return _Falta.BATERIA
        if saida_s > cenario.operacao.limite_operacional_s:  # 17:00:00 em ponto não paga (A11)
            return _Falta.HORARIO
    return None


def _tempo_de_voo_s(
    origem: int, destino: int, v_kmh: int, dia: int, saida_s: int, cenario: Cenario
) -> int:
    """Segundos no ar de `origem` a `destino`, com o vento do bloco da SAÍDA."""
    vento = cenario.vento[(dia, bloco_do_horario(saida_s, cenario.regras))]
    v_solo_kmh = velocidade_solo_kmh(v_kmh, cenario.rumos_graus[origem][destino], vento)
    return tempo_trecho_s(cenario.distancias_km[origem][destino], v_solo_kmh)


def _com_pouso(trecho: Trecho, regras: Regras) -> Trecho:
    """A parada de foto no destino vira pouso com troca de bateria (60 s -> 172 s)."""
    acrescimo_s = regras.parada_com_pouso_s - regras.parada_sem_pouso_s
    return replace(trecho, pouso=True, hora_final_s=trecho.hora_final_s + acrescimo_s)
