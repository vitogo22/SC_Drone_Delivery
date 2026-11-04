"""Regras das coordenadas extras da equipe (Etapa 2).

API prevista:
- validar_extra(extra, matricula, base, regras) -> list[str]   # violações; vazia = válida
13 casas na latitude e na longitude; uma delas termina com os 8 últimos dígitos da matrícula;
>= 100 m de qualquer ponto; < 1500 m de algum ponto do arquivo do professor.
"""
