#!/usr/bin/env bash
# Painel do projeto: micro passos concluídos por etapa (na origin/main e no ramo atual)
# e o que está em andamento (ramos e PRs no GitHub). Uso: .claude/skills/desenvolver-demanda/painel.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

ETAPAS=".claude/skills/implementar-etapa/etapas.md"

resumir() {  # lê o etapas.md da entrada padrão: "Etapa N — título   feitos/total   próximo micro passo"
    awk '
        function fechar() {
            if (titulo != "") printf "  [%2d/%-2d] %s\n          %s\n", feitos, total, titulo, (proximo == "" ? "concluída" : "próximo: " proximo)
        }
        /^## Etapa / { fechar(); titulo = substr($0, 4); feitos = 0; total = 0; proximo = ""; next }
        /^- \[x\] / { feitos++; total++; next }
        /^- \[ \] / { total++; if (proximo == "") proximo = substr($0, 7) }
        END { fechar() }
    '
}

git fetch --quiet --prune origin 2>/dev/null || echo "(sem acesso ao origin: usando o estado local)"

echo "== Oficial: origin/main (só o que já foi mergeado)"
if ! git show "origin/main:${ETAPAS}" 2>/dev/null | resumir; then
    echo "  (etapas.md ainda não está na main: o PR da base precisa ser mergeado)"
fi

ramo="$(git branch --show-current)"
if [ "${ramo}" != "main" ]; then
    echo "== Ramo atual: ${ramo} (inclui o que ainda não foi mergeado)"
    resumir < "${ETAPAS}"
fi

echo "== Em andamento no GitHub (ramos além da main)"
git for-each-ref --format='%(refname:short)|%(committerdate:relative)' refs/remotes/origin \
    | awk -F'|' '$1 != "origin" && $1 != "origin/HEAD" && $1 != "origin/main" { printf "  %s  (último commit: %s)\n", $1, $2; n++ }
                 END { if (n == 0) print "  (nenhum)" }'

if command -v gh >/dev/null 2>&1; then
    echo "== Pull Requests abertos"
    gh pr list --state open 2>/dev/null || echo "  (gh sem login: rode 'gh auth login')"
fi
