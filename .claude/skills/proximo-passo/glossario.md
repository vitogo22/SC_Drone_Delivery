# Glossário de práticas de mercado (o que é e por que a equipe usa)

| Termo | O que é | Por que importa aqui |
|---|---|---|
| **Ramo (branch)** | Linha de trabalho separada da `main` | Cada um trabalha sem quebrar o código do outro |
| **Pull Request (PR)** | Pedido para juntar um ramo na `main`, com descrição, revisão e checks | Toda mudança é vista por outra pessoa antes de entrar |
| **Code review** | Leitura crítica do PR por outro integrante | Pega erro cedo e espalha o conhecimento do código; é o "peer-review" do enunciado |
| **Branch protection** | Regras do GitHub que bloqueiam o merge na `main` sem PR, aprovação e checks verdes | Garante que nada vermelho entra, inclusive por engano |
| **CI / pipeline** | Automação que roda lint, tipos e testes a cada PR (`.github/workflows/ci.yml`) | Ninguém precisa lembrar de testar: o GitHub testa sempre, no Linux |
| **Check (status check)** | Cada job do pipeline, com resultado verde ou vermelho no PR | São os 4 itens que a proteção da `main` exige |
| **TDD (teste primeiro)** | Escrever o teste do comportamento antes do código | O teste prova o requisito e vira documentação viva; a cobertura é 20% da nota |
| **Oráculo de teste** | Valor esperado conhecido de antemão (ex.: 41,0026532396 km/h no exemplo do vento) | Um teste com oráculo pega erro de fórmula na hora |
| **Cobertura** | Percentual do código executado pelos testes | O pipeline exige ≥ 90%; não se ganha cobertura com teste vazio |
| **Lint / formatação** | Verificação automática de estilo e de erros comuns (ruff) | O código da equipe fica com uma cara só; isso é avaliado em "boas práticas" |
| **Type checking** | Conferência dos tipos sem executar o código (mypy strict) | Pega um `str` passado onde se espera `int` antes de rodar |
| **Commit atômico** | Um commit = uma mudança completa e coerente (código + teste) | Fica fácil revisar, entender e, se preciso, desfazer |
| **Squash and merge** | Juntar o PR na `main` como um único commit | O histórico da `main` fica com um commit por demanda |
| **Rebase** | Reaplicar os commits do seu ramo em cima da `main` atual | Mantém o ramo em dia e resolve conflito antes do PR |
| **Conflito** | O git não sabe juntar duas mudanças na mesma linha | Resolve-se mantendo as duas intenções; ver `desenvolver-demanda/git-socorro.md` |
| **Definition of Done** | Critério de "pronto": testes verdes, pipeline verde, revisão aprovada, docs atualizadas | Evita o "está quase pronto"; aqui é o fechamento de cada etapa |
| **Clean Architecture** | Camadas com dependência sempre para dentro (interface → aplicação → domínio) | As regras do problema ficam isoladas e fáceis de testar; `docs/arquitetura.md` |
| **Contrato (ADR)** | Registro das decisões e do porquê (`docs/decisoes.md`) | Quando o professor perguntar "por que assim?", a resposta está escrita |
