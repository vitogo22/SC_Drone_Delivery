---
name: desenvolver-demanda
description: Ponto de partida de QUALQUER mudança no UNIBRASIL Surveyor (código, testes, docs ou skills). Sincroniza com o GitHub, mostra o painel do projeto (passo atual, micro passos e próximos passos), cria um ramo próprio para a demanda, implementa COM TESTES (com a skill implementar-etapa), verifica, abre o Pull Request, acompanha o pipeline do GitHub e PARA, porque o merge na main é feito pela equipe. Use quando pedirem para fazer, continuar, corrigir ou ajustar algo, abrir PR ou retomar um ramo. Para "qual o próximo passo?", use antes a skill proximo-passo.
---

# Desenvolver uma demanda: ramo → testes → PR → pipeline verde → merge pela equipe

**Regras de ouro:**
1. Nunca commitar nem fazer push na `main`. Cada demanda vive no seu próprio ramo e só entra na `main` por Pull Request, revisado e mergeado por um integrante da equipe. Isso evita conflitos quando os dois trabalham ao mesmo tempo, e a revisão do PR é o peer-review que o enunciado recomenda.
2. **Toda feature, correção ou ramo novo que mexe em código vem com teste**, e esse teste roda no pipeline do GitHub (ver "Testes e pipeline" abaixo). O pipeline reprova o PR que muda `src/` sem mudar `tests/`.

## Painel (mostrar no início, a cada passo concluído e no fim)

Rode `.claude/skills/desenvolver-demanda/painel.sh` (etapas concluídas na `main`, no ramo atual e ramos em andamento) e responda neste formato:

```
PASSO ATUAL: Etapa 3 — Geodésia · ramo etapa-03-geo · fluxo: Passo 4 de 8 (implementar)
Micro passos da etapa:
  [x] 3.1 Testes de distancia_km
  [>] 3.2 Implementar Haversine          <- agora
  [ ] 3.3 Testes de rumo_graus
  ...
PRÓXIMOS PASSOS: terminar a 3 → PR · liberadas depois: Etapa 4 (Vento), Etapa 5 (Bateria e custo)
EM ANDAMENTO / PENDÊNCIAS: ramo etapa-01-dados (Vitor) · PR #4 aguardando revisão · perguntas ao professor (0.8)
```

- **Próximos passos** = etapas cujas dependências (tabela de `etapas.md`) já estão concluídas na `main` e que não têm ramo nem PR em andamento.
- Os micro passos de cada etapa estão em `.claude/skills/implementar-etapa/etapas.md`.

## Fluxo em 8 passos

### Passo 1 — Sincronizar
- [ ] 1.1 O hook de início de sessão (`.claude/hooks/sincronizar-git.sh`) já fez `git fetch` e `git pull --ff-only`: leia a mensagem `[sincronizar-git]`. Se ela não apareceu, rode o script à mão.
- [ ] 1.2 `git status`: se houver alteração não commitada que não pertence a esta demanda, **pare e pergunte** ao usuário. Nunca descarte o trabalho de ninguém.
- [ ] 1.3 Para uma demanda nova: `git switch main && git pull --ff-only`.

### Passo 2 — Escolher a demanda
- [ ] 2.1 Rodar o painel e mostrar o estado.
- [ ] 2.2 Se o usuário não disse qual demanda, propor a próxima liberada e confirmar com ele.
- [ ] 2.3 Uma demanda por ramo e por PR: uma etapa ou um ajuste pequeno, nunca várias etapas juntas.

### Passo 3 — Criar o ramo
- [ ] 3.1 Nome em minúsculas e sem acento:
  - etapa: `etapa-NN-tema` (ex.: `etapa-03-geo`);
  - fora das etapas: `ajuste-<tema>`, `docs-<tema>` ou `correcao-<tema>`.
- [ ] 3.2 Demanda nova: `git switch -c <ramo>` a partir da `main` atualizada.
- [ ] 3.3 Retomando um ramo: `git switch <ramo> && git pull --ff-only`.

### Passo 4 — Implementar (sempre com teste)
- [ ] 4.1 Seguir a skill `implementar-etapa`, micro passo por micro passo: **o teste vem antes do código**.
- [ ] 4.2 Cada comportamento novo ou corrigido ganha um teste em `tests/`. Correção de bug começa por um teste que reproduz o bug.
- [ ] 4.3 Um commit por micro passo concluído, **com o código e o teste no mesmo commit**:
  - adicione os arquivos pelo nome (`git add src/... tests/...`), nunca `git add -A` às cegas;
  - mensagem no formato `Etapa 3.2: implementa distancia_km (Haversine)`.
- [ ] 4.4 Marcar `[x]` no micro passo em `etapas.md`, **só na seção da própria etapa**. As outras seções pertencem a outros ramos, e mexer nelas gera conflito.

### Passo 5 — Verificar (local e pipeline)
- [ ] 5.1 `make verificar` verde: é o mesmo que o pipeline roda (ruff, mypy strict, todos os testes, cobertura ≥ 90%).
- [ ] 5.2 `.github/scripts/exige-testes.sh origin/main HEAD`: confere localmente a mesma regra do job "PR traz testes".
- [ ] 5.3 Os testes novos entram no pipeline? Veja "Testes e pipeline" abaixo. Se a demanda trouxe algo que o pipeline ainda não conhece, atualize `.github/workflows/ci.yml` **neste mesmo PR**.
- [ ] 5.4 Revisar o diff com `.claude/skills/implementar-etapa/armadilhas.md`.
- [ ] 5.5 `git diff origin/main --stat`: só os arquivos da demanda. Não reformate nem renomeie arquivos alheios no mesmo PR.

### Passo 6 — Atualizar com a main
- [ ] 6.1 `git fetch origin && git rebase origin/main`.
- [ ] 6.2 Se houver conflito, mantenha as duas mudanças. Na dúvida, pergunte. Depois, `make verificar` de novo.

### Passo 7 — Abrir o Pull Request
- [ ] 7.1 Push:
  - primeira vez: `git push -u origin <ramo>`;
  - depois de um rebase: `git push --force-with-lease`, e só no próprio ramo.
- [ ] 7.2 Criar o PR:
  - com o `gh` instalado e logado: `gh pr create --base main --head <ramo> --title "<título>" --body-file <arquivo>`;
  - sem o `gh`: entregue ao usuário o link `https://github.com/vitogo22/SC_Drone_Delivery/compare/main...<ramo>?expand=1` junto com o título e o corpo prontos. Para instalar o `gh`, o próprio usuário roda `sudo apt install gh` e `gh auth login` (é interativo).
- [ ] 7.3 Corpo do PR no modelo abaixo.
- [ ] 7.4 Acompanhar o pipeline. Os 4 checks precisam ficar verdes: **Lint e tipos**, **Testes (Python 3.10)**, **Testes (Python 3.14)** e **PR traz testes**.
  - com o `gh`: `gh pr checks <número> --watch`;
  - sem o `gh`: aba **Checks** do PR no GitHub.

  Se algum falhar, corrija **no ramo** (novo commit e push) e volte ao Passo 5. Nunca desligue, pule nem afrouxe um passo do pipeline para passar.
- [ ] 7.5 **Pare aqui.** Não faça merge. Avise que o PR está esperando a revisão do outro integrante (merge só com o pipeline verde) e mostre o painel.
- [ ] 7.6 Quando a revisão chegar: siga "Quando você é o autor e recebeu a revisão" da skill `revisar-pr` (corrigir no mesmo ramo, responder cada comentário, pedir nova revisão).

### Passo 8 — Depois que a equipe mergear
- [ ] 8.1 `git switch main && git pull --ff-only`.
- [ ] 8.2 `git branch -d <ramo>`. Se o GitHub não apagou o ramo remoto, também `git push origin --delete <ramo>`.
- [ ] 8.3 Mostrar o painel com o próximo passo.

## Modelo de corpo do PR

```markdown
## Etapa N — <título>

**O que muda:** <1 a 3 frases>

**Micro passos concluídos:** N.1, N.2, … (marcados em etapas.md)

**Testes novos:** `tests/unidade/...` (o que cada um garante, em uma linha)

**Como testar:** `make verificar` (cobertura: XX%). O pipeline roda o mesmo.

**Pipeline:** <mudou o ci.yml? por quê> (ou "sem mudança: os testes novos são descobertos automaticamente")

**Decisões do contrato envolvidas:** A# … (ou "nenhuma")

**Checklist do revisor**
- [ ] Pipeline verde (Lint e tipos, Testes 3.10, Testes 3.14, PR traz testes)
- [ ] Os testes cobrem os oráculos da etapa e falhariam sem o código novo
- [ ] Nenhum item de armadilhas.md
- [ ] Nada fora do escopo da etapa
```

## Testes e pipeline do GitHub (`.github/workflows/ci.yml`)

O pipeline roda em todo PR e em todo push na `main`:

| Job | O que garante |
|---|---|
| Lint e tipos | `make lint` (ruff) e `make tipos` (mypy strict no código e nos testes) |
| Testes (Python 3.10 e 3.14) | `make cobertura`: **todos** os testes (unidade, integração, arquitetura e os marcados `lento`), com cobertura mínima de 90%. O resumo da cobertura aparece na página da execução e o relatório fica como artefato |
| PR traz testes | `.github/scripts/exige-testes.sh`: reprova o PR que muda `.py` em `src/` sem mudar nenhum `.py` em `tests/` |

**Como um teste novo entra no pipeline:**
1. Ele é descoberto automaticamente se estiver em `tests/` com nome `test_*.py` e funções `test_*`, no lugar que espelha o módulo (`tests/unidade/...` ou `tests/integracao/...`). Na maioria dos PRs, não é preciso mexer no `ci.yml`.
2. O `ci.yml` precisa mudar **no mesmo PR** quando a demanda traz algo que o pipeline ainda não tem:
   - dependência nova: vai no `pyproject.toml`, que o pipeline instala com `pip install -e ".[dev]"`;
   - marcador novo do pytest: registrar em `[tool.pytest.ini_options]`;
   - arquivo de dados novo usado nos testes: precisa estar commitado;
   - comando novo da CLI: precisa de teste de integração em `tests/integracao/`;
   - nova versão mínima do Python: ajustar a matriz.
3. É proibido `skip`/`xfail` sem motivo escrito no próprio marcador, `# pragma: no cover` para fugir da cobertura, ou desligar e afrouxar um job.

**Configuração única no GitHub:** a proteção da `main` (PR obrigatório, 1 aprovação, os 4 checks verdes, regra valendo também para o dono) é o item **V1** de `.claude/skills/proximo-passo/onboarding.md`, feito pelo Vitor, que é o dono do repositório. Com ela, nem um humano consegue mergear um PR vermelho ou sem teste. Confira com `.claude/skills/proximo-passo/diagnostico.sh`.

**Deu problema de git** (commit no ramo errado, conflito, pipeline vermelho, ramo desatualizado)? Veja [git-socorro.md](git-socorro.md) antes de qualquer comando que possa perder trabalho.

## Atalhos do Makefile (só para desenvolvimento; não vão no ZIP)

| Comando | O que faz |
|---|---|
| `make testar` | testes rápidos |
| `make verificar` | lint, tipos, testes e cobertura; obrigatório antes do PR |
| `make formatar` | formata o código e corrige o que o ruff souber corrigir |
| `make cobertura` | relatório em `resultados/cobertura.txt` |
| `make rapido` | roda o GA no modo rápido |
| `make entrega` | ZIP de entrega (skill `preparar-entrega`) |

## Proibido
- Commit ou push na `main`, e `push --force` em qualquer ramo compartilhado.
- O Claude fazer merge de PR. O merge é da equipe, e só com o pipeline verde.
- PR que muda código sem teste, ou teste que não falharia sem o código novo.
- Desligar, pular ou afrouxar um job do pipeline (ou o `fail_under`) para o PR passar.
- `git add -A` misturando arquivos de outras demandas.
- Editar a seção de outra etapa no `etapas.md`.
- Descartar alterações locais (`git reset --hard`, `git checkout -- .`, `git clean`) sem pedido explícito do usuário.
