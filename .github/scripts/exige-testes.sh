#!/usr/bin/env bash
# Regra do projeto: toda mudança de código vem com teste.
# Falha se o intervalo base...head altera arquivos .py em src/ sem alterar nenhum .py em tests/.
# Uso: .github/scripts/exige-testes.sh <base> [<head>]    (ex.: origin/main HEAD)
set -euo pipefail

base="${1:?uso: exige-testes.sh <base> [<head>]}"
head="${2:-HEAD}"

codigo="$(git diff --name-only "${base}...${head}" -- 'src/*.py')"
testes="$(git diff --name-only "${base}...${head}" -- 'tests/*.py')"

if [ -n "${codigo}" ] && [ -z "${testes}" ]; then
    echo "::error::Este PR muda código em src/ sem mudar nenhum teste em tests/."
    echo "Código alterado:"
    echo "${codigo}"
    echo "Toda feature ou correção vem com teste (skill desenvolver-demanda, Passo 4)."
    exit 1
fi

contar() { if [ -z "$1" ]; then echo 0; else echo "$1" | wc -l; fi; }
echo "ok: $(contar "${codigo}") arquivo(s) de código e $(contar "${testes}") de teste alterados."
