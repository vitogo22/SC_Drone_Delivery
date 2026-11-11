#!/usr/bin/env bash
# Painel do projeto (fluxo solo, direto na main): micro passos concluídos por etapa na main
# local e quantos commits ainda faltam enviar ao GitHub. Uso: .claude/skills/desenvolver-demanda/painel.sh
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

echo "== Etapas (ramo $(git branch --show-current), incluindo o que ainda não foi enviado)"
resumir < "${ETAPAS}"

echo "== GitHub"
if git rev-parse --verify --quiet origin/main >/dev/null; then
    frente="$(git rev-list --count origin/main..HEAD)"
    atras="$(git rev-list --count HEAD..origin/main)"
    if [ "${frente}" -gt 0 ]; then echo "  ${frente} commit(s) ainda não enviados: o Matheus roda 'git push origin main'"; fi
    if [ "${atras}" -gt 0 ]; then echo "  ${atras} commit(s) no GitHub que não estão aqui: 'git pull --ff-only'"; fi
    if [ "${frente}" -eq 0 ] && [ "${atras}" -eq 0 ]; then echo "  em dia com origin/main"; fi
fi
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "  há alterações não commitadas"
fi
