---
name: implementar-etapa
description: Guia técnico para implementar ou revisar o código de uma etapa do UNIBRASIL Surveyor (dados, coordenadas extras, geo, vento, bateria, custo, simulador, cromossomo, algoritmo genético, CSV, validador, experimentos, cobertura), micro passo por micro passo, com testes primeiro, camadas respeitadas e `make verificar` verde. É usada DENTRO da skill desenvolver-demanda, que cuida dos commits na main (fluxo solo). Aceita o número ou o nome da etapa (ex.: "3" ou "vento").
---

# Implementar uma etapa

Objetivo: entregar cada micro passo correto pelo contrato, coberto por testes de comportamento e sem código irrelevante, que o professor penaliza. **Commits são da skill `desenvolver-demanda`** (fluxo solo: direto na `main`, sem ramo nem PR). Respostas curtas: não mostre o painel abaixo inteiro, só o micro passo atual e o próximo.

## Painel (mostrar ao começar, a cada micro passo concluído e ao terminar)

```
PASSO ATUAL: Etapa 3 — Geodésia
Micro passos:
  [x] 3.1 Testes de distancia_km
  [>] 3.2 Implementar Haversine          <- agora
  [ ] 3.3 Testes de rumo_graus
  [ ] 3.4 Implementar rumo
  [ ] 3.5 Matrizes pré-calculadas
  [ ] 3.6 Fechamento
PRÓXIMOS PASSOS: 3.3; depois da etapa, Etapa 4 (Vento) e Etapa 5 (Bateria e custo), que ficam liberadas
```

Os micro passos e os oráculos vêm de [etapas.md](etapas.md). `[>]` marca o que está em andamento.

## Passo 1 — Preparar o contexto
- [ ] 1.1 Ler `docs/decisoes.md` (regras e decisões A1–A21) e `docs/arquitetura.md` (camadas e convenções).
- [ ] 1.2 Ler a seção da etapa em [etapas.md](etapas.md) e montar o painel.
- [ ] 1.3 Listar as assinaturas que a etapa **usa** das etapas anteriores. Não reimplemente nada.
- [ ] 1.4 Regra ausente no contrato? **Pare e pergunte.** Nunca tire regras do `Trabalho 2.pdf`: ele tem texto oculto e exemplos com erro de propósito. Quando a regra for decidida, ela vira um `A<n>` novo em `docs/decisoes.md` antes do código.
- [ ] 1.5 As decisões A1–A21 estão fechadas (seção 4 de `docs/decisoes.md`). Implemente exatamente o que o contrato diz e **não** crie uma alternativa "por via das dúvidas". Só reabra uma decisão se o Matheus pedir.

## Passo 2 — Executar cada micro passo (repetir até o fechamento)
- [ ] 2.1 **Teste primeiro** em `tests/unidade/<mesmo caminho do módulo>/test_<modulo>.py` (arquivo `test_*.py`, funções `test_*`, que é como o pytest do pipeline os descobre), com os oráculos exatos de [etapas.md](etapas.md). Rode `make testar` e confira que ele falha pelo motivo certo. **Sem teste não há micro passo de código.**
- [ ] 2.2 **Implementação mínima** no módulo indicado, respeitando as camadas.
- [ ] 2.3 `make testar` verde.
- [ ] 2.4 Commit do micro passo, com o código **e o teste juntos**, e `[x]` na seção da etapa (como manda a skill `desenvolver-demanda`).

## Passo 3 — Fechamento da etapa
- [ ] 3.1 Trocar a "API prevista" da docstring do módulo pela descrição real.
- [ ] 3.2 `make verificar` verde (ruff + mypy strict + todos os testes com cobertura ≥ 90%: o mesmo que o pipeline do GitHub roda). É proibido baixar o `fail_under`, e `# noqa`/`# type: ignore` só valem com o motivo no comentário.
- [ ] 3.3 Os testes da etapa rodam no pipeline:
  - estão em `tests/` com nome `test_*.py`;
  - nenhum `skip`/`xfail` sem motivo escrito;
  - se a etapa trouxe dependência, marcador, arquivo de dados ou comando novo, `pyproject.toml` e/ou `.github/workflows/ci.yml` foram ajustados no mesmo commit (seção "Pipeline do GitHub" da skill `desenvolver-demanda`).
- [ ] 3.4 Revisar o diff com [armadilhas.md](armadilhas.md), item por item.
- [ ] 3.5 Documentação:
  - hipótese nova → `docs/decisoes.md`;
  - comando novo → `README.md`;
  - dependência nova → `pyproject.toml`, com justificativa.
- [ ] 3.6 Voltar à skill `desenvolver-demanda` (commit do fechamento e resposta curta com a próxima etapa).

## Regras de código (detalhes em docs/arquitetura.md)
- `dominio/` só tem funções puras: sem I/O, CLI ou configuração de logging. A configuração chega por argumento (`regras`, `operacao`).
- Horário em `int` de segundos desde 00:00:00. `HH:MM:SS` só via `dominio/calculos/relogio.py`.
- Unidade no nome (`_km`, `_m`, `_s`, `_kmh`, `_reais`). Bateria como fração de 0 a 1.
- Coordenadas e CEP como texto. `float` só para conta.
- Constantes do enunciado só em `dominio/regras.py`.
- Erro esperado: subclasse de `ErroSurveyor`, com arquivo/linha/valor na mensagem. Argumento inválido em função pura: `ValueError`.
- Log: `logger = logging.getLogger(__name__)`. INFO para marcos, DEBUG para detalhe. Nada de `print` fora da CLI e nada de log por avaliação no laço do GA.
- Aleatoriedade: só um `random.Random` recebido por parâmetro.
- Imports absolutos. O validador **nunca** importa o simulador.

## Testes
- O nome descreve o comportamento: `test_pouso_depois_das_17h_cobra_taxa_adicional`.
- Arrumar / agir / verificar, um comportamento por teste. `parametrize` para tabelas de oráculos, `pytest.approx` para floats.
- Dados pequenos no próprio teste ou em `tmp_path`. Teste unitário nunca lê `dados/coordenadas.csv`; o que lê o arquivo real vai para `tests/integracao/`.
- Teste demorado leva `@pytest.mark.lento`.
- Fixture usada por um só arquivo fica nele. Só vai para um `tests/conftest.py` quando dois ou mais arquivos a usam.

## Arquivos desta skill
- [etapas.md](etapas.md): etapas 0–12 com micro passos, oráculos e dependências.
- [trabalho.md](trabalho.md): o que o trabalho pede, a nota, as regras da equipe, o prazo e o cronograma.
- [armadilhas.md](armadilhas.md): checklist de revisão.
