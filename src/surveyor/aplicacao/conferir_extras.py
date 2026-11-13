"""Caso de uso: conferir as coordenadas extras da equipe (Etapa 2)."""

from dataclasses import dataclass

from surveyor.aplicacao.configuracao import ArquivosDeEntrada, Configuracao, Integrante
from surveyor.dominio.erros import ErroDados
from surveyor.dominio.modelos import Coordenada
from surveyor.dominio.validacao.extras import ponto_mais_proximo, validar_extra
from surveyor.infraestrutura.arquivos.leitor_csv import ler_coordenadas, ler_extras


@dataclass(frozen=True, slots=True)
class ConferenciaExtra:
    """Resultado de uma extra: o ponto mais próximo na base consolidada e as violações."""

    integrante: Integrante
    extra: Coordenada
    mais_proximo: Coordenada
    distancia_m: float
    violacoes: tuple[str, ...]  # vazia = extra válida


def executar(entrada: ArquivosDeEntrada, config: Configuracao) -> list[ConferenciaExtra]:
    """Confere cada extra contra o professor e as outras extras (a linha i é do integrante i)."""
    professor = ler_coordenadas(entrada.coordenadas, config.regras)
    extras = ler_extras(entrada.extras)
    if len(extras) != len(config.equipe):
        raise ErroDados(
            f"{entrada.extras}: {len(extras)} coordenadas extras "
            f"para {len(config.equipe)} integrante(s)"
        )
    conferencias: list[ConferenciaExtra] = []
    for posicao, (integrante, extra) in enumerate(zip(config.equipe, extras, strict=True)):
        base = [*professor, *extras[:posicao], *extras[posicao + 1 :]]
        mais_proximo, distancia_m = ponto_mais_proximo(extra, base, config.regras)
        violacoes = validar_extra(extra, integrante.matricula, base, config.regras)
        conferencias.append(
            ConferenciaExtra(integrante, extra, mais_proximo, distancia_m, tuple(violacoes))
        )
    return conferencias
