---
name: revisar-pr
description: Guia o code review de um Pull Request do UNIBRASIL Surveyor feito por um integrante no PR do outro. Cobre preparar a revisão, conferir o pipeline, rodar localmente, ler o diff com checklist, escrever comentários construtivos e decidir entre aprovar ou pedir mudanças, ensinando a prática de mercado. Também cobre o lado do autor (responder à revisão). Use quando pedirem para revisar um PR, "review", "aprovar o PR", "o PR #N está bom?", ou quando o próximo passo for revisar.
---

# Revisar um Pull Request (code review)

**Por quê (mercado):** nenhum código entra na `main` sem que outra pessoa o leia. A revisão pega erro cedo e espalha o conhecimento do código pela equipe. A proteção da `main` exige 1 aprovação, então o PR do colega fica parado até você revisar.

**Quem faz o quê:** o Claude lê o diff, roda as verificações e **propõe** os comentários. Quem decide, comenta, aprova e clica em merge é o revisor humano. O Claude só envia comentários pelo `gh` se o revisor pedir explicitamente.

## Painel

```
PASSO ATUAL: Revisão do PR #4 (Etapa 3 — Geodésia, do Matheus) · Passo 4 de 7 (ler o diff)
Micro passos:
  [x] 4.1 Escopo
  [>] 4.2 Testes cobrem os oráculos            <- agora
  [ ] 4.3 Contrato e armadilhas
  ...
PRÓXIMOS PASSOS: Passo 5 (comentar) → Passo 6 (decidir) → Passo 7 (merge)
```

## Passo 1 — Preparar
- [ ] 1.1 `gh pr list` e `gh pr view <N>`: ler o título, a descrição e os micro passos que o autor diz ter feito. Sem o `gh`: aba "Pull requests" no GitHub.
- [ ] 1.2 Abrir a seção da etapa em `.claude/skills/implementar-etapa/etapas.md`: o que **deveria** ter sido feito e os oráculos.
- [ ] 1.3 Trazer o código para a máquina:
  - com o `gh`: `gh pr checkout <N>`;
  - sem o `gh`: `git fetch origin <ramo> && git switch <ramo>`.

## Passo 2 — Pipeline
- [ ] 2.1 `gh pr checks <N>` (ou a aba Checks): os 4 checks verdes (Lint e tipos, Testes 3.10, Testes 3.14, PR traz testes).
- [ ] 2.2 Algum vermelho? Pare a revisão, comente "**bloqueante:** o check X falhou em <passo>", peça a correção e volte depois.

## Passo 3 — Rodar localmente
- [ ] 3.1 `make verificar` verde.
- [ ] 3.2 Se o PR traz um comando ou comportamento visível, execute-o (ex.: `python -m surveyor extras`) e confira o resultado com o que diz a etapa.

## Passo 4 — Ler o diff (`gh pr diff <N>` ou a aba "Files changed")
- [ ] 4.1 **Escopo:** só o que a etapa pede. Nada de arquivo alheio reformatado nem "aproveitei e mudei".
- [ ] 4.2 **Testes:**
  - cada comportamento tem teste, com os oráculos de `etapas.md`;
  - o teste **falharia sem o código**. Para provar, comente a linha principal do código, rode `make testar`, veja falhar e desfaça.
- [ ] 4.3 **Contrato:** os valores e as regras batem com `docs/decisoes.md`. Nenhuma regra nova sem um `A<n>` registrado.
- [ ] 4.4 **Armadilhas:** passar o diff por `.claude/skills/implementar-etapa/armadilhas.md`, item por item.
- [ ] 4.5 **Clareza:**
  - nomes descritivos com unidade (`_km`, `_s`);
  - docstring real, sem "API prevista";
  - função curta, com uma responsabilidade;
  - sem código morto.
- [ ] 4.6 **Camadas:** os imports respeitam `docs/arquitetura.md`. O `tests/test_arquitetura.py` pega o grosso, mas confira a intenção.

## Passo 5 — Comentar
- [ ] 5.1 Um comentário por assunto, **na linha** do problema (aba "Files changed", botão `+`).
- [ ] 5.2 Começar com um prefixo que diz o peso:
  - **bloqueante:** impede a aprovação (bug, regra errada, falta de teste);
  - **sugestão:** melhoria opcional;
  - **dúvida:** pergunta, sem acusação;
  - **elogio:** reconhecer o que ficou bom também é prática de mercado.
- [ ] 5.3 Formato: **o quê** + **por quê** + **proposta**. Exemplo:
  > **bloqueante:** `tempo_trecho_s` usa `round`. O contrato (`docs/decisoes.md`, seção 1: "arredondado para cima") e a Etapa 5.3 pedem teto: 120,4 s precisa virar 121, mas `round` dá 120. Proposta: `math.ceil(x - 1e-9)` e um teste com 120,4.
- [ ] 5.4 Critique o código, nunca a pessoa ("este trecho faz…", e não "você errou…").

## Passo 6 — Decidir
- [ ] 6.1 Há algum **bloqueante**? Então **Request changes**. Senão, **Approve** (as sugestões podem virar outro PR).
  - pela tela: "Files changed" → **Review changes**;
  - pelo terminal, o próprio revisor roda: `gh pr review <N> --approve` ou `--request-changes --body "<resumo>"`.
- [ ] 6.2 No resumo da revisão: o que foi conferido, os bloqueantes (se houver) e um elogio sincero.

## Passo 7 — Merge (humano)
- [ ] 7.1 Com aprovação e os 4 checks verdes: **Squash and merge**, mantendo o título do PR como mensagem.
- [ ] 7.2 Avise o autor. Ele segue o Passo 8 da skill `desenvolver-demanda` (atualizar a `main` e apagar o ramo).
- [ ] 7.3 Na sua máquina: `git switch main && git pull --ff-only`.

## Quando você é o autor e recebeu a revisão
- [ ] A.1 Leia todos os comentários antes de mudar qualquer coisa.
- [ ] A.2 Cada **bloqueante** vira um commit no **mesmo ramo** (`Etapa 3.2: corrige arredondamento para teto (revisão)`), com teste. Depois, push.
- [ ] A.3 Responda cada comentário ("feito em <commit>" ou o porquê de discordar) e marque como resolvido. A proteção exige todas as conversas resolvidas.
- [ ] A.4 Peça uma nova revisão (botão "Re-request review"). Novos commits invalidam a aprovação anterior.
