# O trabalho, a nota e as pendências

## O que o trabalho pede

Um drone sai do campus UniBrasil (CEP 82821020), fotografa todos os pontos de `dados/coordenadas.csv` mais as coordenadas extras da equipe (cada um uma vez) e volta ao campus. Tudo isso em até 7 dias, voando só das 06:00:00 às 19:00:00 e sem nunca ficar sem bateria no ar. A equipe escolhe a **ordem dos pontos**, a **velocidade de cada trecho** e os **dias/horários de voo** para minimizar o custo (tempo de voo + pousos). É obrigatório usar computação evolucionária (algoritmo genético), em Python rodando nativo no Linux.

## Como a nota é dividida (priorize nessa ordem)

| Peso | Critério | Onde se ganha |
|---|---|---|
| 30% | Requisitos: distância, vento e bateria, taxa de pouso no fim do dia, custo e tempo | Etapas 1–6 e 9 |
| 30% | Computação evolucionária: fitness clara, codificação genética (blocos construtivos), solução válida, monitoramento e critério de parada, qualidade da ordem **e dos horários** | Etapas 6–8 e 10 |
| 20% | Clareza: documentação das coordenadas extras, boas práticas, nomes, separação de arquivos, facilidade de verificar os resultados | todas + `docs/` |
| 20% | Percentual de cobertura dos testes unitários | Etapa 11 (cobertura ≥ 90%) |

O professor penaliza **severamente** erros de interpretação típicos de IA e código irrelevante.

## Entregáveis (um único ZIP; detalhes na skill `preparar-entrega`)

1. Código-fonte, com README dizendo como instalar e quais comandos executar para chegar ao resultado entregue (com a semente), e um modo rápido para reproduzir ao menos parcialmente.
2. Testes unitários próprios (mínimo 3; aqui, um por requisito) e evidência do percentual de cobertura.
3. Evidências de execução do algoritmo: log, `resultados/progresso.csv`, gráfico de convergência e saída do validador.
4. CSV com o melhor plano de voo (`resultados/plano_de_voo.csv`, 11 colunas).
5. Nome completo e matrícula de **todos** os integrantes. Erro ou omissão aqui é falta grave.
6. Documentação das coordenadas extras (matrícula e distância em metros até o ponto mais próximo).

## Regras da equipe

- Equipe: Vitor Hugo Viana Mondequi (2024100142) e Matheus Dominguez Biesek (2024100467). A regra é não repetir nenhum integrante da equipe do 1º bimestre: os dois não podem ter feito o trabalho do 1º bimestre juntos.
- É proibido compartilhar arquivos com outras equipes, inclusive testes. A pena é zero para todas as equipes envolvidas.
- Um só integrante envia o ZIP. Se os dois enviarem, o professor escolhe uma versão arbitrariamente.
- O enunciado pede que falhas conceituais e contradições sejam esclarecidas com o professor. A equipe optou por registrá-las na seção 4 de `docs/decisoes.md`.

## Prazo e decisões

**Prazo de entrega: terça, 24/11/2026** (A13).

Em 2026-11-12 o Matheus decidiu não consultar o professor sobre as regras. Todas as decisões (A1–A21) foram confirmadas pela equipe e estão na seção 4 de `docs/decisoes.md`, junto com a lista de erros encontrados no enunciado. Não reabra essas decisões sem um pedido do Matheus.

## Ordem das etapas e cronograma (fluxo solo)

Desde 2026-11-10, o Matheus faz as etapas sozinho, direto na `main` (ver `CLAUDE.md`). O painel (`.claude/skills/desenvolver-demanda/painel.sh`) mostra o que já está feito.

5 Bateria e custo (feita) → 2 Coordenadas extras (feita) → 7 Cromossomo → 6 Simulador → 9 CSV e validador → 8 Algoritmo genético → 10 Experimentos → 12 Entrega. A 11 (cobertura) é contínua.

| Terminar até | Etapa |
|---|---|
| qui 12/11 | 2.5 e 2.6: comando `extras` e `docs/coordenadas_extras.md` |
| sex 13/11 | 7 Cromossomo |
| dom 15/11 | 6 Simulador (a maior: 2 dias) |
| seg 16/11 | 9 CSV de saída e validador independente |
| qua 18/11 | 8 Algoritmo genético (2 dias) |
| sex 20/11 | 10 Experimentos (R$ 40, 80 e 160 por hora) e execução final |
| sáb 21/11 | 12 Entrega: ZIP montado e testado como o professor |
| dom 22 e seg 23/11 | Folga para imprevistos |
| **ter 24/11** | **Prazo: enviar o ZIP** |

- O validador (Etapa 9) continua **sem importar o simulador**, para conferir o plano de forma independente.

O checklist final de entrega e a montagem do ZIP estão na skill `preparar-entrega`.
