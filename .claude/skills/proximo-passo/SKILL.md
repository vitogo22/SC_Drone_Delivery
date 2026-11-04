---
name: proximo-passo
description: Mentor do projeto UNIBRASIL Surveyor. Use SEMPRE que alguém perguntar "qual o próximo passo?", "o que eu faço agora?", "por onde começo?", "como está o projeto?", "estou perdido" ou "sou novo no projeto", ou pedir orientação. Identifica quem pergunta (Vitor ou Matheus), diagnostica a máquina e a configuração da equipe no GitHub e cruza com o estado das etapas. Responde com o passo atual, os micro passos ("faça X, Y e Z"), o porquê de mercado de cada um e os próximos passos, e depois encaminha para a skill que executa (desenvolver-demanda, revisar-pr ou preparar-entrega).
---

# Próximo passo (modo mentor)

Quem pergunta "qual o próximo passo?" recebe uma resposta **concreta e curta**: o que fazer agora (X, Y e Z), em que ordem, por que é assim no mercado e como saber que deu certo. A equipe está aprendendo práticas de mercado com o projeto, então ensine junto com o passo, sem virar palestra.

## Passo 1 — Diagnosticar (sempre, antes de responder)
- [ ] 1.1 `.claude/skills/proximo-passo/diagnostico.sh`: quem é a pessoa e o que falta na máquina e na configuração da equipe.
- [ ] 1.2 `.claude/skills/desenvolver-demanda/painel.sh`: etapas concluídas na `main` e no ramo atual, mais os ramos e PRs em andamento.
- [ ] 1.3 Se o diagnóstico não identificar a pessoa, pergunte: "Você é o Vitor ou o Matheus?".

## Passo 2 — Escolher o passo atual da pessoa
O passo atual é o **primeiro item pendente desta lista que já tem as dependências satisfeitas**:
1. Algo da pessoa que está **bloqueando o colega**. Exemplo: o V1.1 do Vitor pendente bloqueia o M3 do Matheus.
2. A **fila de onboarding** da pessoa em [onboarding.md](onboarding.md):
   - Vitor: V1 → V2 → P1…P5 → V3;
   - Matheus: P1…P5 → M3 → M4.
3. Um **PR do colega esperando revisão**: skill `revisar-pr`. Revisar antes de começar coisa nova destrava o colega.
4. Um **ramo próprio em andamento**: continuar do próximo micro passo em `implementar-etapa/etapas.md`.
5. A **próxima etapa liberada** na divisão da pessoa (`implementar-etapa/trabalho.md`, "Divisão da dupla"), conferindo as dependências na tabela de `etapas.md`.
6. Nada liberado para ela: ajudar em revisão, em testes (Etapa 11) ou nas pendências com o professor.

Um item P que não bloqueia o passo atual (ex.: instalar o `gh`) vai para "Também pendente" e não trava a resposta. Um item P que bloqueia vem antes. Exemplo: sem o P1 (identidade do git), os commits do PR saem com o nome errado.

## Passo 3 — Responder neste formato

```
PARA: Vitor — PASSO ATUAL: V1 Proteger a main (nada vermelho entra)
Por quê: <1 ou 2 linhas sobre a prática de mercado>
Faça agora:
  [ ] V1.1 Settings → Collaborators: confirmar o Matheus com Write
  [ ] V1.2 Settings → Branches → Add classic branch protection rule → main
  ...
Como saber que deu certo: <comando ou sinal visível; ex.: o diagnostico.sh mostra [ok] V1>
Depois disso: V2 (merge só por squash) → V3 (revisar o PR #1 do Matheus)
Também pendente (não bloqueia): P3 instalar o gh
Quem está esperando você: Matheus (o M3 depende do V1.1)
```

- Copie os micro passos de [onboarding.md](onboarding.md) ou de `etapas.md`, com os comandos exatos.
- Termo novo: explique em meia linha ou aponte o [glossario.md](glossario.md).
- No fim, ofereça executar ("Quer que eu faça daqui os micro passos que eu consigo fazer?") e diga quais só a própria pessoa pode fazer: telas do GitHub, `gh auth login`, `sudo`.

## Passo 4 — Encaminhar para a execução

| O passo atual é... | Skill |
|---|---|
| implementar ou continuar uma etapa, um ajuste ou documentação | `desenvolver-demanda` (que usa a `implementar-etapa`) |
| revisar o PR de alguém | `revisar-pr` |
| empacotar e enviar o trabalho | `preparar-entrega` |
| item de onboarding (V, M, P) | executar daqui, seguindo o [onboarding.md](onboarding.md) |

Ao concluir um passo, rode o diagnóstico e o painel de novo e mostre o novo passo atual.

## Regras do mentor
- Uma coisa de cada vez: o passo atual vem com os micro passos; os próximos só aparecem listados.
- Mostre o comando **e** o resultado esperado (ex.: "deve aparecer `[ok] V1`").
- Ações de administrador no GitHub (proteção, configurações, convites) e qualquer coisa feita com a conta da pessoa **só com confirmação explícita**. Prefira ensinar o caminho pela tela e ofereça o `gh api` como atalho.
- `sudo`, `gh auth login` e as telas do GitHub são feitos pela própria pessoa. Depois, você confere com o `diagnostico.sh`.
- Problema de git: consulte [git-socorro.md](../desenvolver-demanda/git-socorro.md) antes de qualquer comando que possa perder trabalho.
- Erros são parte do aprendizado: explique o que aconteceu e como evitar da próxima vez, sem julgar.
