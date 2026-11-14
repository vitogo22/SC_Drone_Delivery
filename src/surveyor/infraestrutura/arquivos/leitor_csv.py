"""Leitura e validação dos CSVs de entrada (Etapas 1 e 4) e do CSV do plano (Etapa 9).

- `ler_coordenadas(caminho, regras)`: arquivo do professor, com o campus obrigatório.
- `ler_extras(caminho)`: coordenadas da equipe, todas com `pode_pousar=False` (A6).
- `ler_vento(caminho, regras)`: previsão por (dia, bloco), um registro para cada par.
- `ler_plano(caminho)`: plano no formato de `escrever_plano`, para o validador conferir.

Coordenadas usam o formato `cep,longitude,latitude` (a longitude vem antes) e guardam CEP e
coordenadas como texto, para saírem idênticos no CSV do plano. Qualquer problema no arquivo
vira `ErroDados` com o arquivo e o número da linha.
"""

import csv
from collections.abc import Iterator
from pathlib import Path

from surveyor.dominio.calculos.relogio import para_segundos
from surveyor.dominio.calculos.vento import Vento, blocos_de_vento, direcao_em_graus
from surveyor.dominio.erros import ErroDados
from surveyor.dominio.modelos import Coordenada, PlanoDeVoo, Trecho
from surveyor.dominio.regras import Regras
from surveyor.infraestrutura.arquivos.escritor_csv import COLUNAS_PLANO, TEXTO_POUSO

COLUNAS_COORDENADAS = ("cep", "longitude", "latitude")
COLUNAS_VENTO = ("dia", "hora_bloco", "velocidade_kmh", "direcao")
POUSO_DO_TEXTO = {texto: pouso for pouso, texto in TEXTO_POUSO.items()}


def ler_coordenadas(caminho: Path, regras: Regras) -> list[Coordenada]:
    """Lê o CSV do professor; o campus precisa estar na lista."""
    coordenadas = _ler_pontos(caminho, pode_pousar=True)
    if all(coordenada.cep != regras.cep_campus for coordenada in coordenadas):
        raise ErroDados(f"{caminho}: campus {regras.cep_campus} ausente")
    return coordenadas


def ler_extras(caminho: Path) -> list[Coordenada]:
    """Lê as coordenadas extras da equipe, no mesmo formato do CSV do professor."""
    return _ler_pontos(caminho, pode_pousar=False)  # A6: nas extras o drone só fotografa


def ler_vento(caminho: Path, regras: Regras) -> dict[tuple[int, int], Vento]:
    """Lê a previsão de vento, indexada por (dia, hora de início do bloco)."""
    dias = range(1, regras.prazo_dias + 1)
    blocos = blocos_de_vento(regras)
    tabela: dict[tuple[int, int], Vento] = {}
    linha_da_chave: dict[tuple[int, int], int] = {}
    for numero, linha in _linhas_csv(caminho, COLUNAS_VENTO):
        try:
            dia, bloco = int(linha["dia"]), int(linha["hora_bloco"])
            velocidade_kmh = float(linha["velocidade_kmh"])
        except ValueError as erro:
            motivo = "dia e hora_bloco devem ser inteiros e velocidade_kmh, um número"
            raise _erro(caminho, numero, motivo) from erro
        try:
            vem_de_graus = direcao_em_graus(linha["direcao"])
        except ValueError as erro:
            raise _erro(caminho, numero, str(erro)) from erro
        if dia not in dias:
            raise _erro(caminho, numero, f"dia {dia} fora de 1 a {regras.prazo_dias}")
        if bloco not in blocos:
            lista = ", ".join(str(b) for b in blocos)
            raise _erro(caminho, numero, f"hora_bloco {bloco} não é um dos blocos usados ({lista})")
        if (dia, bloco) in linha_da_chave:
            anterior = linha_da_chave[(dia, bloco)]
            motivo = f"dia {dia}, bloco {bloco} repetido (já aparece na linha {anterior})"
            raise _erro(caminho, numero, motivo)
        linha_da_chave[(dia, bloco)] = numero
        tabela[(dia, bloco)] = Vento(velocidade_kmh, vem_de_graus)

    faltando = [
        f"({dia}, {bloco})" for dia in dias for bloco in blocos if (dia, bloco) not in tabela
    ]
    if faltando:
        raise ErroDados(f"{caminho}: faltam (dia, bloco): {', '.join(faltando)}")
    return tabela


def ler_plano(caminho: Path) -> PlanoDeVoo:
    """Lê um CSV de plano de voo, conferindo só o formato de cada valor.

    As regras do plano (velocidades, dias, horários, bateria) ficam com o validador, que precisa
    receber o plano errado para apontar o erro. O CSV não diz quais pontos são extras: todas as
    coordenadas saem com `pode_pousar=True`, e o validador confere CEPs, coordenadas e pousos
    contra os arquivos de entrada.
    """
    trechos: list[Trecho] = []
    for numero, linha in _linhas_csv(caminho, COLUNAS_PLANO):
        try:
            trechos.append(_trecho(linha))
        except ValueError as erro:
            raise _erro(caminho, numero, str(erro)) from erro
    return PlanoDeVoo(tuple(trechos))


def _trecho(linha: dict[str, str]) -> Trecho:
    """Uma linha do CSV do plano; levanta ValueError com o motivo se um valor está mal escrito."""
    pouso = POUSO_DO_TEXTO.get(linha["Pouso"])
    if pouso is None:
        raise ValueError(f"Pouso deve ser {' ou '.join(POUSO_DO_TEXTO)}: {linha['Pouso']!r}")
    return Trecho(
        origem=Coordenada(
            linha["CEP inicial"], linha["Latitude inicial"], linha["Longitude inicial"]
        ),
        destino=Coordenada(linha["CEP final"], linha["Latitude final"], linha["Longitude final"]),
        dia=_inteiro(linha, "Dia do vôo"),
        hora_inicial_s=para_segundos(linha["Hora inicial"]),
        velocidade_kmh=_inteiro(linha, "Velocidade"),
        pouso=pouso,
        hora_final_s=para_segundos(linha["Hora final"]),
    )


def _inteiro(linha: dict[str, str], coluna: str) -> int:
    try:
        return int(linha[coluna])
    except ValueError as erro:
        raise ValueError(f"{coluna} deve ser um número inteiro: {linha[coluna]!r}") from erro


def _ler_pontos(caminho: Path, *, pode_pousar: bool) -> list[Coordenada]:
    """Lê um CSV `cep,longitude,latitude` mantendo CEP e coordenadas como texto original."""
    pontos: list[Coordenada] = []
    linha_do_cep: dict[str, int] = {}
    for numero, linha in _linhas_csv(caminho, COLUNAS_COORDENADAS):
        try:
            ponto = Coordenada(
                cep=linha["cep"],
                latitude_texto=linha["latitude"],
                longitude_texto=linha["longitude"],
                pode_pousar=pode_pousar,
            )
        except ValueError as erro:
            raise _erro(caminho, numero, str(erro)) from erro
        if ponto.cep in linha_do_cep:
            motivo = f"CEP {ponto.cep} repetido (já aparece na linha {linha_do_cep[ponto.cep]})"
            raise _erro(caminho, numero, motivo)
        linha_do_cep[ponto.cep] = numero
        pontos.append(ponto)
    return pontos


def _linhas_csv(caminho: Path, colunas: tuple[str, ...]) -> Iterator[tuple[int, dict[str, str]]]:
    """Entrega (número da linha, valores) depois de conferir cabeçalho e quantidade de valores."""
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for coluna in colunas:
            if coluna not in (leitor.fieldnames or ()):
                raise _erro(caminho, 1, f"falta a coluna {coluna!r}")
        for linha in leitor:
            if None in linha or None in linha.values():
                motivo = f"esperava {len(colunas)} valores ({', '.join(colunas)})"
                raise _erro(caminho, leitor.line_num, motivo)
            yield leitor.line_num, linha


def _erro(caminho: Path, numero_linha: int, motivo: str) -> ErroDados:
    return ErroDados(f"{caminho}, linha {numero_linha}: {motivo}")
