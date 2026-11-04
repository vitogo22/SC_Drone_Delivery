"""Leitura e validação dos CSVs de entrada (Etapas 1 e 4).

API prevista:
- ler_coordenadas(caminho) -> list[Coordenada]     # colunas: cep, longitude, latitude (nesta ordem)
- ler_extras(caminho) -> list[Coordenada]          # pode_pousar=False (A6)
- ler_vento(caminho) -> tabela por (dia, bloco)
Problemas de formato viram ErroDados com nome do arquivo e número da linha.
"""
