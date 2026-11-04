# Atalhos de desenvolvimento. Rode `make` para ver a lista.
# Usa o Python do .venv quando ele existe; senão, o python3 do sistema.
PY ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := ajuda

# Entrega: SÓ o que o professor precisa para ler, instalar e rodar, mais o que o enunciado exige.
# (sem .venv, .git, .github, .claude, Makefile, caches, logs soltos; ver skill preparar-entrega)
ENTREGA := ../Trabalho2_SC_Drone_Delivery.zip
CONTEUDO_ENTREGA := README.md pyproject.toml src tests dados docs resultados

.PHONY: ajuda instalar formatar lint tipos testar testar-tudo cobertura verificar \
        rapido completo validar limpar entrega

ajuda: ## Lista os comandos disponíveis
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-12s %s\n", $$1, $$2}'

instalar: ## Cria o .venv e instala o projeto com as ferramentas de desenvolvimento
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[dev]"

formatar: ## Formata o código e corrige o que o ruff souber corrigir
	$(PY) -m ruff format src tests
	$(PY) -m ruff check --fix src tests

lint: ## Verifica estilo e erros comuns (sem alterar nada)
	$(PY) -m ruff check src tests
	$(PY) -m ruff format --check src tests

tipos: ## Checagem estática de tipos (mypy strict)
	$(PY) -m mypy

testar: ## Roda os testes rápidos
	$(PY) -m pytest -m "not lento"

testar-tudo: ## Roda todos os testes, inclusive os lentos
	$(PY) -m pytest

cobertura: ## Testes + cobertura (terminal, resultados/cobertura.txt e HTML em resultados/cobertura/)
	@mkdir -p resultados
	$(PY) -m pytest --cov --cov-report=term-missing --cov-report=html:resultados/cobertura \
		| tee resultados/cobertura.txt

verificar: lint tipos cobertura ## Tudo o que precisa passar antes de um commit

rapido: ## Roda o algoritmo no modo rápido (para o professor reproduzir)
	$(PY) -m surveyor otimizar --rapido

completo: ## Roda o algoritmo com os parâmetros completos
	$(PY) -m surveyor otimizar

validar: ## Valida resultados/plano_de_voo.csv de forma independente
	$(PY) -m surveyor validar

limpar: ## Remove caches e artefatos gerados
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov resultados/cobertura build dist src/*.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

entrega: ## Gera o ZIP de entrega (lista fechada, a partir da main commitada) e o confere
	@test "$$(git branch --show-current)" = main || { echo "Gere a entrega a partir da main (git switch main && git pull --ff-only)."; exit 1; }
	@test -z "$$(git status --porcelain)" || { echo "Há alterações não commitadas: elas entram na main por PR antes da entrega."; exit 1; }
	git archive --format=zip --prefix=SC_Drone_Delivery/ -o $(ENTREGA) HEAD $(CONTEUDO_ENTREGA)
	.claude/skills/preparar-entrega/verificar_zip.sh $(ENTREGA)
	@echo "Entrega pronta em $(ENTREGA)"
