# Arquitetura

O projeto segue **Clean Architecture** em quatro camadas. A dependência sempre aponta para dentro: o domínio (regras de negócio) não conhece arquivos, logs, CLI nem o algoritmo genético.

```
interface ──► aplicacao ──► otimizacao ──► dominio
                   │                          ▲
                   └──► infraestrutura ───────┘
```

## Estrutura

```
SC_Drone_Delivery/
├── pyproject.toml              dependências e configuração de pytest, cobertura, ruff e mypy
├── dados/                      entradas versionadas: coordenadas.csv (AVA), extras.csv, vento.csv
├── docs/                       decisões, arquitetura, coordenadas extras, experimentos
├── logs/                       um log por execução (criada na primeira execução, fora do git)
├── resultados/                 evidências da entrega: plano de voo, progresso, gráficos, cobertura
├── src/surveyor/
│   ├── dominio/                REGRAS DE NEGÓCIO (núcleo, sem I/O)
│   │   ├── regras.py           Regras do enunciado + ParametrosOperacao (escolhas da equipe)
│   │   ├── modelos.py          Coordenada, Trecho, PlanoDeVoo
│   │   ├── erros.py            ErroSurveyor e subclasses
│   │   ├── calculos/           relógio, geo, vento, bateria, custo (funções puras)
│   │   ├── simulador.py        decisões de voo -> plano sempre seguro
│   │   └── validacao/          regras das extras e validador independente do plano
│   ├── otimizacao/             ALGORITMO GENÉTICO (motor; depende só do domínio)
│   │   ├── parametros.py       ParametrosGA
│   │   ├── progresso.py        contrato ObservadorDeProgresso + EstatisticasDaGeracao
│   │   └── cromossomo.py, operadores.py, fitness.py, algoritmo.py
│   ├── aplicacao/              CASOS DE USO (orquestram as outras camadas)
│   │   ├── configuracao.py     ArquivosDeEntrada, Configuracao
│   │   ├── otimizar_rota.py    executar(): ler -> otimizar -> validar -> gravar
│   │   └── validar_plano.py    executar(): conferir um CSV
│   ├── infraestrutura/         DETALHES TÉCNICOS (implementam contratos internos)
│   │   ├── arquivos/           leitor_csv.py, escritor_csv.py
│   │   └── logs/               configuracao.py (política de logs), monitor_progresso.py
│   └── interface/              ENTRADA DO USUÁRIO
│       └── cli.py              argumentos, logs, códigos de saída
└── tests/
    ├── unidade/                espelha src/surveyor/ (um arquivo de teste por módulo)
    ├── integracao/             executa `python -m surveyor` em outro processo
    └── test_arquitetura.py     garante as regras de dependência abaixo
```

## Regras de dependência

| Camada | Pode importar | Não pode importar |
|---|---|---|
| `dominio` | só a biblioteca padrão | qualquer outra camada |
| `dominio/validacao` | `dominio` | **`dominio.simulador`**: se o validador usasse a mesma lógica, um erro do simulador passaria |
| `otimizacao` | `dominio` | `aplicacao`, `infraestrutura`, `interface` |
| `infraestrutura` | `dominio`, `otimizacao` (contratos) | `aplicacao`, `interface` |
| `aplicacao` | todas as internas | `interface` |
| `interface` | `aplicacao`, `infraestrutura.logs`, `dominio.erros` | — |

`tests/test_arquitetura.py` reprova qualquer import que quebre a tabela. Imports relativos são proibidos pelo ruff (TID252), para que nenhum escape da verificação.

**Inversão de dependência no monitoramento:** o laço evolutivo (`otimizacao`) só conhece a interface `ObservadorDeProgresso`. Quem grava CSV e log é `infraestrutura/logs/monitor_progresso.py`, entregue pelo caso de uso. Nos testes do GA, basta passar um observador que guarda as estatísticas numa lista.

## Política de logs (`infraestrutura/logs/`)

| Destino | Nível | Para quê |
|---|---|---|
| terminal | escolhido com `--log-nivel` (padrão INFO) | acompanhar a execução |
| `logs/surveyor_<data>_<hora>.log` | DEBUG | diagnóstico; um arquivo por execução |
| `resultados/progresso.csv` | uma linha por geração | evidência do monitoramento e base do gráfico de convergência |

| Nível | Quando |
|---|---|
| ERROR | a execução não pôde continuar (erro esperado) ou o plano viola uma regra |
| WARNING | algo aceitável, mas suspeito |
| INFO | marcos: parâmetros, dados carregados, progresso a cada N gerações, resultado e arquivos gravados |
| DEBUG | detalhe de decisão (pouso inserido, melhora do melhor custo) |

O logging é configurado **só** na interface. Os módulos fazem `logger = logging.getLogger(__name__)`. Nada de `print` fora da CLI e nada de log por avaliação de indivíduo no laço do GA. Para a entrega, copie o log da execução final para `resultados/`.

## Convenções de código

| Assunto | Regra |
|---|---|
| Horário | `int` de segundos desde 00:00:00 do dia de voo; `HH:MM:SS` só via `dominio/calculos/relogio.py` |
| Unidades | no nome: `_km`, `_m`, `_s`, `_kmh`, `_reais`; bateria como fração de 0 a 1 |
| Coordenadas e CEP | texto como veio do arquivo (13 casas, zeros preservados); `float` só para as contas |
| Constantes | regras do enunciado só em `dominio/regras.py`; nada de número mágico |
| Configuração | passada como argumento (`regras`, `operacao`, `ga`); nada de variável global |
| Aleatoriedade | um `random.Random(semente)` criado no caso de uso e passado adiante |
| Erros | erro esperado = subclasse de `ErroSurveyor`, com arquivo/linha/valor na mensagem; bug não é capturado |
| Modelos | dataclasses `frozen=True, slots=True`; só dados, sem regras |
| Casos de uso | um por módulo, com uma função `executar(...)` |
| Estilo | nomes em português, type hints completos (mypy strict, inclusive nos testes), docstring curta |
| Código morto | proibido: nada de alternativas "por via das dúvidas", flags sem uso ou funções sem chamador |

## Testes

- `tests/unidade/` espelha `src/surveyor/`: `src/surveyor/dominio/calculos/geo.py` → `tests/unidade/dominio/calculos/test_geo.py`.
- O nome descreve o comportamento: `test_pouso_depois_das_17h_cobra_taxa_adicional`.
- Arrumar / agir / verificar; um comportamento por teste; `parametrize` para tabelas de oráculos; `pytest.approx` para floats.
- Dados pequenos no próprio teste ou em `tmp_path`. Teste unitário nunca lê `dados/coordenadas.csv`.
- Testes demorados levam `@pytest.mark.lento` e podem ser pulados com `pytest -m "not lento"`.
- Cobertura mínima de 90% (`fail_under`), atingida com testes de comportamento, nunca com código inútil.

## Comandos

Verificação de qualidade (ferramentas instaladas com `pip install -e ".[dev]"`): `ruff check src tests`, `mypy` e `pytest --cov`. As três precisam passar antes de qualquer mudança entrar no projeto.
