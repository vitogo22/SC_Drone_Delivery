#!/usr/bin/env bash
# Hook SessionStart: sincroniza o repositório sempre que o Claude Code abre nesta pasta.
# - git fetch de origin;
# - git pull --ff-only no ramo atual, se ele tiver upstream (nunca cria merge nem perde alteração local);
# - avisa se o ramo está atrás de origin/main ou com alterações não commitadas.
# A mensagem aparece para o usuário (systemMessage) e entra no contexto do Claude (additionalContext).
set -u

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

ramo="$(git branch --show-current)"
linhas=()

if git fetch --quiet --prune origin 2>/dev/null; then
    if git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
        if saida="$(git pull --ff-only --quiet 2>&1)"; then
            linhas+=("git pull ok no ramo '${ramo}'.")
        else
            linhas+=("git pull --ff-only falhou no ramo '${ramo}' (alterações locais conflitantes ou histórico divergente): ${saida}")
        fi
    else
        linhas+=("Ramo '${ramo}' ainda sem upstream: só foi feito git fetch.")
    fi
else
    linhas+=("git fetch falhou (sem rede ou sem acesso ao origin); seguindo com o estado local.")
fi

if [ "${ramo}" != "main" ] && git rev-parse --verify --quiet origin/main >/dev/null; then
    atras="$(git rev-list --count HEAD..origin/main)"
    if [ "${atras}" -gt 0 ]; then
        linhas+=("O ramo '${ramo}' está ${atras} commit(s) atrás de origin/main: rode 'git rebase origin/main' antes de abrir o PR.")
    fi
fi

if [ -n "$(git status --porcelain)" ]; then
    linhas+=("Há alterações não commitadas no ramo '${ramo}'.")
fi

mensagem="[sincronizar-git] $(printf '%s ' "${linhas[@]}")"
python3 -c 'import json, sys
m = sys.argv[1].strip()
print(json.dumps({"systemMessage": m,
                  "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": m}},
                 ensure_ascii=False))' "${mensagem}" 2>/dev/null || echo "${mensagem}"
