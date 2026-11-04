"""Erros esperados do projeto.

Erro previsível (arquivo ruim, parâmetro inválido, plano que viola o enunciado) é subclasse de
`ErroSurveyor`; a interface o transforma em mensagem + código de saída 1. Argumento inválido em
função pura continua sendo `ValueError`. Bug não é capturado: deve aparecer com traceback.
"""


class ErroSurveyor(Exception):
    """Base de todos os erros esperados do projeto."""


class ErroConfiguracao(ErroSurveyor):
    """Parâmetro de configuração fora da faixa permitida."""


class ErroDados(ErroSurveyor):
    """Arquivo de entrada com formato ou conteúdo inválido."""


class ErroPlano(ErroSurveyor):
    """Plano de voo que viola uma regra do enunciado."""
