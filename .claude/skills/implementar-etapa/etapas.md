# Etapas do projeto: passo a passo com micro passos

Como usar:
- Fluxo de um terminal, direto na `main` (skill `desenvolver-demanda`): um commit por micro passo, e cada commit marca o `[x]` do seu micro passo.
- Os micro passos são as caixas `- [ ]`. Para ver o resumo, rode `.claude/skills/desenvolver-demanda/painel.sh`. A ordem das etapas está no `CLAUDE.md`.
- Os caminhos são relativos a `src/surveyor/`, os códigos A# remetem a `docs/decisoes.md` e o contexto do trabalho está em [trabalho.md](trabalho.md).

Todo micro passo de código segue a mesma ordem: **teste primeiro → implementação mínima → `make testar`**. O último micro passo de cada etapa é sempre o **fechamento**:
1. trocar a "API prevista" da docstring do módulo pela descrição real;
2. `make verificar` verde;
3. revisar o diff com [armadilhas.md](armadilhas.md);
4. commit do fechamento e resposta curta com a próxima etapa (skill `desenvolver-demanda`).

| Etapa | Depende de | Pode andar junto com |
|---|---|---|
| 0 Base e pendências | — | — |
| 1 Dados | 0 | 3, 4, 5, 7 |
| 2 Extras | 1, 3 | 4, 5, 7 |
| 3 Geo | 0 | 1, 4, 5, 7 |
| 4 Vento | 3 (rumo) | 1, 5, 7 |
| 5 Bateria e custo | 0 | 1, 3, 4, 7 |
| 6 Simulador | 1, 3, 4, 5 | 7, 9 |
| 7 Cromossomo | 0 | 1 a 6 |
| 8 Algoritmo genético | 6, 7 | 9 |
| 9 CSV e validador | 1, 3, 4, 5 (não usa o simulador) | 6, 8 |
| 10 Experimentos | 8, 9 | — |
| 11 Cobertura | contínuo | — |
| 12 Entrega | todas | — |

---

## Etapa 0 — Base do projeto e pendências
**Ramo:** `arquitetura-base` (a base) e `docs-respostas-professor` (respostas) · **Depende de:** —

- [x] 0.1 Estrutura em Clean Architecture com ferramentas (`pyproject.toml`, `Makefile`) e testes de arquitetura. O pipeline do GitHub roda lint, tipos, todos os testes com cobertura (Python 3.10 e 3.14) e exige teste em todo PR que muda código.
- [x] 0.2 Base do domínio: `dominio/regras.py`, `dominio/modelos.py`, `dominio/erros.py`, `dominio/calculos/relogio.py`; mais `otimizacao/parametros.py` e `otimizacao/progresso.py`.
- [x] 0.3 Logs: `infraestrutura/logs/configuracao.py` (política) e `monitor_progresso.py` (`MonitorDeProgresso`).
- [x] 0.4 `aplicacao/configuracao.py` e CLI (`otimizar`, `validar`). Os casos de uso ainda levantam `NotImplementedError`.
- [x] 0.5 `dados/coordenadas.csv` (do AVA, conferido) e `dados/vento.csv` (35 células conferidas).
- [x] 0.6 Skills (`desenvolver-demanda`, `implementar-etapa`, `preparar-entrega`) e o hook que roda `git pull` ao abrir o projeto.
- [x] 0.7 Publicar a base na `main` (PR do ramo `arquitetura-base`, revisado pelo outro integrante).
- [x] 0.8 Prazo: **24/11/2026** (A13). Em 2026-11-12 a equipe decidiu não consultar o professor sobre as regras.
- [x] 0.9 Decisões A1–A13 confirmadas pela equipe na seção 4 de `docs/decisoes.md`, sem mudança no código.

## Etapa 1 — Leitura dos dados de entrada
**Módulo:** `infraestrutura/arquivos/leitor_csv.py` · **Depende de:** 0

- [x] 1.1 Teste: um mini-CSV `cep,longitude,latitude` (3 linhas, em `tmp_path`) vira `list[Coordenada]`, com latitude e longitude nos campos certos e o texto preservado (inclusive o zero final de `-25.4387124100140`).
- [x] 1.2 Implementar `ler_coordenadas(caminho) -> list[Coordenada]`.
- [x] 1.3 Testes de erro: CEP duplicado, CEP inválido, coluna faltando e campus ausente viram `ErroDados("arquivo, linha N: motivo")`.
- [x] 1.4 Implementar as validações.
- [x] 1.5 `ler_extras(caminho)`: mesmo formato `cep,longitude,latitude`, mas com `pode_pousar=False` (A6). Inclui o teste.
- [x] 1.6 Teste de integração em `tests/integracao/`: o `dados/coordenadas.csv` real tem 374 pontos e o primeiro é o campus `82821020`.
- [x] 1.7 Fechamento.

**Já conferido no arquivo real:** cabeçalho `cep,longitude,latitude` (a longitude vem **antes**), 374 linhas, CEPs únicos de 8 dígitos, 13 casas decimais e nenhuma coordenada repetida.

## Etapa 2 — Coordenadas extras da equipe
**Módulos:** `dominio/validacao/extras.py`, `dados/extras.csv`, `docs/coordenadas_extras.md` · **Depende de:** 1, 3

- [x] 2.1 Testes de `validar_extra(extra, matricula, base, regras) -> list[str]`. Cada caso deve ser rejeitado: 12 casas, final diferente da matrícula, a 99 m de um ponto, a 1501 m do ponto mais próximo do professor, CEP diferente dos 8 últimos dígitos. E um caso válido deve passar.
- [x] 2.2 Implementar `validar_extra` (usa `geo.distancia_km`).
- [x] 2.3 Cada integrante escolhe a sua coordenada (CEPs **24100142** e **24100467**):
  1. no mapa, ache um local sem pontos, a 300–1000 m de algum ponto do professor (folga para as regras de 100 m e 1500 m);
  2. latitude com 13 casas = 5 casas livres + os 8 dígitos da matrícula (ex.: `-25.43871` + `24100142` = `-25.4387124100142`);
  3. longitude também com exatamente 13 casas;
  4. se o validador recusar, mova o ponto e repita.
- [x] 2.4 Gravar `dados/extras.csv` (`cep,longitude,latitude`) e validar as duas juntas: a distância entre elas também precisa ser de pelo menos 100 m.
- [x] 2.5 Comando `python -m surveyor extras`: valida e imprime a tabela de `docs/coordenadas_extras.md` (integrante, matrícula, CEP, latitude, longitude, ponto mais próximo e distância em metros na base consolidada). Atualizar o documento com essa saída.
- [x] 2.6 Fechamento.

## Etapa 3 — Geodésia
**Módulo:** `dominio/calculos/geo.py` · **Depende de:** 0

- [x] 3.1 Testes de `distancia_km`: 1° de latitude = `111.19492664455873` km (`approx`), o mesmo ponto dá 0 e `d(a,b) == d(b,a)`.
- [x] 3.2 Implementar Haversine: `a = sin²(Δφ/2) + cos φ1 · cos φ2 · sin²(Δλ/2)`; `d = 2 · R · atan2(√a, √(1 − a))`, com φ e λ **em radianos** e `R = regras.raio_terra_km` (6371).
- [x] 3.3 Testes de `rumo_graus`: norte = 0, sul = 180, leste ≈ 90, oeste ≈ 270.
- [x] 3.4 Implementar `θ = atan2(sin Δλ · cos φ2, cos φ1 · sin φ2 − sin φ1 · cos φ2 · cos Δλ)` em graus, módulo 360.
- [x] 3.5 Matrizes N×N pré-calculadas de distância e de rumo. Testar diagonal zero e simetria da distância.
- [x] 3.6 Fechamento.

## Etapa 4 — Vento
**Módulos:** `dominio/calculos/vento.py`, `infraestrutura/arquivos/leitor_csv.py` (`ler_vento`) · **Depende de:** 3

- [x] 4.1 `ler_vento(caminho)`: 35 linhas, dias de 1 a 7, blocos 6/9/12/15/18 e direções válidas. Inclui os testes.
- [x] 4.2 Direção em graus (rosa dos ventos de 16 pontos: N = 0, NE = 45, ENE = 67,5, E = 90, SSE = 157,5, SSW = 202,5, WSW = 247,5). O vento sopra para `dir + 180`. Teste: vento de SSE aponta para 337,5°.
- [x] 4.3 `bloco_do_horario(hora_saida_s)` pela hora de **saída**. Testes: 08:59:00 → 6; 09:21:00 → 9; 18:59:59 → 18; antes de 06:00:00 → `ValueError`.
- [x] 4.4 Soma vetorial: **não** vira função, porque nada a usaria (código sem uso é penalizado) e o modelo é o triângulo (A2). O valor do enunciado pela soma (`41.0026532396`) fica registrado no teste do triângulo como o que **não** deve sair.
- [x] 4.5 `velocidade_solo_kmh` pelo triângulo (A2): `α = (dir + 180) − rumo`; `v_solo = w·cos α + √(v² − (w·sin α)²)`. Testes: o exemplo dá `39.3372461072`; vento 0 → `v`; a favor puro → `v + w`; contra puro → `v − w`.
- [x] 4.6 Fechamento.

## Etapa 5 — Bateria, tempo e custo
**Módulos:** `dominio/calculos/bateria.py`, `dominio/calculos/custo.py` · **Depende de:** 0

- [x] 5.1 `autonomia_s(v, regras)` com a velocidade **ajustada**. Oráculos:
  - com `Regras(fator_autonomia=1.0)`: A(36) = 5000, A(48) = 2812.5, A(60) = 1800, A(72) = 1250;
  - no padrão: A(36) = 5700, A(80) ≈ 1154.25;
  - velocidades 0, 32, 83 e 84 → `ValueError`.
- [x] 5.2 `consumo(duracao_s, v, regras) = duracao_s / A(v)`, uma função só para o trecho e a parada (as duas contas são iguais); na parada, `v` é a do trecho que chega (A1). Com testes.
- [x] 5.3 `tempo_trecho_s = ceil(d / v_solo × 3600 − 1e-9)`. Testes: 120.4 → 121; 120.0 → 120; 120.00000000000001 → 120.
- [x] 5.4 `taxa_pouso_reais(hora_final_s, regras)` (A11). Testes: 17:00:00 → R$ 80; 17:00:01 → R$ 160.
- [x] 5.5 `custo_total(plano, regras, operacao)` (A4). Teste com um plano de 2 trechos calculado à mão.
- [x] 5.6 Fechamento.

## Etapa 6 — Simulador (decodificador)
**Módulo:** `dominio/simulador.py` · **Depende de:** 1, 3, 4, 5

- [x] 6.1 Definir a entrada (ordem dos pontos, velocidade por ponto, dias habilitados: tipos simples, sem o Cromossomo) e a saída (`PlanoDeVoo`, se é válido e o motivo quando não é).
- [ ] 6.2 Caso feliz: 3 pontos, sem pouso intermediário, resultado calculado à mão.
- [ ] 6.3 Pouso por bateria. Invariante: ao chegar a um ponto, sempre há bateria para pousar ali. Se faltar para o próximo trecho, a linha anterior vira Pouso = SIM, a parada passa de 60 para 172 s e a bateria vai a 100%.
- [ ] 6.4 Fim de expediente (`operacao.limite_operacional_s`, 17:00:00; o teto é 19:00:00): seguir para o próximo dia habilitado às 06:00:00. Depois do dia 7, o plano é inválido.
- [ ] 6.5 Extras: nunca pousar nelas. Antes de voar para uma extra, garantir bateria para chegar ao próximo ponto que pode pousar e pousar lá.
- [ ] 6.6 Trecho impossível: tentar outras velocidades (a mais próxima primeiro), depois esperar o próximo bloco ou dia; se nada servir, o plano é inválido. Com vento contra de 21 km/h, o alcance fica em torno de 24 km.
- [ ] 6.7 Teste de propriedade com 1.000 permutações do arquivo real: a bateria nunca fica abaixo da reserva, nenhum horário passa de 19:00:00 e nenhuma extra recebe pouso (`@pytest.mark.lento`).
- [ ] 6.8 Fechamento.

## Etapa 7 — Cromossomo
**Módulos:** `otimizacao/cromossomo.py`, `docs/codificacao.md` · **Depende de:** 0

- [x] 7.1 `Cromossomo` com três partes: **ordem** (permutação dos pontos, sem o campus), **velocidade** (índice de 0 a 11 por ponto de destino, `36 + 4·i`, N + 1 genes) e **calendário** (7 bits: voar ou não em cada dia). Incluir validação, cópia independente e testes. A cópia **não** virou função: o cromossomo é imutável (tuplas, `frozen`), então o filho nunca altera o pai. O limite superior dos índices (11) e os 7 bits são conferidos na conversão da 7.2, que recebe as `Regras`.
- [ ] 7.2 Conversão do cromossomo na entrada do simulador, com teste.
- [x] 7.3 Escrever `docs/codificacao.md`:
  - comparar com as 7 codificações sugeridas no enunciado;
  - explicar a hipótese dos blocos construtivos (a velocidade viaja junto com o ponto);
  - explicar por que os cruzamentos clássicos citados no enunciado (um ponto, múltiplos pontos, uniforme) **não** servem para a permutação, porque geram CEP repetido e CEP faltando, e por que usamos OX/PMX/ERX na ordem e o uniforme só no calendário e nas velocidades;
  - justificar o calendário: os dias 1 e 6 têm vento de 3 a 8 km/h e os dias 2 e 5, de 16 a 21 km/h; vento constante nunca reduz o tempo de uma rota fechada (+0% a +40% em 2.000 rotas simuladas); a espera em solo não conta (A5).
- [ ] 7.4 Fechamento.

## Etapa 8 — Algoritmo genético
**Módulos:** `otimizacao/operadores.py`, `fitness.py`, `algoritmo.py`; `aplicacao/otimizar_rota.py` · **Depende de:** 6, 7

- [ ] 8.1 Seleção por torneio (k = 3), com testes. O custo é **minimizado**: qualquer seleção proporcional (roleta) tem que converter o custo em aptidão antes (ex.: `max_custo − custo` ou rank).
- [ ] 8.2 Cruzamento OX (e PMX/ERX para os experimentos). A velocidade herda do pai que forneceu o ponto e o calendário usa cruzamento uniforme. Testes: a permutação sai válida e os pais ficam intactos.
- [ ] 8.3 Mutações: troca, inversão e deslocamento (ordem); ±1 (velocidade); inverter um bit (calendário). Com testes.
- [ ] 8.4 Fitness = custo do simulador + penalidade se o plano for inválido.
- [ ] 8.5 População inicial: 10–20% de vizinho mais próximo perturbado e o resto aleatório; velocidades iniciais de 36 a 52.
- [ ] 8.6 Laço evolutivo com elitismo e critérios de parada (gerações, estagnação, tempo), chamando `ObservadorDeProgresso.registrar(...)` a cada geração. Usar `random.Random(semente)`.
- [ ] 8.7 `otimizar_rota.executar`: ler as entradas → rodar o GA com `MonitorDeProgresso` (`resultados/progresso.csv`) → validar e gravar (depende da Etapa 9).
- [ ] 8.8 Gráfico de convergência a partir de `progresso.csv` (o `matplotlib` entra no `pyproject` nesta etapa).
- [ ] 8.9 Testes:
  - a mesma semente dá o mesmo resultado;
  - integração com 8–10 pontos e poucas gerações;
  - o custo final é menor que o do vizinho mais próximo a 36 km/h.
- [ ] 8.10 Fechamento.

## Etapa 9 — CSV de saída e validador independente
**Módulos:** `infraestrutura/arquivos/escritor_csv.py`, `dominio/validacao/plano.py`, `aplicacao/validar_plano.py` · **Depende de:** 1, 3, 4, 5

- [ ] 9.1 `escrever_plano`. Teste do cabeçalho exato: `CEP inicial,Latitude inicial,Longitude inicial,Dia do vôo,Hora inicial,Velocidade,CEP final,Latitude final,Longitude final,Pouso,Hora final`. Coordenadas como texto, `HH:MM:SS`, `SIM`/`NÃO`, UTF-8 e hífen ASCII.
- [ ] 9.2 Leitura de um CSV de plano (para o validador), com testes.
- [ ] 9.3 Regras do validador, **sem usar o simulador**, cada uma com um teste de CSV adulterado:
  - campus no início e no fim, e a última linha com Pouso = SIM;
  - continuidade entre as linhas;
  - cada CEP aparece uma vez;
  - as coordenadas batem com a entrada;
  - velocidades permitidas;
  - dias de 1 a 7 e horários dentro da janela;
  - Hora final recalculada;
  - bateria nunca abaixo da reserva;
  - nenhum pouso em extra;
  - todo dia termina com pouso.
- [ ] 9.4 `validar_plano.executar`, mais um resumo (tempo total, pousos, R$, custo).
- [ ] 9.5 Fechamento.

## Etapa 10 — Experimentos e execução final
**Arquivo:** `docs/experimentos.md` · **Depende de:** 8, 9

- [ ] 10.1 Rodar de 3 a 5 sementes por configuração:
  - população (100 / 200 / 400);
  - cruzamento (OX / PMX / ERX);
  - mutação (5 / 15 / 25%);
  - seleção (torneio k = 2/3/5, rank, roleta sobre a aptidão transformada);
  - elitismo (0 / 2 / 5%);
  - semeadura (0 / 10 / 20%);
  - `valor_hora_reais` (40 / 80 / 160).
- [ ] 10.2 Comparar mecanismos para soluções inválidas (o enunciado pede): reparo do simulador × penalidade.
- [ ] 10.3 Registrar a tabela em `docs/experimentos.md` e conferir as ordens de grandeza (abaixo).
- [ ] 10.4 Atualizar o padrão de `ParametrosGA` para a melhor configuração.
- [ ] 10.5 Execução final com a semente fixada: plano, progresso, gráfico, mapa da rota, log e saída do validador em `resultados/`.
- [ ] 10.6 Fechamento.

**Ordens de grandeza** (rota do vizinho mais próximo, sem vento e sem extras: 340,8 km; 375 paradas de 60 s ≈ 6,25 h):
- a 36 km/h: ≈ 15,7 h de voo e ≈ 10 baterias;
- a 80 km/h: ≈ 10,5 h de voo e ≈ 33 baterias.

Bastam 1 ou 2 dias de voo. Um resultado muito fora dessas faixas indica bug.

## Etapa 11 — Cobertura (contínua)
- [ ] 11.1 Manter `make cobertura` ≥ 90% a cada PR (o `fail_under` reprova abaixo disso).
- [ ] 11.2 Antes da entrega, fechar as lacunas apontadas em `term-missing`, sem testes vazios.
- [ ] 11.3 Gravar `resultados/cobertura.txt` final (evidência exigida).

## Etapa 12 — Entrega
**Skill:** `preparar-entrega` (os micro passos detalhados estão lá) · **Depende de:** todas

- [ ] 12.1 Pré-requisitos: todas as etapas na `main` e enviadas (`git push`). As decisões já estão confirmadas (seção 4 de `docs/decisoes.md`).
- [ ] 12.2 Evidências finais em `resultados/`.
- [ ] 12.3 Documentos conferidos (README de reprodução, nomes, matrículas, extras).
- [ ] 12.4 `make entrega` gera o ZIP só com o conteúdo permitido.
- [ ] 12.5 ZIP testado como o professor vai usar (instalação limpa, testes, execução).
- [ ] 12.6 Um só integrante envia.
