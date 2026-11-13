---
name: preparar-entrega
description: Monta e confere o ZIP de entrega do Trabalho 2 (UNIBRASIL Surveyor). Ele leva só o código-fonte e o necessário para o professor ler o README, instalar as dependências e rodar, mais os artefatos que o enunciado exige (plano de voo, evidências, cobertura, documentação). Nada de .venv, .git, .github, .claude, caches ou logs soltos. Use quando falarem em entrega, ZIP, empacotar, enviar ao professor, "o que vai no zip" ou na Etapa 12.
---

# Preparar a entrega

O professor vai abrir o ZIP, ler o README, criar o próprio ambiente (`python3 -m venv` + `pip install`) e rodar. Portanto o ZIP leva **só** o que serve para isso, mais o que o enunciado exige.

> **"Só o código" não significa tirar as evidências.** O enunciado exige o CSV do melhor plano, as evidências de execução, as evidências de cobertura e a documentação das coordenadas extras. Sem isso perde-se nota. Elas vão em `resultados/` e `docs/`.

## O que vai no ZIP (lista fechada)

| Caminho | Para quê |
|---|---|
| `README.md` | nome completo e matrícula de todos; como instalar e quais comandos geram o resultado entregue |
| `pyproject.toml` | dependências (`pip install`) e configuração de testes e cobertura |
| `src/` | código-fonte |
| `tests/` | testes unitários próprios (exigidos) |
| `dados/` | entradas: coordenadas do AVA, extras da equipe, vento |
| `docs/` | decisões, coordenadas extras (exigido), arquitetura, codificação genética, experimentos |
| `resultados/` | `plano_de_voo.csv` (exigido), `progresso.csv`, gráficos, mapa da rota, log e saída do validador da execução final, `cobertura.txt` (exigido) |

## O que NÃO vai

| Item | Por quê |
|---|---|
| `.venv/` | o professor instala o próprio ambiente pelo README |
| `.git/`, `.gitignore`, `.gitattributes` | controle de versão, não faz parte do programa |
| `.github/` (CI) | automação do repositório |
| `.claude/`, `CLAUDE.md` | ferramentas de desenvolvimento da equipe |
| `Makefile`, `.editorconfig` | atalhos e configuração de editor; o README usa comandos Python diretos |
| `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/`, `resultados/cobertura/` (HTML), `*.egg-info/`, `build/`, `dist/` | lixo gerado |
| `logs/` | logs de desenvolvimento; só o log da execução final vai, copiado para `resultados/` |
| `Trabalho 2.pdf`, outros `.zip` | não são parte da solução |

Isso é garantido por construção: `make entrega` usa `git archive` com a **lista fechada** acima, a partir do último commit da `main`. O `verificar_zip.sh` confere de novo.

## Painel

```
PASSO ATUAL: Entrega · Passo 3 de 6 (conferir documentos)
Micro passos:
  [x] 3.1 README: equipe e reprodução
  [>] 3.2 Coordenadas extras                   <- agora
  [ ] 3.3 Decisões confirmadas e erros do enunciado
  ...
PRÓXIMOS PASSOS: Passo 4 (gerar o ZIP) → Passo 5 (testar como o professor) → Passo 6 (enviar)
```

Os passos 1 a 3 mudam arquivos: faça-os direto na `main`, pela skill `desenvolver-demanda`. Os passos 4 a 6 também são na `main`, depois do `git push` do Matheus.

## Passo 1 — Pré-requisitos
- [ ] 1.1 Painel (`.claude/skills/desenvolver-demanda/painel.sh`): Etapas 0 a 11 concluídas e enviadas (`git push`).
- [ ] 1.2 Decisões confirmadas na seção 4 de `docs/decisoes.md` e refletidas no código (feito em 2026-11-12).
- [ ] 1.3 `make verificar` verde na `main` atualizada.

## Passo 2 — Evidências finais em `resultados/`
- [ ] 2.1 Execução final com a configuração escolhida nos experimentos e a semente fixada: `python -m surveyor --log-arquivo resultados/execucao.log otimizar --semente <S>`. Gera `plano_de_voo.csv` e `progresso.csv`.
- [ ] 2.2 `python -m surveyor validar > resultados/validacao.txt 2>&1`: deve terminar com "Plano válido".
- [ ] 2.3 Gráfico de convergência e mapa da rota (marcando os pousos) em `resultados/`.
- [ ] 2.4 `make cobertura`: atualiza `resultados/cobertura.txt`.
- [ ] 2.5 Conferir as ordens de grandeza (`etapas.md`, Etapa 10) e anotar no README: tempo total de voo, número de pousos, custo em R$ e dias usados.

## Passo 3 — Documentos
- [ ] 3.1 README:
  - nome completo e matrícula dos dois, conferidos com o cadastro;
  - instalação (inclusive `python3-venv` no Debian/Ubuntu);
  - **o comando exato que gerou o resultado entregue** (com a semente) e quanto tempo ele leva;
  - modo rápido para reprodução parcial;
  - como rodar os testes e a cobertura;
  - nenhuma menção a `make`.
- [ ] 3.2 `docs/coordenadas_extras.md` preenchido (saída de `python -m surveyor extras`).
- [ ] 3.3 `docs/decisoes.md`, `docs/codificacao.md` e `docs/experimentos.md` completos.
- [ ] 3.4 Nenhuma menção a regras "condicionais por matrícula" em lugar nenhum: `grep -rni "matr[ií]cula come" src tests docs README.md` deve voltar vazio.
- [ ] 3.5 Commits da entrega na `main` e enviados pelo Matheus (`git push`).

## Passo 4 — Gerar o ZIP (na `main` atualizada, sem alterações pendentes)
- [ ] 4.1 `git switch main && git pull --ff-only && git status` (limpo).
- [ ] 4.2 `make entrega`. Gera `../Trabalho2_SC_Drone_Delivery.zip` com a lista fechada e já roda o `verificar_zip.sh`.

## Passo 5 — Testar como o professor
- [ ] 5.1 O `verificar_zip.sh` passou nas 4 fases: conteúdo proibido, obrigatórios, instalação limpa, e testes + execução rápida + validação. Para rodar à mão: `.claude/skills/preparar-entrega/verificar_zip.sh ../Trabalho2_SC_Drone_Delivery.zip`.
- [ ] 5.2 Abrir o ZIP e ler o README como se fosse o professor: os comandos funcionam copiando e colando.

## Passo 6 — Enviar
- [ ] 6.1 **Um só integrante** envia o ZIP no AVA. Se os dois enviarem, o professor escolhe uma versão arbitrariamente.
- [ ] 6.2 Avisar o outro integrante que a entrega foi feita (data e hora).

## Checklist final (tudo precisa estar marcado antes do Passo 6)
- [ ] Nome completo e matrícula de todos no README e na documentação.
- [ ] CSV com 11 colunas, latitude antes de longitude, 13 casas, `HH:MM:SS`, `SIM`/`NÃO`, hífen ASCII.
- [ ] `validar` aprova o plano: bateria nunca zerada, nenhum pouso fora do horário ou numa extra, nenhum CEP repetido, campus no início e no fim, tudo até o dia 7.
- [ ] Evidências em `resultados/`: plano, progresso, gráfico, mapa, log, validação e cobertura.
- [ ] Documentação das extras com matrícula e distância em metros.
- [ ] ZIP sem nada da lista "NÃO vai" e aprovado pelo `verificar_zip.sh`.
- [ ] Nenhum arquivo nem teste compartilhado com outras equipes.
