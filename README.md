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
- O programa usa só a biblioteca padrão do Python. O `pip` instala apenas as ferramentas de teste.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Reproduzir o resultado entregue

```bash
python -m surveyor otimizar --semente 42    # gera resultados/plano_de_voo.csv e resultados/progresso.csv
python -m surveyor validar                  # confere o plano de forma independente (bateria, horários, CEPs)
python -m surveyor extras                   # valida as coordenadas extras e imprime a tabela de docs/coordenadas_extras.md
```

- **Reprodução parcial (1 a 2 minutos):** `python -m surveyor otimizar --rapido`.
- **Sem instalar nada:** `PYTHONPATH=src python3 -m surveyor otimizar --rapido`.
- **Todas as opções:** `python -m surveyor --help` e `python -m surveyor otimizar --help`.

O resultado entregue, com o log da execução, o progresso por geração, os gráficos e a saída do validador, está em `resultados/`. Cada execução também grava um log em `logs/surveyor_<data>_<hora>.log`.

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
