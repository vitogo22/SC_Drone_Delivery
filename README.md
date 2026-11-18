# UNIBRASIL Surveyor

Plano de voo de um drone que fotografa CEPs de Curitiba e volta ao campus UniBrasil, otimizado por **algoritmo genético** (Serviços Cognitivos, atividade discente supervisionada 2, Prof. Mozart Hasse).

## Equipe

| Nome completo | Matrícula | CEP da coordenada extra |
|---|---|---|
| Vitor Hugo Viana Mondequi | 2024100142 | 24100142 |
| Matheus Dominguez Biesek | 2024100467 | 24100467 |

## Requisitos

- Linux com Python **3.10 ou superior** (`python3 --version`).
- Módulo `venv`. No Debian/Ubuntu, se `python3 -m venv` falhar: `sudo apt install python3-venv`.
- Dependências (instaladas pelo `pip`): `matplotlib`, para o gráfico de convergência e o mapa da rota, e as ferramentas de teste.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Reproduzir o resultado entregue

```bash
python -m surveyor otimizar --semente 42    # cerca de 5 min; gera resultados/plano_de_voo.csv, progresso.csv, convergencia.png e rota.png
python -m surveyor validar                  # confere o plano sem o simulador e mostra tempo, pousos e custo
python -m surveyor extras                   # valida as coordenadas extras e imprime a tabela de docs/coordenadas_extras.md
python -m surveyor experimentos             # compara os parâmetros do GA (resultados/experimentos.csv e a tabela de docs/experimentos.md)
```

- **Experimentos:** levam de 40 a 60 min. **Não é preciso rodar para avaliar**: a tabela e a análise estão em `docs/experimentos.md`, e cada execução está em `resultados/experimentos.csv`.
- **Reprodução parcial (menos de 1 minuto):** `python -m surveyor otimizar --rapido`.
- **Outro plano:** `python -m surveyor validar caminho/do/plano.csv` (sai com código 1 e lista cada violação, com a linha do CSV).
- **Todas as opções:** `python -m surveyor --help` e `python -m surveyor otimizar --help`.

**Resultado entregue** (semente 42, `resultados/plano_de_voo.csv`): R$ 2.182,47, sendo 15,28 h de voo e 12 pousos (R$ 960,00 de taxas), nos dias 1 e 6. O validador aprova o plano. A rota do vizinho mais próximo a 36 km/h custa R$ 2.465,42.

Os arquivos da execução entregue, com o log, o progresso por geração, os gráficos e a saída do validador, estão em `resultados/`. Cada execução também grava um log em `logs/surveyor_<data>_<hora>.log`.

## Testes e cobertura

```bash
python -m pytest                                        # todos os testes
python -m pytest --cov --cov-report=term-missing        # com o percentual de cobertura
```

A evidência de cobertura da versão entregue está em `resultados/cobertura.txt`.

## Estrutura

Clean Architecture em quatro camadas. A dependência sempre aponta para o domínio:

```
src/surveyor/
├── dominio/          regras de negócio: regras do enunciado, modelos, cálculos, simulador, validação
├── otimizacao/       algoritmo genético (parâmetros, cromossomo, operadores, fitness, laço)
├── aplicacao/        casos de uso: otimizar_rota, validar_plano e conferir_extras
├── infraestrutura/   arquivos CSV e logs (política de logs e monitor de progresso)
└── interface/        linha de comando
tests/
├── unidade/          espelha src/surveyor/
├── integracao/       executa o programa de ponta a ponta
└── test_arquitetura.py
dados/                entradas (coordenadas do AVA, coordenadas extras, vento)
docs/                 decisões, arquitetura, coordenadas extras, codificação, experimentos
resultados/           plano de voo e evidências de execução e de cobertura
```

## Documentação

- [`docs/decisoes.md`](docs/decisoes.md): regras do enunciado e interpretações adotadas.
- [`docs/arquitetura.md`](docs/arquitetura.md): camadas, política de logs, convenções e testes.
- [`docs/coordenadas_extras.md`](docs/coordenadas_extras.md): coordenadas extras da equipe.
- [`docs/codificacao.md`](docs/codificacao.md): cromossomo, comparação com as codificações sugeridas e blocos construtivos.
- [`docs/experimentos.md`](docs/experimentos.md): parâmetros testados no algoritmo genético.
