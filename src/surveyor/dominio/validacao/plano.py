"""Validador independente do plano de voo (Etapa 9).

`validar_plano(plano, pontos, vento, regras, operacao)` devolve as violações (lista vazia =
plano válido), cada uma com a linha do CSV (a 1 é o cabeçalho). Confere início e fim no
campus, continuidade, visitas, coordenadas da entrada, velocidades, dias, janela de horário,
Hora final recalculada, bateria, pouso em extra e o pouso no fim de cada dia.

Refaz as contas trecho a trecho com surveyor.dominio.calculos, mas NUNCA usa o simulador:
se os dois compartilhassem a lógica, um erro no simulador passaria despercebido.
(Regra conferida em tests/test_arquitetura.py.)
"""

from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from itertools import pairwise

from surveyor.dominio.calculos.bateria import consumo
from surveyor.dominio.calculos.custo import tempo_trecho_s
from surveyor.dominio.calculos.geo import distancia_km, rumo_graus
from surveyor.dominio.calculos.relogio import para_hhmmss
from surveyor.dominio.calculos.vento import Vento, bloco_do_horario, velocidade_solo_kmh
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import ParametrosOperacao, Regras


def validar_plano(
    plano: PlanoDeVoo,
    pontos: Sequence[Coordenada],
    vento: Mapping[tuple[int, int], Vento],
    regras: Regras,
    operacao: ParametrosOperacao,
) -> list[str]:
    """Violações do plano contra a entrada (`pontos`: professor, com o campus, e extras)."""
    trechos = plano.trechos
    if not trechos:
        return ["plano vazio"]
    entrada = {ponto.cep: ponto for ponto in pontos}
    return [
        *_inicio_e_fim(trechos, regras),
        *_visitas(trechos, entrada, regras),
        *(
            f"{_linha(numero)}: {violacao}"
            for numero, trecho in enumerate(trechos)
            for violacao in _trecho(trecho, entrada, vento, regras)
        ),
        *_sequencia(trechos),
        *_bateria(trechos, regras, operacao),
    ]


def _linha(numero: int) -> str:
    """Linha do CSV do trecho `numero` (0 = primeiro trecho, na linha 2)."""
    return f"linha {numero + 2}"


def _inicio_e_fim(trechos: Sequence[Trecho], regras: Regras) -> Iterator[str]:
    campus = regras.cep_campus
    if trechos[0].origem.cep != campus:
        yield f"{_linha(0)}: o plano deve começar no campus {campus}"
    ultima = _linha(len(trechos) - 1)
    if trechos[-1].destino.cep != campus:
        yield f"{ultima}: o plano deve terminar no campus {campus}"
    if not trechos[-1].pouso:
        yield f"{ultima}: a última linha deve ter Pouso = SIM (A9)"


def _visitas(
    trechos: Sequence[Trecho], entrada: Mapping[str, Coordenada], regras: Regras
) -> Iterator[str]:
    """Cada CEP da entrada, fora o campus (que pode ser revisitado, A20), é destino uma vez."""
    destinos = Counter(t.destino.cep for t in trechos if t.destino.cep != regras.cep_campus)
    for cep, vezes in destinos.items():
        if vezes > 1:
            yield f"CEP {cep} aparece {vezes} vezes como destino"
    faltando = [cep for cep in entrada if cep != regras.cep_campus and cep not in destinos]
    if faltando:
        plural = "CEP" if len(faltando) == 1 else "CEPs"
        yield f"falta visitar {len(faltando)} {plural}: {', '.join(faltando)}"


def _trecho(
    trecho: Trecho,
    entrada: Mapping[str, Coordenada],
    vento: Mapping[tuple[int, int], Vento],
    regras: Regras,
) -> Iterator[str]:
    """Regras de uma linha sozinha."""
    for ponto in (trecho.origem, trecho.destino):
        original = entrada.get(ponto.cep)
        if original is None:
            yield f"CEP {ponto.cep} não está na entrada"
        elif (ponto.latitude_texto, ponto.longitude_texto) != (
            original.latitude_texto,
            original.longitude_texto,
        ):
            yield f"coordenadas do CEP {ponto.cep} diferentes da entrada"
    destino = entrada.get(trecho.destino.cep)
    if trecho.pouso and destino is not None and not destino.pode_pousar:
        yield f"pouso na coordenada extra {destino.cep} (A6)"

    velocidade_ok = trecho.velocidade_kmh in regras.velocidades_kmh
    if not velocidade_ok:
        yield f"velocidade {trecho.velocidade_kmh} km/h não permitida (36 a 80, de 4 em 4; A7)"
    dia_ok = 1 <= trecho.dia <= regras.prazo_dias
    if not dia_ok:
        yield f"dia {trecho.dia} fora de 1 a {regras.prazo_dias}"
    saida_ok = trecho.hora_inicial_s >= regras.inicio_voos_s
    if not saida_ok:
        inicio = para_hhmmss(regras.inicio_voos_s)
        yield f"Hora inicial {para_hhmmss(trecho.hora_inicial_s)} antes de {inicio}"
    if trecho.hora_final_s > regras.limite_pouso_s:
        limite = para_hhmmss(regras.limite_pouso_s)
        yield f"Hora final {para_hhmmss(trecho.hora_final_s)} depois de {limite}"
    elif velocidade_ok and dia_ok and saida_ok:
        yield from _hora_final(trecho, vento, regras)


def _hora_final(
    trecho: Trecho, vento: Mapping[tuple[int, int], Vento], regras: Regras
) -> Iterator[str]:
    """Refaz a Hora final: vento do bloco da saída, tempo arredondado para cima e a parada."""
    previsao = vento[(trecho.dia, bloco_do_horario(trecho.hora_inicial_s, regras))]
    rumo = rumo_graus(trecho.origem, trecho.destino)
    try:
        v_solo_kmh = velocidade_solo_kmh(trecho.velocidade_kmh, rumo, previsao)
    except ValueError as erro:
        yield str(erro)
        return
    parada_s = regras.parada_com_pouso_s if trecho.pouso else regras.parada_sem_pouso_s
    voo_s = tempo_trecho_s(distancia_km(trecho.origem, trecho.destino, regras), v_solo_kmh)
    diferenca_s = trecho.hora_final_s - (trecho.hora_inicial_s + voo_s + parada_s)
    if diferenca_s:
        hora_final = para_hhmmss(trecho.hora_final_s)
        yield f"Hora final {hora_final} difere da calculada em {diferenca_s:+d} s"


def _sequencia(trechos: Sequence[Trecho]) -> Iterator[str]:
    """Regras entre uma linha e a anterior: lugar, dia e horário."""
    for numero, (anterior, atual) in enumerate(pairwise(trechos), start=1):
        linha = _linha(numero)
        if atual.origem.cep != anterior.destino.cep:
            yield (
                f"{linha}: começa em {atual.origem.cep}, "
                f"mas a linha anterior termina em {anterior.destino.cep}"
            )
        if atual.dia < anterior.dia:
            yield f"{linha}: dia {atual.dia} depois do dia {anterior.dia}"
        elif atual.dia > anterior.dia and not anterior.pouso:
            yield f"{linha}: o dia {anterior.dia} termina sem pouso"
        elif atual.dia == anterior.dia and atual.hora_inicial_s < anterior.hora_final_s:
            yield (
                f"{linha}: Hora inicial {para_hhmmss(atual.hora_inicial_s)} antes da Hora final "
                f"da linha anterior ({para_hhmmss(anterior.hora_final_s)})"
            )


def _bateria(
    trechos: Sequence[Trecho], regras: Regras, operacao: ParametrosOperacao
) -> Iterator[str]:
    """Carga ao fim de cada linha. Sem pouso, a espera no ar até a próxima saída também gasta
    (A21), na taxa do trecho que chegou (A1). Todo pouso troca a bateria."""
    bateria = 1.0
    for numero, trecho in enumerate(trechos):
        # Velocidade fora da lista não tem autonomia definida; a linha já foi apontada.
        if trecho.velocidade_kmh in regras.velocidades_kmh:
            pairando_s = 0
            proximo = trechos[numero + 1] if numero + 1 < len(trechos) else None
            if not trecho.pouso and proximo is not None and proximo.dia == trecho.dia:
                pairando_s = max(0, proximo.hora_inicial_s - trecho.hora_final_s)
            bateria -= consumo(trecho.duracao_s + pairando_s, trecho.velocidade_kmh, regras)
            if bateria < operacao.reserva_bateria:
                yield (
                    f"{_linha(numero)}: bateria em {bateria:.1%} ao fim da linha, "
                    f"abaixo da reserva de {operacao.reserva_bateria:.0%}"
                )
        if trecho.pouso:
            bateria = 1.0
