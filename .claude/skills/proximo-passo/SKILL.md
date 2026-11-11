---
name: proximo-passo
description: Orienta o próximo passo do UNIBRASIL Surveyor no fluxo solo (Matheus, direto na main). Use SEMPRE que perguntarem "qual o próximo passo?", "o que eu faço agora?", "por onde começo?", "como está o projeto?" ou "estou perdido". Mostra em poucas linhas onde o projeto está e qual é o próximo passo, e depois encaminha para a skill que executa (desenvolver-demanda ou preparar-entrega).
---

# Próximo passo (fluxo solo)

O Matheus faz o trabalho sozinho desde 2026-11-10, direto na `main`. Ele pediu **respostas curtas**: na última sessão, uma resposta longa o deixou confuso.

## 1 — Situar
- [ ] 1.1 Rode `.claude/skills/desenvolver-demanda/painel.sh`.
- [ ] 1.2 O próximo passo é a primeira etapa não concluída na "Ordem das etapas (solo)" do `CLAUDE.md`, a partir do próximo micro passo que o painel mostra.

## 2 — Responder (no máximo uns 8 linhas)
```
Feito: Etapas 1, 3 e 4 (179 testes, cobertura 100%). 14 commits ainda não enviados.
Próximo: Etapa 5 — Bateria, tempo e custo (5.1 autonomia_s pela velocidade ajustada).
Pendente com você: 0.8 perguntar ao professor o prazo (mensagem pronta em trabalho.md).
Sigo?
```
- Um passo de cada vez. Não liste todas as etapas, nem tabelas ou pendências que não bloqueiam.
- Mencione o 0.8 (prazo com o professor) enquanto ele não estiver feito, porque o prazo é desconhecido.
- Explique termos novos em meia linha, ou aponte o [glossario.md](glossario.md).

## 3 — Encaminhar
| O passo é... | Skill |
|---|---|
| implementar ou continuar uma etapa | `desenvolver-demanda` (que usa a `implementar-etapa`) |
| empacotar e enviar o trabalho | `preparar-entrega` |

## Sem uso no fluxo solo
As filas de onboarding da dupla (V1–V3, M3–M4 em [onboarding.md](onboarding.md)), a proteção da `main` com aprovação obrigatória e a skill `revisar-pr` eram para o trabalho em dupla com PR. Não as proponha. A identidade do git (P1) também não importa: o Matheus disse que o e-mail dos commits é irrelevante para o professor.
