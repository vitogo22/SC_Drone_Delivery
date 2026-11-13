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
Feito: Etapas 1, 3, 4 e 5; Etapa 2 até a 2.4 (224 testes, cobertura 100%). 12 commits ainda não enviados.
Próximo: 2.5 — comando `python -m surveyor extras` (no cronograma: até qui 12/11).
Prazo: ter 24/11.
Sigo?
```
- Um passo de cada vez. Não liste todas as etapas, nem tabelas ou pendências que não bloqueiam.
- Compare com o cronograma de [trabalho.md](../implementar-etapa/trabalho.md) e diga em meia linha se o projeto está em dia ou atrasado (prazo: 24/11/2026).
- Se algo depender do Matheus, abra com o bloco "⚠️ PRECISO DE VOCÊ" (ver `CLAUDE.md`).
- Explique termos novos em meia linha, ou aponte o [glossario.md](glossario.md).

## 3 — Encaminhar
| O passo é... | Skill |
|---|---|
| implementar ou continuar uma etapa | `desenvolver-demanda` (que usa a `implementar-etapa`) |
| empacotar e enviar o trabalho | `preparar-entrega` |

## Sem uso no fluxo solo
As filas de onboarding da dupla (V1–V3, M3–M4 em [onboarding.md](onboarding.md)), a proteção da `main` com aprovação obrigatória e a skill `revisar-pr` eram para o trabalho em dupla com PR. Não as proponha. A identidade do git (P1) também não importa: o Matheus disse que o e-mail dos commits é irrelevante para o professor.
