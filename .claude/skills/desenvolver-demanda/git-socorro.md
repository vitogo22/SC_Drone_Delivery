# Socorro git: situações comuns e a saída segura

Antes de qualquer comando que pode perder trabalho (`reset`, `restore`, `clean`, `push --force`), **pergunte à pessoa** e mostre o que vai acontecer. O primeiro passo é sempre `git status` e `git log --oneline -5`.

| Situação | Saída segura |
|---|---|
| **Estou mexendo na `main` e esqueci de criar o ramo** (nada commitado ainda) | `git switch -c <ramo>`: as alterações vão junto para o ramo novo |
| **Commitei na `main` sem querer** (sem push) | 1. `git switch -c <ramo>`, que leva os commits para o ramo novo. 2. `git branch -f main origin/main`, que volta a `main` local ao GitHub sem tocar nos arquivos. 3. Seguir no ramo novo |
| **Tentei dar push na `main`** | Com a proteção ligada (V1), o GitHub recusa, e é para isso que ela existe. Faça como na linha acima e abra um PR |
| **O hook disse "git pull --ff-only falhou"** | Há alterações locais em conflito com o que chegou, ou um histórico divergente. Commite (no ramo certo) ou guarde com `git stash`, rode `git pull --ff-only` e depois `git stash pop` |
| **Conflito no rebase** | 1. `git status` mostra os arquivos em conflito. 2. Abra cada um, procure `<<<<<<<` e `>>>>>>>` e deixe o resultado com **as duas intenções**. 3. `git add <arquivo>`. 4. `git rebase --continue`. Para desistir: `git rebase --abort`, que volta como estava |
| **Conflito em `etapas.md`** | Alguém marcou outra seção. Mantenha as marcações dos dois e não desmarque nada |
| **O PR diz "This branch is out-of-date"** | `git fetch origin && git rebase origin/main`, depois `make verificar` e `git push --force-with-lease` (só no próprio ramo) |
| **Um check do pipeline ficou vermelho** | 1. No PR, aba Checks, ache o passo vermelho. 2. Reproduza com o mesmo comando localmente: `make lint`, `make tipos`, `make cobertura` ou `.github/scripts/exige-testes.sh origin/main HEAD`. 3. Corrija no ramo, commit e push |
| **"PR traz testes" falhou** | Falta teste para o código alterado: escreva o teste do comportamento. Teste vazio só para passar é proibido, e o revisor reprova |
| **Mensagem de commit errada** (sem push) | `git commit --amend -m "mensagem certa"` |
| **Esqueci um arquivo no último commit** (sem push) | `git add <arquivo> && git commit --amend --no-edit` |
| **Quero desfazer um commit que já está no GitHub** | Nunca reescreva a `main`. No ramo: `git revert <hash>`, que cria um commit desfazendo, e depois push |
| **Quero jogar fora as minhas mudanças num arquivo** | `git restore <arquivo>`. **Perde o trabalho:** confirme com a pessoa antes |
| **Estou num "detached HEAD"** | `git switch <ramo>`. Se fez commits ali, antes rode `git switch -c <ramo-novo>` para não perdê-los |
| **Não sei em que ramo estou nem o que mudei** | `git status`, `git branch --show-current` e `.claude/skills/desenvolver-demanda/painel.sh` |
