---
name: desenvolver-demanda
description: Ponto de partida de QUALQUER mudança no UNIBRASIL Surveyor (código, testes, docs ou skills), no fluxo solo direto na main. Mostra onde o projeto está, implementa COM TESTES (com a skill implementar-etapa), verifica e faz um commit por micro passo na main. Não cria ramo, não abre PR e não faz push (o push é do Matheus). Use quando pedirem para fazer, continuar, corrigir ou ajustar algo, ou para seguir para o próximo passo.
---

# Desenvolver uma demanda (fluxo solo, direto na `main`)

Desde 2026-11-10 o Matheus faz o trabalho sozinho e decidiu trabalhar direto na `main`, sem ramos nem PR. **Respostas curtas:** o que foi feito, o resultado do `make verificar` e o próximo passo em uma linha.

## 1 — Situar
- [ ] 1.1 Leia a mensagem `[sincronizar-git]` do hook de início de sessão.
- [ ] 1.2 `git status`. Se houver alteração que não é desta demanda, **pare e pergunte**. Nunca descarte trabalho.
- [ ] 1.3 `.claude/skills/desenvolver-demanda/painel.sh`: etapas feitas e commits ainda não enviados.
- [ ] 1.4 Se o usuário não disse a demanda, siga a "Ordem das etapas (solo)" do `CLAUDE.md`.

## 2 — Implementar, sempre com teste
- [ ] 2.1 Siga a skill `implementar-etapa`, micro passo por micro passo: **o teste vem antes do código** e deve falhar pelo motivo certo.
- [ ] 2.2 Uma correção de bug começa por um teste que reproduz o bug.
- [ ] 2.3 Se o micro passo do roteiro pedir algo que seria código sem uso, não implemente. Registre o motivo no próprio item de `etapas.md` (exemplo: 4.4).

## 3 — Verificar e commitar (a cada micro passo)
- [ ] 3.1 `make verificar` verde. É o mesmo que o pipeline roda: ruff, mypy strict, todos os testes e cobertura ≥ 90%.
- [ ] 3.2 Revise o diff com `.claude/skills/implementar-etapa/armadilhas.md`.
- [ ] 3.3 Marque `[x]` no micro passo em `etapas.md`.
- [ ] 3.4 Commit na `main`:
  - `git add` pelo nome dos arquivos (código, teste e `etapas.md`), nunca `git add -A`;
  - o `resultados/cobertura.txt` gerado pelo `make verificar` não entra;
  - mensagem `Etapa N.M: <o que mudou>`, terminando com a linha de coautoria do Claude.

## 4 — Fim da etapa
- [ ] 4.1 Faça o fechamento da etapa (skill `implementar-etapa`, Passo 3).
- [ ] 4.2 Responda em poucas linhas: o que a etapa faz agora, os testes e a cobertura, quantos commits faltam enviar (o Matheus roda `git push origin main`) e qual é a próxima etapa.

## Pipeline do GitHub (`.github/workflows/ci.yml`)
Roda a cada push na `main`:
- **Lint e tipos:** `make lint` e `make tipos`.
- **Testes (Python 3.10 e 3.14):** `make cobertura`, com todos os testes e cobertura mínima de 90%.

Um teste novo entra sozinho no pipeline se estiver em `tests/` com nome `test_*.py`. O `pyproject.toml` (e, se preciso, o `ci.yml`) muda **no mesmo commit** quando a demanda traz uma dependência, um marcador do pytest ou uma versão mínima do Python nova.

Problema de git? Veja [git-socorro.md](git-socorro.md) antes de qualquer comando que possa perder trabalho.

## Proibido
- `push --force`, ou descartar alterações locais (`reset --hard`, `checkout -- .`, `clean`) sem pedido explícito.
- Mudar código sem teste, ou escrever teste que não falharia sem o código novo.
- Desligar, pular ou afrouxar um job do pipeline (ou o `fail_under`) para passar.
- `git add -A` às cegas.
