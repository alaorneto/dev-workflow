# Segurança

O skill roda no CI de outros projetos, com token de escrita em alguns workflows. Este arquivo diz como reportar uma falha e o que exatamente ele executa, com quais permissões, para quem adota ou revisa.

Conteúdo: [reportar](#como-reportar-uma-falha) · [versões](#versões-que-recebem-correção) · [CI](#o-que-o-skill-executa-no-ci) · [máquina local](#o-que-roda-na-máquina-de-quem-desenvolve) · [segredos](#segredos) · [para revisar](#o-que-conferir-ao-adotar)

## Como reportar uma falha

Não abra issue pública nem PR com o problema. Use o reporte privado do GitHub: aba **Security** do repositório → **Report a vulnerability** ([link direto](https://github.com/alaorneto/dev-workflow/security/advisories/new)). O relato fica visível só para quem mantém o repositório.

Inclua:

- a versão do skill (`python3 scripts/bootstrap.py version`, ou o arquivo `VERSION` da cópia);
- o workflow ou script afetado e o gatilho (evento, label, entrada do disparo manual);
- os passos para reproduzir e o que um atacante obtém (escrita no repositório, segredo exposto, release forjada);
- se já viu isso explorado.

A conversa continua no próprio advisory. A correção sai numa versão nova do skill, pelo fluxo normal de release, e o advisory é publicado depois dela, com a versão que corrige.

Se o botão **Report a vulnerability** não aparecer, abra uma issue pedindo um canal privado, sem nenhum detalhe da falha.

## Versões que recebem correção

Só a última versão publicada (arquivo `VERSION` e [Releases](https://github.com/alaorneto/dev-workflow/releases)). Um projeto recebe a correção atualizando a cópia: `python3 <skill-novo>/scripts/bootstrap.py update`, rodado a partir da versão nova ([installation.md](references/installation.md)).

## O que o skill executa no CI

Todos os workflows rodam os scripts da cópia versionada do skill no projeto (`.claude/skills/dev-workflow/`, ou a raiz neste repositório): Python 3.11+ só com a biblioteca padrão, `git` e `gh`. Nenhum instala dependência, exceto os dois casos marcados na tabela. As actions de terceiros são fixadas por SHA: `actions/checkout`, `actions/setup-python`, `actions/setup-node` e `anthropics/claude-code-action`. Cada workflow declara as permissões de que precisa; o padrão "Read" em "Settings → Actions → General → Workflow permissions" basta.

| Workflow | Gatilho | Permissões do `GITHUB_TOKEN` | O que roda | Código do PR |
|---|---|---|---|---|
| `pr-check.yml` (Verificação do PR) | `pull_request`; também na fila de merge (`merge_group`) | Workflow: `contents: read`. Job "Verificação do PR": `contents: read`, `issues: read`, `pull-requests: read`. Job "Prévia da versão": `contents: read`, `issues: write`, `pull-requests: write` | `github_issues.py check-pr`, `release.py check --tree .pr-head`, `release.py preview` (`--check` e `--comment`) | Nunca executado. Os scripts e a configuração vêm da branch base; o PR é baixado em `.pr-head` só para leitura, com `persist-credentials: false`. A prévia, que escreve um comentário, só roda para PR do próprio repositório |
| `pr-merged.yml` (Evidências do PR mesclado) | `pull_request_target`, `closed`, só se mesclado | `contents: read`, `issues: write`, `pull-requests: write` | `github_issues.py pr-merged`: comenta as evidências nas issues citadas | Nunca baixado: o checkout é o da branch de destino, padrão desse gatilho |
| `release.yml` (Versão e release) | `push` na branch padrão e em `release/**`; `workflow_dispatch` | `contents: write` (commit de release, tag, GitHub Release), `issues: write` (comentário e milestone), `pull-requests: write` (comentário nos PRs; PR de release no modo `pull-request`). `actions: write` só é pedido quando `release.dispatch_workflow` está configurado, para disparar o workflow de publicação | `release.py run` | O código já mesclado na branch. As entradas do disparo manual entram por variável de ambiente, nunca interpoladas no script. Com o segredo `RELEASE_TOKEN`, o checkout e o `gh` usam esse token no lugar do `GITHUB_TOKEN` |
| `epic-checklist.yml` (Caixas do epic) | `issues`, `closed` e `reopened` | `contents: read`, `issues: write` | `github_issues.py sync-checklist` e `close-epic`: marca a caixa da filha no epic e fecha o epic ao fechar a última | Não há PR. O número da issue entra por variável de ambiente |
| `semver-analysis.yml` (Análise de versão por agente, opcional) | `pull_request`, `labeled` e `synchronize`, só com label de versão e só para PR do próprio repositório | `contents: read`, `issues: read`, `pull-requests: write` | `release.py plan`; o Claude Code (`anthropics/claude-code-action`) lê o diff e grava `semver-analysis.json`; `release.py record-analysis` comenta no PR. Os passos são pulados sem `ANTHROPIC_API_KEY` ou `CLAUDE_CODE_OAUTH_TOKEN` | Scripts da base, com `persist-credentials: false`. O diff é lido por um modelo: o agente só tem `Read`, `Grep`, `Glob`, `Write` e `git diff`/`log`/`show`, o prompt manda tratar o diff como dado, o agente tem no máximo 40 turnos, o arquivo é validado antes de virar comentário por uma cópia dos scripts e da configuração feita antes de o agente rodar (somente leitura, executada com `python3 -I` fora do workspace: nada que o agente escreva é executado), e a análise só eleva o nível, nunca o reduz |
| `dev-workflow-selftest.yml` (Autoteste, opcional, `init --selftest`) | `pull_request` e `push` que tocam o skill | `contents: read` | A suíte do skill (`unittest`) com Python 3.11 a 3.13 e Node. No repositório do skill, instala do PyPI `ruff` e `mypy` em versões fixas para o lint e os tipos | Executado, só com permissão de leitura e sem usar segredos |

Todo job tem `timeout-minutes` (10 minutos; 20 na release e na análise; 30 no autoteste). Release, evidências e caixas do epic usam `concurrency` sem cancelar uma execução em andamento, para que duas escritas não se cruzem.

## O que roda na máquina de quem desenvolve

| O quê | Quando | O que faz |
|---|---|---|
| Hook `commit-msg` (`bootstrap.py install-hook` ou `pre-commit`) | Todo commit | `github_issues.py commit-msg`: lê o nome da branch, acrescenta `Refs: #N` à mensagem e recusa commit sem referência. Não acessa a rede |
| Hooks do Claude Code (opcional, Node) | Pedido do usuário, `EnterPlanMode`, `ExitPlanMode`, comandos de shell | Lê a entrada do hook, roda só `git` (para ler o estado do repositório) e devolve lembretes; recusa `git commit --no-verify`, commit sem o hook instalado e PR sem `Closes`/`Refs #N`. Falha interna nunca bloqueia |
| Scripts (`bootstrap.py`, `github_issues.py`, `release.py`) | Quando você ou o agente os chamam | `git` e `gh` com a autenticação que já existe na máquina. Os scripts não leem nem guardam token: quem autentica é o `gh` |

## Segredos

Nenhum é obrigatório.

| Segredo | Usado por | Escopo mínimo |
|---|---|---|
| `RELEASE_TOKEN` | `release.yml` | Fine-grained PAT ou GitHub App com escrita em conteúdo (e em PRs no modo `pull-request`), de quem pode ignorar a proteção da branch. Serve para escrever em branch protegida e para a tag disparar outros workflows |
| `ANTHROPIC_API_KEY` ou `CLAUDE_CODE_OAUTH_TOKEN` | `semver-analysis.yml` | Só a análise por agente. PR de fork não recebe segredos e fica fora do job |

## O que conferir ao adotar

- Os workflows gerados pelo `init` são iguais aos modelos (`bootstrap.py doctor` aponta o que difere); um workflow personalizado deixa de receber as correções do `update`.
- "Verificação do PR" como check obrigatório e a proteção da branch padrão ([installation.md](references/installation.md#4-passos-de-quem-é-dono-do-repositório-uma-vez)).
- `RELEASE_TOKEN`, se existir, com o menor escopo que o modo de release pede.
