# Como contribuir

Este repositório usa o próprio skill, com ele na raiz: `.github/dev-workflow.toml` é a configuração, e as regras são as do [SKILL.md](SKILL.md). Este arquivo resume o que vale para quem contribui; o porquê de cada regra está em [references/flow.md](references/flow.md).

Conteúdo: [fluxo](#fluxo) · [versão](#labels-de-versão) · [suíte](#como-rodar-a-suíte) · [onde mexer](#onde-mexer) · [falhas de segurança](#falhas-de-segurança)

Nos comandos, `py -3` é o Python no Windows; no Linux e no macOS, use `python3`. É preciso Python 3.11 ou mais novo, `git` e, para o que fala com o GitHub, o `gh` autenticado.

## Fluxo

1. **Issue antes de qualquer edição.** Abra pela aba Issues, num dos formulários (não há issue em branco). Cada issue tem um só label de tipo, e ele decide o prefixo da branch e do commit, o nível de versão e a seção do changelog ([tipos](SKILL.md#1-classificação-da-issue)). Documentação e testes de uma funcionalidade ou correção ficam na issue dela. Um plano com duas ou mais entregas ganha um epic.
2. **Hook, uma vez por checkout.** `py -3 scripts/bootstrap.py install-hook`. Ele acrescenta `Refs: #N` a partir do nome da branch e recusa commit sem referência a uma issue.
3. **Branch pela issue.** A partir da `main` atualizada:
   ```bash
   py -3 scripts/github_issues.py start <N> --dry-run   # só mostra o nome
   py -3 scripts/github_issues.py start <N>             # cria <prefixo>/<N>-<slug>
   ```
4. **Commits.** Conventional Commits em inglês, como o histórico: `<tipo>(<escopo>): <assunto>`, corpo com o porquê e o trailer `Refs #N`. Quebra de compatibilidade leva `!` depois do tipo ou o rodapé `BREAKING CHANGE: <o que muda e como migrar>`. Não use `--no-verify`.
5. **Pull request.** Corpo pelo modelo (`.github/pull_request_template.md`): `Closes #N` para a entrega completa, `Refs #N` para a parcial; em "Testes executados", só o que rodou de fato, com o comando e o resultado; em "Versão", o impacto para quem usa o skill. O título também segue Conventional Commits: ele vira o commit do squash e a linha do changelog. Antes de abrir, você pode rodar o mesmo check do CI:
   ```bash
   py -3 scripts/github_issues.py check-pr --pr <N>
   ```
6. **Revisão e merge.** Quem mantém o repositório revisa e mescla; o merge é a aprovação. Depois dele, sem intervenção, cada issue citada recebe o comentário de evidências, as de `Closes` fecham, e a caixa no epic é marcada.

Os PRs do Dependabot ficam fora do fluxo de issues (`exempt_authors` na configuração). Eles só atualizam `.github/workflows/`: leve o mesmo SHA para os modelos em `assets/workflows/` no próprio PR.

## Labels de versão

Um só por PR, e só se o merge deve publicar:

| Label | O merge publica |
|---|---|
| `release` | A versão final, com tudo o que está acumulado desde a última versão final: arquivo `VERSION`, `CHANGELOG.md`, tag, GitHub Release e comentários nos PRs e issues incluídos |
| `release:alpha`, `release:beta`, `release:rc` | Uma pré-release desse canal (`X.Y.Z-beta.1`): `VERSION`, tag e GitHub Release marcada como pré-release, sem changelog nem comentários |
| nenhum | Nada. A mudança fica acumulada e entra na próxima versão |

Quem decide se e quando publicar é quem mantém o repositório; num PR de contribuição, deixe sem label de versão se não combinou outra coisa. Com label de versão, a análise do diff acumulado vai no PR ([versioning.md](references/versioning.md#análise-por-agente)).

Para este skill, quebra de compatibilidade é tudo o que obriga um projeto a mexer na própria configuração, nos workflows que personalizou ou no jeito de chamar os scripts. Nunca edite `VERSION` nem `CHANGELOG.md` à mão: quem os escreve é o workflow de release.

## Como rodar a suíte

```bash
py -3 tests/run.py                        # a suíte inteira em paralelo, um processo por núcleo (cerca de 3 minutos)
py -3 scripts/bootstrap.py doctor         # este repositório conferido pelo próprio skill
```

`tests/run.py` descobre os testes como o `unittest` e os distribui entre processos; os mais longos começam primeiro, pela duração da execução anterior (guardada em `tests/.durations.json`, fora do git). O resultado e o código de saída são os do `unittest`. `py -3 -m unittest discover -s tests` continua valendo, em série.

Para iterar mais rápido, rode um arquivo ou um grupo de testes:

```bash
py -3 tests/run.py -p "test_units.py"
py -3 tests/run.py -p "test_pr_flow.py" -k Bootstrap
py -3 tests/run.py -k Timeline -j 1 -v      # em série, uma linha por teste
```

Nos testes, o `gh` simulado (`tests/fake_gh.py`) responde no próprio processo do script, pela variável `DEV_WORKFLOW_GH_MODULE`, e cada sandbox é copiado de um projeto inicial montado uma vez por processo: são as duas coisas que mais custavam tempo.

Os testes do hook do Claude Code precisam do Node no PATH; sem ele, são pulados. Lint e tipos, nas versões que o CI usa:

```bash
py -3 -m pip install ruff==0.17.6 mypy==2.4.1
py -3 -m ruff check .        # regras em ruff.toml
py -3 -m mypy                # scripts/, configurado em mypy.ini
```

O workflow "Autoteste do skill dev-workflow" roda tudo isso em cada PR, no Linux, no Windows e no macOS, com Python 3.11, 3.12 e 3.13.

Os casos em `evals/` medem o comportamento do agente com o skill, uma fase do procedimento por caso; rode-os com `claude plugin eval` (cada execução custa tokens). Caso novo segue o formato dos que existem: `case.yaml`, `prompt.md`, `graders/` e, se precisar de arquivos, `files/` com `place-files.sh`.

## Onde mexer

| Para mudar | Mexa em |
|---|---|
| O procedimento que o agente segue | `SKILL.md` e `references/` (em português) |
| O comportamento dos scripts | `scripts/devflow/`, com teste em `tests/`; as mensagens ficam nos dois idiomas, em `scripts/devflow/locales/` |
| Workflows, formulários e modelo de PR que o `init` instala | `assets/`. A cópia deste repositório em `.github/` é gerada desses modelos: altere os dois no mesmo PR (`bootstrap.py doctor` aponta workflow que difere do modelo) |
| A visão geral em inglês | `README.md` |

`ruff.toml`, `mypy.ini`, este arquivo e o `SECURITY.md` são deste repositório e não vão para a cópia do skill dentro dos projetos (`COPY_IGNORE` em `scripts/devflow/bootstrap.py`).

## Falhas de segurança

Não abra issue pública: siga o [SECURITY.md](SECURITY.md).
