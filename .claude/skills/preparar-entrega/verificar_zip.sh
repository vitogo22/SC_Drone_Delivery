#!/usr/bin/env bash
# Confere o ZIP de entrega do jeito que o professor vai usar.
# Uso: .claude/skills/preparar-entrega/verificar_zip.sh caminho/do/arquivo.zip
#   1. só o conteúdo permitido (nada de .venv, .git, .github, .claude, caches, logs soltos...)
#   2. os arquivos obrigatórios estão lá
#   3. ambiente limpo: python3 -m venv + pip install
#   4. testes + execução rápida + validação do plano
set -euo pipefail

zip="${1:?uso: verificar_zip.sh caminho/do/arquivo.zip}"
[ -f "${zip}" ] || { echo "ERRO: arquivo não encontrado: ${zip}"; exit 1; }

echo "== 1/4 Conteúdo proibido"
# Em qualquer nível: ambientes, controle de versão, ferramentas da equipe e caches.
# Só na raiz do projeto: logs/, build/, dist/ e venv/ (src/surveyor/infraestrutura/logs/ é código e fica).
proibidos='(^|/)(\.venv|\.git|\.github|\.claude|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|htmlcov|[^/]*\.egg-info)(/|$)|^[^/]+/(venv|logs|build|dist)/|(^|/)(CLAUDE\.md|Makefile|\.gitignore|\.gitattributes|\.editorconfig|\.coverage)$|\.(zip|pdf|pyc)$|resultados/cobertura/'
if unzip -Z1 "${zip}" | grep -E "${proibidos}"; then
    echo "ERRO: os itens acima não podem ir na entrega."
    exit 1
fi
echo "ok"

echo "== 2/4 Arquivos obrigatórios"
obrigatorios=(
    README.md pyproject.toml src/surveyor/__init__.py tests/test_arquitetura.py
    dados/coordenadas.csv dados/extras.csv dados/vento.csv
    docs/decisoes.md docs/coordenadas_extras.md docs/codificacao.md docs/experimentos.md
    resultados/plano_de_voo.csv resultados/progresso.csv resultados/cobertura.txt
)
faltando=0
for caminho in "${obrigatorios[@]}"; do
    if ! unzip -Z1 "${zip}" | grep -q -E "^[^/]+/${caminho}$"; then
        echo "FALTA: ${caminho}"
        faltando=1
    fi
done
[ "${faltando}" -eq 0 ] || { echo "ERRO: faltam arquivos obrigatórios."; exit 1; }
echo "ok"

echo "== 3/4 Instalação limpa (como o professor faz)"
tmp="$(mktemp -d)"
trap 'rm -rf "${tmp}"' EXIT
unzip -q "${zip}" -d "${tmp}/zip"
raiz="$(find "${tmp}/zip" -mindepth 1 -maxdepth 1 -type d | head -1)"
if ! python3 -m venv "${tmp}/venv"; then
    echo "ERRO: 'python3 -m venv' falhou. No Debian/Ubuntu: sudo apt install python3-venv"
    exit 2
fi
"${tmp}/venv/bin/python" -m pip install --quiet --upgrade pip
"${tmp}/venv/bin/python" -m pip install --quiet -e "${raiz}[dev]"
echo "ok"

echo "== 4/4 Testes, execução rápida e validação"
cd "${raiz}"
"${tmp}/venv/bin/python" -m pytest -q
"${tmp}/venv/bin/python" -m surveyor --log-arquivo "${tmp}/execucao.log" otimizar --rapido --saida "${tmp}/plano.csv"
"${tmp}/venv/bin/python" -m surveyor --log-arquivo "${tmp}/validacao.log" validar "${tmp}/plano.csv"

echo "OK: o ZIP está pronto para ser enviado."
