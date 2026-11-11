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
- Toda falha conceitual ou contradição do enunciado deve ser levada ao professor (ver abaixo).

## Pendências com o professor

**Prazo de entrega: 24/11/2026** (A13).

O enunciado diz que é **dever da equipe** esclarecer com o professor toda falha conceitual, instrução sem sentido ou informação contraditória. A mensagem abaixo **informa** só as falhas reais e o que adotamos, então ela vale mesmo sem resposta. Os pontos em que o enunciado só é omisso (A1, A3, A5, A6, A9, A10) não vão na mensagem: foram decididos pela leitura mais segura em `docs/decisoes.md`. Se o professor responder, registre a resposta na seção 4 de `docs/decisoes.md` e ajuste o código e os testes. Mensagem pronta para enviar:

> Professor, boa noite. Somos a equipe Vitor Hugo Viana Mondequi (2024100142) e Matheus Dominguez Biesek (2024100467). Como pede a especificação, registramos os pontos que nos pareceram falhas ou contradições e a interpretação que adotamos. Se alguma estiver errada, por favor nos avise.
>
> 1. **Vento:** no exemplo, a soma do vetor do drone (apontado para o destino) com o vetor do vento resulta num rumo de 28,3° em vez de 39,5°, ou seja, o drone não chegaria ao destino. Usamos o triângulo de velocidades, com correção de rumo: 39,34 km/h em vez de 41,00 km/h no exemplo.
> 2. **Velocidade:** a coluna do CSV diz "0 a 83", mas o mínimo é 10 m/s e só valem múltiplos de 4. Usamos 36, 40, …, 80 km/h.
> 3. **Paradas:** "a cada troca de bateria [...] 60 s se não houver pouso" não faz sentido, porque sem pouso não há troca de bateria. Lemos como "a cada parada".
> 4. **Custo:** o custo é medido pelo tempo de voo e pelos pousos, mas não há conversão entre segundos e reais. Usamos 1 h de voo = R$ 80 e comparamos 40, 80 e 160 nos experimentos.
> 5. **Tabela de vento:** a linha em nós não corresponde à linha em km/h. Usamos a linha em km/h.
>
> Obrigado!

## Ordem das etapas (fluxo solo)

Desde 2026-11-10, o Matheus faz as etapas sozinho, direto na `main` (ver `CLAUDE.md`). O painel (`.claude/skills/desenvolver-demanda/painel.sh`) mostra o que já está feito.

5 Bateria e custo → 2 Coordenadas extras → 7 Cromossomo → 6 Simulador → 9 CSV e validador → 8 Algoritmo genético → 10 Experimentos → 12 Entrega. A 11 (cobertura) é contínua.

- A 2 vem cedo porque a 2.3 depende de escolher as coordenadas no mapa: uma por integrante, cada uma ligada à própria matrícula.
- O validador (Etapa 9) continua **sem importar o simulador**, para conferir o plano de forma independente.

O checklist final de entrega e a montagem do ZIP estão na skill `preparar-entrega`.
