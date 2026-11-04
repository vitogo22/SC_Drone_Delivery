# Onboarding: configuração única da equipe e de cada máquina

Itens feitos **uma vez só**. Antes das etapas do projeto, cada pessoa segue a **sua fila**, na ordem. O `diagnostico.sh` confere sozinho os itens marcados com (auto). Os demais, pergunte à pessoa.

## Filas por pessoa (ordem de execução)

| Pessoa | Fila | Depois da fila |
|---|---|---|
| **Vitor** (dono do repositório) | **V1 → V2** → P1…P5 → V3 | etapas da divisão em `implementar-etapa/trabalho.md` |
| **Matheus** | P1…P5 → **M3** → M4 | etapas da divisão em `implementar-etapa/trabalho.md` |

Dependências entre as filas:
- V1.1 (o Matheus ter permissão de escrita) libera o M3 (abrir o PR #1).
- O M3 faz o pipeline rodar pela primeira vez, o que permite completar o V1.4 pela tela.
- O V1 e o M3 juntos liberam o V3 (revisar e mergear o PR #1).

---

## V1 — Proteger a `main`: nada vermelho entra (Vitor) (auto)

**Por quê (mercado):** em empresa, ninguém sobe código direto na branch principal. Tudo passa por Pull Request, com pipeline verde e aprovação de outra pessoa. A regra fica no GitHub, então não depende da boa vontade de ninguém, nem do dono.

- [ ] V1.1 Settings → **Collaborators** → confirmar que o Matheus está lá com papel **Write**. Se não estiver, use "Add people" e espere ele aceitar o convite (e-mail ou sino do GitHub).
- [ ] V1.2 Settings → **Branches** → **Add classic branch protection rule** → Branch name pattern: `main`.
- [ ] V1.3 Marcar **Require a pull request before merging**, com **Require approvals: 1** e **Dismiss stale pull request approvals when new commits are pushed**.
- [ ] V1.4 Marcar **Require status checks to pass before merging** e **Require branches to be up to date before merging**. Na busca, adicionar os 4 checks: `Lint e tipos`, `Testes (Python 3.10)`, `Testes (Python 3.14)` e `PR traz testes`.
  - Se a busca não achar os checks, é porque o pipeline ainda não rodou nenhuma vez (isso acontece quando o PR #1 do Matheus é aberto). Salve a regra sem eles e volte aqui depois.
  - Outra saída: a via `gh api` abaixo, que cadastra os checks pelo nome.
- [ ] V1.5 Marcar **Require conversation resolution before merging**.
- [ ] V1.6 Marcar **Do not allow bypassing the above settings**. A regra vale também para o dono.
- [ ] V1.7 **Create/Save changes**. Para conferir: rode o `diagnostico.sh` (deve mostrar `[ok] V1`) ou abra o PR, onde o botão de merge fica bloqueado até os checks e a aprovação.

**Via `gh api`** (alternativa ao V1.2–V1.7). O Claude só executa com confirmação explícita do Vitor e com o `gh` logado na conta dele:

```bash
gh api -X PUT repos/vitogo22/SC_Drone_Delivery/branches/main/protection \
  -H "Accept: application/vnd.github+json" --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "Lint e tipos"},
      {"context": "Testes (Python 3.10)"},
      {"context": "Testes (Python 3.14)"},
      {"context": "PR traz testes"}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 1, "dismiss_stale_reviews": true},
  "required_conversation_resolution": true,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```

> Com 1 aprovação obrigatória e a regra valendo para o dono, cada um precisa da aprovação do outro para mergear: o PR do Vitor é aprovado pelo Matheus e vice-versa. Isso é o peer-review que o enunciado recomenda.

## V2 — Merge só por squash e ramo apagado depois do merge (Vitor) (auto com gh)

**Por quê (mercado):** "squash and merge" transforma cada PR em **um** commit na `main`, então o histórico fica legível (um commit por demanda). Apagar o ramo depois do merge evita ramos velhos acumulados.

- [ ] V2.1 Settings → **General** → seção **Pull Requests**: deixar marcado só **Allow squash merging**. Desmarcar "Allow merge commits" e "Allow rebase merging".
- [ ] V2.2 Na mesma seção, marcar **Automatically delete head branches**.
- [ ] V2.3 Alternativa pelo terminal (com confirmação): `gh api -X PATCH repos/vitogo22/SC_Drone_Delivery -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false -F delete_branch_on_merge=true`.

## V3 — Revisar, aprovar e mergear o PR #1 da base (Vitor)

**Por quê (mercado):** o primeiro code review do time. Quem revisa garante qualidade e aprende o código que vai usar.

- [ ] V3.1 Seguir a skill `revisar-pr` no PR #1 (`arquitetura-base`).
- [ ] V3.2 Aprovar e clicar **Squash and merge**.
- [ ] V3.3 Na máquina dele: `git switch main && git pull --ff-only`.

## M3 — Publicar a base: PR #1 (Matheus) (auto)

É o micro passo 0.7 de `etapas.md`. **Depende de:** V1.1 (permissão de escrita).

- [ ] M3.1 Seguir a skill `desenvolver-demanda` a partir do Passo 4.3, no ramo `arquitetura-base`: commits organizados por assunto (estrutura e ferramentas, domínio, logs, testes, docs, skills).
- [ ] M3.2 Push e PR com o título "Etapa 0: base do projeto (arquitetura, ferramentas, pipeline e skills)".
- [ ] M3.3 Acompanhar o pipeline até os 4 checks ficarem verdes e pedir a revisão do Vitor.

## M4 — Perguntas ao professor (Matheus, ou quem tiver o canal com ele)

- [ ] M4.1 Enviar a mensagem pronta de `implementar-etapa/trabalho.md` (micro passo 0.8) e descobrir o prazo.
- [ ] M4.2 Quando ele responder: ramo `docs-respostas-professor` e seção 4 de `docs/decisoes.md` (micro passo 0.9).

---

## Itens pessoais (cada um, na própria máquina)

### P1 — Identidade do git (auto)
**Por quê:** cada commit é assinado com nome e e-mail. Com o e-mail da conta, o commit aparece no seu perfil do GitHub e a equipe sabe quem fez o quê.
- [ ] P1.1 `git config --global user.name "Nome Completo"`.
- [ ] P1.2 `git config --global user.email "<e-mail da conta GitHub>"`. Para não expor o e-mail, use o endereço "noreply" que aparece em GitHub → Settings → Emails (formato `ID+usuario@users.noreply.github.com`).
- [ ] P1.3 Conferir com `git config user.name` e `git config user.email`.

### P2 — Sistema e Python (auto)
**Por quê:** o professor roda em Linux. Desenvolvendo no mesmo ambiente, não tem surpresa.
- [ ] P2.1 Linux, ou **WSL2 com Ubuntu** se usar Windows. O `Makefile`, os scripts e o hook do Claude são em bash.
- [ ] P2.2 Python 3.10 ou superior: `python3 --version`.
- [ ] P2.3 `sudo apt install python3-venv make`.

### P3 — GitHub CLI (auto)
**Por quê:** abrir PR, ver o pipeline e revisar pelo terminal. O Claude também usa o `gh` para isso.
- [ ] P3.1 `sudo apt install gh`.
- [ ] P3.2 `gh auth login` → GitHub.com → HTTPS → login pelo navegador. É interativo: a própria pessoa faz.
- [ ] P3.3 Conferir com `gh auth status`.

### P4 — Projeto instalado (auto)
**Por quê:** todos rodam exatamente o mesmo ambiente, e acaba o "na minha máquina funciona".
- [ ] P4.1 Clonar, se ainda não tiver: `git clone https://github.com/vitogo22/SC_Drone_Delivery.git`.
- [ ] P4.2 `make instalar` e depois `make verificar`, que deve ficar verde.

### P5 — Claude Code na pasta certa
**Por quê:** as skills, o `CLAUDE.md` e o hook do `git pull` só carregam com o Claude aberto **dentro** de `SC_Drone_Delivery/`.
- [ ] P5.1 `cd SC_Drone_Delivery && claude` (ou abrir essa pasta no VS Code).
- [ ] P5.2 Na primeira vez, aprovar o hook do projeto quando o Claude Code pedir. Depois, conferir em `/hooks`.
