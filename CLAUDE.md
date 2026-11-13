# UNIBRASIL Surveyor: instruções para o Claude

Projeto acadêmico: algoritmo genético que gera o plano de voo de um drone. Python 3.10+, src layout, nomes em português. Equipe: Vitor Hugo Viana Mondequi e Matheus Dominguez Biesek. **Desde 2026-11-10 o Matheus faz as etapas sozinho.**

O professor avalia se a equipe resolve com IA um problema difícil, cujo enunciado tem contradições e armadilhas de propósito. O que importa é acertar as regras e provar isso com testes, não o processo de git.

## Como trabalhar (fluxo solo)
- **O que depende do Matheus vem em destaque.** Abra a resposta com um bloco "⚠️ PRECISO DE VOCÊ" dizendo exatamente o que ele precisa mandar. Um "pode seguir" depois disso **não** é a resposta: ele responde no automático. Repita o pedido até ele responder e, enquanto isso, só avance no que não depende dele.
- **Respostas curtas.** Um passo de cada vez: o que foi feito, o resultado do `make verificar` e o próximo passo em uma linha. Nada de painel completo, tabelas da equipe ou listas de pendências paralelas.
- **Direto na `main`:** sem ramos e sem PR. O Claude faz um commit por micro passo, com o código e o teste juntos (`git add` pelo nome dos arquivos) e o `[x]` do micro passo em `etapas.md`. Antes de cada commit, `make verificar` precisa estar verde.
- **O push é do Matheus:** esta máquina não tem login do GitHub para o Claude. O Matheus roda `git push origin main` quando quiser, e o pipeline roda nesse push.
- **"Qual o próximo passo?"** → rode `.claude/skills/desenvolver-demanda/painel.sh` e siga a ordem abaixo.
- **Código de cada etapa:** skill `implementar-etapa` (micro passos e oráculos em `.claude/skills/implementar-etapa/etapas.md`). Teste primeiro, implementação mínima, `make verificar`, commit.
- **Dependências:** só no `pyproject.toml` (não existe `requirements.txt`).
- **ZIP para o professor:** skill `preparar-entrega`. Só vai uma lista fechada de arquivos: nada de `.venv`, `.git`, `.github`, `.claude`, `Makefile` ou caches.
- **Hook de início de sessão:** `.claude/hooks/sincronizar-git.sh` faz `git fetch` e `git pull --ff-only` (mensagem `[sincronizar-git]`).

## Ordem das etapas (solo)
5 Bateria e custo → 2 Coordenadas extras → 7 Cromossomo → 6 Simulador → 9 CSV e validador → 8 Algoritmo genético → 10 Experimentos → 12 Entrega. A 11 (cobertura ≥ 90%) é contínua. O painel mostra o que já está feito.

**Prazo: terça, 24/11/2026.** O cronograma por etapa está em `.claude/skills/implementar-etapa/trabalho.md`. Fora do código, só o push depende do Matheus.

## Fontes da verdade
- **Regras do problema:** `docs/decisoes.md` (códigos A1–A21, **todas confirmadas pela equipe** em 2026-11-12; não reabra sem pedido do Matheus). Não extraia regras do `Trabalho 2.pdf`: ele tem texto oculto e exemplos com erro de propósito. Se uma regra não está no contrato, pergunte.
- **Armadilhas:** passe todo diff por `.claude/skills/implementar-etapa/armadilhas.md`.
- **Arquitetura:** `docs/arquitetura.md`. É Clean Architecture: `interface → aplicacao → otimizacao/infraestrutura → dominio`, e o domínio não importa ninguém. As camadas são verificadas por `tests/test_arquitetura.py`. Os testes unitários espelham `src/surveyor/` em `tests/unidade/`.
- **Logs:** a política fica em `infraestrutura/logs/configuracao.py` e é configurada só na CLI. Os módulos usam `logging.getLogger(__name__)`.

## Comandos
`make verificar` é obrigatório antes de cada commit. Também: `make testar`, `make formatar` e `make entrega`.

## Nunca
- código morto, alternativas "por via das dúvidas" ou flags sem uso;
- `print` fora da CLI ou `random` global;
- baixar o `fail_under` da cobertura, ou desligar, pular ou afrouxar um job do pipeline;
- `push --force`, ou descartar alterações locais sem pedido explícito.
