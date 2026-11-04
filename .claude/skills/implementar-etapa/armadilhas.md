# Checklist de armadilhas

O enunciado foi escrito para induzir IAs ao erro. Passe cada diff por esta lista.

## Regras
- [ ] Algum requisito tratado como opcional ou condicional (ex.: por número de matrícula)? **Todos valem para todos**, e isso nem deve ser citado nos documentos.
- [ ] A autonomia foi calculada com a velocidade **com vento**? O certo é a velocidade ajustada.
- [ ] O bloco de vento foi escolhido pela hora de **chegada**? O certo é a de saída.
- [ ] Foi usada a coluna 21h, a linha em nós ou as rajadas?
- [ ] A direção do vento foi lida como "para onde vai"? Ela é "de onde vem" (+180°).
- [ ] O vento foi calculado pela soma vetorial sem corrigir o rumo? O padrão é o triângulo (A2).
- [ ] A parada foi descontada na taxa de 36 km/h? O certo é a taxa do trecho (A1).
- [ ] Apareceu `R = 6,371`, distância euclidiana em graus ou graus sem conversão para radianos?
- [ ] Foi usado `round`, ou arredondada a autonomia? O certo é o teto (`ceil`) no tempo.
- [ ] Alguma velocidade fora de 36–80 ou que não seja múltipla de 4?
- [ ] A taxa das 17h foi cobrada na decolagem, em vez do pouso?
- [ ] Faltou o pouso de fim de dia, há voo depois de 19:00:00 ou um trecho atravessa a noite?
- [ ] O drone pousa numa coordenada extra (A6)?
- [ ] O voo sempre começa no dia 1 e segue dias seguidos, ignorando o calendário?
- [ ] Cruzamento de um ponto, múltiplos pontos ou uniforme aplicado direto na permutação da rota (gera CEP repetido e CEP faltando)?
- [ ] Roleta aplicada ao custo como se fosse aptidão (com minimização, ela favorece os piores)?

## Dados
- [ ] Latitude e longitude trocadas na leitura do CSV do professor?
- [ ] Coordenada convertida para `float` e reescrita (perde casas e o zero final)?
- [ ] CEP tratado como número (perde o zero à esquerda)?
- [ ] Travessão "–" ou outro caractere ambíguo no CSV ou no código (o ruff RUF001 acusa)?
- [ ] CEP repetido ou plano que não volta ao campus?

## Código
- [ ] Código morto, modelo alternativo, flag que ninguém lê ou parâmetro sem uso?
- [ ] Número mágico fora de `dominio/regras.py`?
- [ ] `print` fora da CLI, log por avaliação no laço quente ou `random` global?
- [ ] Import que quebra as camadas (o validador importando o simulador, o domínio importando `infraestrutura`)?
- [ ] Requisito sem teste ou teste sem verificação real?
- [ ] Código alterado em `src/` sem teste alterado em `tests/` (o job "PR traz testes" reprova)?
- [ ] `skip`/`xfail` sem motivo, `# pragma: no cover` para fugir da cobertura, ou job do pipeline desligado ou afrouxado?
- [ ] Dependência, marcador, arquivo de dados ou comando novo sem ajuste no `pyproject.toml` ou no `.github/workflows/ci.yml`?
