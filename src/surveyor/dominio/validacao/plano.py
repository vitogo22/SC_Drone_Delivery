"""Validador independente do plano de voo (Etapa 9).

Refaz as contas trecho a trecho com surveyor.dominio.calculos, mas NUNCA usa o simulador:
se os dois compartilhassem a lógica, um erro no simulador passaria despercebido.
(Regra conferida em tests/test_arquitetura.py.)
"""
