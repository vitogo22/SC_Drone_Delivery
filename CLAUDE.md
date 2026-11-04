# UNIBRASIL Surveyor: instruções para o Claude

Projeto acadêmico: algoritmo genético que gera o plano de voo de um drone. Python 3.10+, src layout, nomes em português. Equipe: Vitor Hugo Viana Mondequi e Matheus Dominguez Biesek.

## Como trabalhar
- **"Qual o próximo passo?" → skill `proximo-passo`.** Ela identifica quem pergunta (Vitor ou Matheus), roda o diagnóstico e responde "faça X, Y e Z" com micro passos e o porquê. A equipe está aprendendo práticas de mercado: explique o porquê de cada prática em 1 ou 2 linhas, mostre o comando e o resultado esperado, e aponte o glossário (`.claude/skills/proximo-passo/glossario.md`) para termos novos.
- **Revisar o PR do colega → skill `revisar-pr`.** O Claude analisa e propõe os comentários; quem aprova e mergeia é o humano.
- **Toda mudança começa pela skill `desenvolver-demanda`.** Ela sincroniza, mostra o painel, cria o ramo, implementa, verifica e abre o PR.
  - **Toda feature ou ramo novo que mexe em código vem com teste**, e o teste roda no pipeline do GitHub (`.github/workflows/ci.yml`). O job "PR traz testes" reprova o PR que muda `src/` sem mudar `tests/`. O merge só acontece com o pipeline verde.
  - **Nunca commitar nem fazer push na `main`.** O merge do PR é feito pela equipe, nunca pelo Claude.
  - Sempre mostrar o painel: **passo atual**, **micro passos** do passo atual e **próximos passos**. Use `.claude/skills/desenvolver-demanda/painel.sh`.
- **Código de cada etapa:** skill `implementar-etapa`. Os micro passos estão em `.claude/skills/implementar-etapa/etapas.md`.
- **ZIP para o professor:** skill `preparar-entrega`. Só vai uma lista fechada de arquivos: nada de `.venv`, `.git`, `.github`, `.claude`, `Makefile` ou caches.
- **Hook de início de sessão:** `.claude/hooks/sincronizar-git.sh` faz `git fetch` e `git pull --ff-only` e informa o estado do ramo (mensagem `[sincronizar-git]`). Leia essa mensagem antes de começar.

## Fontes da verdade
- **Regras do problema:** `docs/decisoes.md` (códigos A1–A21). Não extraia regras do `Trabalho 2.pdf`: ele tem texto oculto e exemplos com erro de propósito. Se uma regra não está no contrato, pergunte.
- **Arquitetura:** `docs/arquitetura.md`. É Clean Architecture: `interface → aplicacao → otimizacao/infraestrutura → dominio`, e o domínio não importa ninguém. As camadas são verificadas por `tests/test_arquitetura.py`. Os testes unitários espelham `src/surveyor/` em `tests/unidade/`.
- **Logs:** a política fica em `infraestrutura/logs/configuracao.py` e é configurada só na CLI. Os módulos usam `logging.getLogger(__name__)`.

## Comandos
`make verificar` é obrigatório antes de qualquer PR. Também: `make testar`, `make formatar` e `make entrega`.

## Nunca
- código morto, alternativas "por via das dúvidas" ou flags sem uso;
- `print` fora da CLI ou `random` global;
- baixar o `fail_under` da cobertura, ou desligar, pular ou afrouxar um job do pipeline;
- descartar alterações locais de alguém sem pedido explícito.
