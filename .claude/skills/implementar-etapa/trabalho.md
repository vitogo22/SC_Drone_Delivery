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

O enunciado não informa a **data de entrega**. As decisões A1–A13 de `docs/decisoes.md` são provisórias. Quando o professor responder, registre a resposta na seção 4 de `docs/decisoes.md` e ajuste o código e os testes. Mensagem pronta para enviar:

> Professor, boa noite. Somos a equipe Vitor Hugo Viana Mondequi e Matheus Dominguez Biesek. Estudando a especificação do Trabalho 2, encontramos pontos que precisam de esclarecimento:
>
> 1. **Consumo nas paradas (60 s / 172 s):** a bateria deve ser descontada na taxa da velocidade de referência (36 km/h) ou na taxa da velocidade do trecho? Pretendemos usar a do trecho, por ser mais segura.
> 2. **Vento:** o exemplo soma o vetor do drone, apontado para o destino, com o vetor do vento. O vetor resultante aponta para 28,3° em vez de 39,5°, ou seja, o drone não chegaria ao destino. Podemos usar o triângulo de velocidades, com correção de rumo? No exemplo, ele dá 39,34 km/h em vez de 41,00 km/h.
> 3. **Fator 1,14:** ele multiplica a autonomia (5000 s → 5700 s) ou divide?
> 4. **Função de custo:** como combinar tempo de voo (segundos) com pousos (R$)? Propomos que 1 h de voo equivalha a R$ 80.
> 5. **Tempo total de voo:** é a soma do tempo no ar, sem contar a espera em solo entre os dias?
> 6. **Recarga nas coordenadas extras:** o drone pode pousar nelas, ou apenas nas coordenadas do seu arquivo?
> 7. **Pouso final no campus:** conta como pouso (172 s e R$ 80)? E os 172 s de um pouso saem inteiros da bateria que está chegando?
> 8. **Velocidade:** a tabela do CSV diz "0 a 83", mas o mínimo é 10 m/s e só se aceitam múltiplos de 4. As velocidades válidas são 36, 40, …, 80 km/h?
> 9. **Paradas:** no trecho "a cada troca de bateria [...] 60 s se não houver pouso", entendemos "a cada parada". Está correto?
> 10. **Prazo:** qual é a data de entrega?
>
> Obrigado!

## Ordem das etapas (fluxo solo)

Desde 2026-11-10, o Matheus faz as etapas sozinho, direto na `main` (ver `CLAUDE.md`). O painel (`.claude/skills/desenvolver-demanda/painel.sh`) mostra o que já está feito.

5 Bateria e custo → 2 Coordenadas extras → 7 Cromossomo → 6 Simulador → 9 CSV e validador → 8 Algoritmo genético → 10 Experimentos → 12 Entrega. A 11 (cobertura) é contínua.

- A 2 vem cedo porque a 2.3 depende de escolher as coordenadas no mapa: uma por integrante, cada uma ligada à própria matrícula.
- O validador (Etapa 9) continua **sem importar o simulador**, para conferir o plano de forma independente.

O checklist final de entrega e a montagem do ZIP estão na skill `preparar-entrega`.
