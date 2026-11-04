#!/usr/bin/env bash
# Diagnóstico de quem está trabalhando, desta máquina e da configuração da equipe no GitHub.
# Os códigos (P1, V1, M3...) são os itens de .claude/skills/proximo-passo/onboarding.md.
# Uso: .claude/skills/proximo-passo/diagnostico.sh
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

REPO="vitogo22/SC_Drone_Delivery"
ok()    { printf '  [ok]       %s\n' "$1"; }
falta() { printf '  [PENDENTE] %s\n' "$1"; }
info()  { printf '  [info]     %s\n' "$1"; }

echo "== Quem está trabalhando"
nome="$(git config user.name || true)"
email="$(git config user.email || true)"
case "$(printf '%s %s' "${nome}" "${email}" | tr '[:upper:]' '[:lower:]')" in
    *vitor*|*vitogo22*) pessoa="Vitor" ;;
    *matheus*|*biesek*) pessoa="Matheus" ;;
    *) pessoa="desconhecida (pergunte quem é)" ;;
esac
info "git: ${nome:-?} <${email:-?}>  ->  pessoa: ${pessoa}"
case "${email}" in
    ""|*@email.com|*@example.com|*@localhost*) falta "P1 e-mail do git não é o da conta GitHub: '${email}'" ;;
    *) ok "P1 e-mail do git real" ;;
esac
if [ "$(printf '%s' "${nome}" | wc -w)" -ge 2 ]; then ok "P1 nome completo no git"; else falta "P1 user.name sem o nome completo: '${nome}'"; fi

echo "== Ferramentas desta máquina"
case "$(uname -r)" in *[Mm]icrosoft*|*WSL*) info "rodando no WSL (ok: o professor usa Linux)" ;; esac
if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' 2>/dev/null; then
    ok "P2 Python $(python3 -c 'import platform; print(platform.python_version())')"
else
    falta "P2 Python 3.10 ou superior"
fi
if python3 -c 'import ensurepip' 2>/dev/null; then ok "P2 módulo venv completo"; else falta "P2 python3-venv (sudo apt install python3-venv)"; fi
if command -v make >/dev/null; then ok "P2 make"; else falta "P2 make (sudo apt install make)"; fi
gh_logado=0
if command -v gh >/dev/null; then
    if gh auth status >/dev/null 2>&1; then ok "P3 gh instalado e logado"; gh_logado=1; else falta "P3 gh sem login (gh auth login)"; fi
else
    falta "P3 gh não instalado (sudo apt install gh)"
fi
if [ -x .venv/bin/python ] && .venv/bin/python -c 'import surveyor, pytest' 2>/dev/null; then
    ok "P4 ambiente do projeto instalado (.venv)"
else
    falta "P4 ambiente do projeto (make instalar)"
fi

echo "== Repositório local"
git fetch --quiet --prune origin 2>/dev/null || info "sem acesso ao origin agora"
ramo="$(git branch --show-current)"
info "ramo atual: ${ramo}"
if [ -z "$(git status --porcelain)" ]; then ok "sem alterações pendentes"; else info "há alterações não commitadas neste ramo"; fi
if git ls-remote --exit-code --heads origin arquitetura-base >/dev/null 2>&1; then
    ok "M3 ramo arquitetura-base publicado no GitHub"
elif git rev-parse --verify --quiet origin/main:pyproject.toml >/dev/null; then
    ok "M3 base já está na main"
else
    falta "M3 base ainda não publicada (Matheus: commit + push + PR do ramo arquitetura-base)"
fi

echo "== GitHub (configuração da equipe)"
protegido="$(curl -fsS "https://api.github.com/repos/${REPO}/branches/main" 2>/dev/null \
    | grep -o '"protected": *[a-z]*' | grep -o '[a-z]*$')"
case "${protegido}" in
    true)  ok "V1 main protegida (PR + pipeline verde + aprovação)" ;;
    false) falta "V1 main SEM proteção: hoje qualquer push ou PR vermelho entra (Vitor)" ;;
    *)     info "não foi possível consultar a proteção da main" ;;
esac
if [ "${gh_logado}" -eq 1 ]; then
    gh api "repos/${REPO}" --jq '
        if (.allow_merge_commit == false and .allow_rebase_merge == false and .delete_branch_on_merge == true)
        then "  [ok]       V2 merge só por squash e ramo apagado após o merge"
        else "  [PENDENTE] V2 merges: squash=\(.allow_squash_merge) merge-commit=\(.allow_merge_commit) rebase=\(.allow_rebase_merge) apagar-ramo=\(.delete_branch_on_merge)"
        end' 2>/dev/null || info "V2 sem permissão para ler as configurações do repositório"
    login="$(gh api user --jq .login 2>/dev/null || true)"
    permissao="$(gh api "repos/${REPO}/collaborators/${login}/permission" --jq .permission 2>/dev/null || true)"
    case "${permissao}" in
        admin|maintain|write) ok "V1.1 ${login} tem permissão '${permissao}' no repositório" ;;
        "") info "V1.1 não foi possível ler a permissão de ${login:-?}" ;;
        *) falta "V1.1 ${login} só tem permissão '${permissao}': o dono precisa dar Write" ;;
    esac
    echo "== Pull Requests abertos"
    gh pr list --repo "${REPO}" --state open 2>/dev/null || true
else
    info "V2, V1.1 e PRs abertos: precisam do gh logado para serem conferidos"
fi
