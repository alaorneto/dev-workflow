"""Português do Brasil: o idioma de referência. Toda chave de mensagem existe aqui."""

from __future__ import annotations

from typing import Any

_COMMON_SECTIONS = [
    "Contexto",
    "Objetivo",
    "Escopo",
    "Abordagem técnica",
    "Critérios de aceite",
    "Plano de testes",
    "Documentação a atualizar",
    "Riscos e dependências",
    "Definição de pronto",
]

DEFAULTS: dict[str, Any] = {
    "types": {
        "bug": {"description": "Comportamento incorreto ou regressão"},
        "feature": {"description": "Nova funcionalidade"},
        "enhancement": {"description": "Melhoria de funcionalidade existente"},
        "documentation": {"description": "Somente documentação"},
        "refactor": {"description": "Reestruturação sem mudança de comportamento"},
        "test": {"description": "Somente testes, fixtures ou evidência de verificação"},
        "ci": {"description": "Pipeline e checks automáticos"},
        "chore": {"description": "Dependências, ferramentas e configuração de desenvolvimento"},
    },
    "issues": {
        "items_section": "Itens",
        "depends_marker": "depende de",
        "acceptance_section": "Critérios de aceite",
        "sections": {
            "default": _COMMON_SECTIONS,
            "bug": [
                "Comportamento observado",
                "Comportamento esperado",
                "Passos para reproduzir",
                *_COMMON_SECTIONS[2:],
            ],
            "documentation": ["Contexto", "Objetivo", "Critérios de aceite", "Definição de pronto"],
        },
    },
    "pr": {
        "required_sections": ["Issues", "Resumo", "Testes executados", "Documentação", "Versão"],
        "version_section": "Versão",
        "tests_section": "Testes executados",
        "docs_section": "Documentação",
        "override_reason_marker": "Motivo da sobreposição",
    },
    "changelog": {
        "intro": (
            "Todas as mudanças publicadas deste projeto. Este arquivo é escrito pela automação de release; "
            "não edite as seções de versão à mão."
        ),
        "sections": [
            {"id": "breaking", "title": "⚠ Mudanças incompatíveis"},
            {"id": "features", "title": "Funcionalidades"},
            {"id": "improvements", "title": "Melhorias"},
            {"id": "fixes", "title": "Correções"},
            {"id": "docs", "title": "Documentação"},
            {"id": "maintenance", "title": "Manutenção"},
        ],
    },
}

MESSAGES: dict[str, str] = {
    # --- configuração --------------------------------------------------------------------------
    "config.language.unknown": "não é um idioma aceito; use um de {accepted}.",
    "config.prerelease.table": "deve ser uma tabela (`[versioning.prerelease]`) com a lista `channels`.",
    "config.channels.type": 'deve ser uma lista de textos, por exemplo `["alpha", "beta", "rc"]`.',
    "config.channels.name": (
        "tem o canal `{channel}`, que não é um nome válido: use minúsculas, começando por letra "
        "(letras, dígitos e hífen)."
    ),
    "config.channels.order": (
        "deve ir do canal menos maduro ao mais maduro, na ordem de precedência do SemVer, que é alfabética (ASCII): "
        "`{later}` não vem depois de `{earlier}`. É essa a ordem que os gerenciadores de pacote aplicam."
    ),
    "config.channels.pep440": (
        "tem o canal `{channel}`, que não tem forma PEP 440, e `versioning.files` usa um marcador `_pep440`. "
        "Canais com forma PEP 440: {accepted}."
    ),
    "config.channels.pep440_clash": (
        "tem `{first}` e `{second}`, que viram a mesma forma PEP 440 (`{form}`); deixe só um deles."
    ),
    "config.prerelease_prefix.empty": "deve ser um texto não vazio, por exemplo `release:`.",
    "config.prerelease_prefix.clash": (
        "gera o label `{label}` para o canal `{channel}`, que já é outro label do fluxo; mude o prefixo."
    ),
    # --- plano de versão -----------------------------------------------------------------------
    "plan.cycle.target_changed": (
        "O alvo do ciclo mudou de {old} para {new}: o acumulado agora pede mais do que {tag} previa, "
        "e a numeração dos canais recomeça em {new}."
    ),
    "plan.request.unknown_label": (
        "O label `{label}` em {change} não é um canal de pré-release deste projeto ({accepted}) e não pede versão."
    ),
    "plan.request.manual_prerelease": (
        "A execução manual pede a pré-release `{channel}` e vence os labels nesta execução; "
        "pedidos dos PRs novos: {asked}."
    ),
    "plan.request.manual_final": (
        "A execução manual pede a versão final e vence os labels nesta execução; pedidos dos PRs novos: {asked}."
    ),
    "plan.request.most_mature": "Vence o pedido mais maduro: {winner}. Também pediram versão: {others}.",
    "plan.request.promoted": (
        "O label `{label}` pede um canal anterior a `{current}`, que o ciclo de {core} já publicou ({tag}): "
        "a pré-release sai em `{current}`, porque o canal não regride."
    ),
    "plan.prerelease.nothing_new": (
        "Nada novo desde {tag}: outra pré-release `{channel}` sairia igual a ela. Para promover, peça um canal "
        "mais maduro; para a versão final, rode com `--force`."
    ),
    "plan.cycle.floor": (
        "O ciclo em andamento já publicou {tag}: a versão não desce, e o alvo fica em {floor} "
        "(o cálculo daria {target})."
    ),
    "plan.cycle.override_below": (
        "A sobreposição pede {target}, abaixo de {floor}, que o ciclo em andamento já publicou em pré-release "
        "({tag}). Uma versão não regride: retire a sobreposição ou use um nível que alcance {floor}."
    ),
    "plan.channel.regressed": (
        "O canal `{channel}` é anterior a `{current}`, que o ciclo de {core} já publicou ({tag}). "
        "Uma pré-release não regride de canal: use `{current}` ou um canal mais maduro."
    ),
    "plan.core.taken": (
        "A versão {core} já tem tag em outra linha ({tags}), fora do alcance desta branch. "
        "Duas linhas não publicam o mesmo número: confira a branch e o nível calculado."
    ),
    # --- release -------------------------------------------------------------------------------
    "release.channel.unknown": (
        "Canal de pré-release `{channel}` fora da lista do projeto. "
        "Canais aceitos (`versioning.prerelease.channels`): {accepted}."
    ),
    "release.channel.none": "Este projeto não aceita pré-releases: `versioning.prerelease.channels` está vazio.",
    "release.beginning": "o início",
    "release.nothing": (
        "Nada a versionar: {count} mudança(s) acumulada(s) desde {base}, nenhuma em PR com label de versão ({labels})."
    ),
    "release.nothing.cycle": (
        "Nada a versionar: {count} mudança(s) acumulada(s) desde {base}, {fresh} depois de {previous}; "
        "nenhuma destas em PR com label de versão ({labels})."
    ),
    "release.manual.answered": (
        "O pedido desta execução manual foi atendido por {tag}, que acabou de ser publicada; "
        "nada entrou depois dela."
    ),
    "report.cycle": "Ciclo de pré-releases em andamento: {cycle}. Versão corrente: {current}.",
    # --- notas da versão -----------------------------------------------------------------------
    "notes.news.title": "Novidades desde {previous}",
    "notes.news.none": (
        "Nada novo desde {previous}: esta versão leva o mesmo conteúdo ao canal `{channel}`."
    ),
    "notes.accumulated.title": "Acumulado desde {base}",
    # --- prévia e check do pedido de versão ----------------------------------------------------
    "preview.prerelease.title": "### Prévia de versão: ao mesclar, este PR publica a pré-release **{tag}** ({level})",
    "preview.prerelease.body": (
        "Entram nela este PR e {others} mudança(s) já acumulada(s) desde {base}. É uma versão de teste do canal "
        "`{channel}`: o changelog e os comentários nas issues ficam para a versão final, pedida com `{release}`."
    ),
    "preview.prerelease.news": (
        "Novidade desde {previous}: este PR e {fresh} mudança(s) que ainda não saíram em pré-release."
    ),
    "preview.final.closes_cycle": (
        "Ela encerra o ciclo de pré-releases em andamento ({cycle}): cobre tudo desde {base}, e é nela que saem "
        "o changelog e os comentários nas issues."
    ),
    "preview.pending.title": "### Prévia de versão: este PR não pede versão, mas entra em **{tag}** ({level})",
    "preview.pending.body": (
        "Há pedido de versão ainda não atendido ({asked}): **{tag}** ainda não saiu, e este PR entra nela ao ser "
        "mesclado. Se não é essa a intenção, espere a versão sair antes de mesclar, ou retire o label de quem pediu."
    ),
    "preview.none.channels": "Com um label de canal ({labels}), publicaria uma pré-release desse número.",
    "check.version_labels.many": (
        "Mais de um label de versão ({labels}); deixe só um: `{release}` publica a versão final, e cada label de "
        "canal, uma pré-release."
    ),
    "check.version_labels.unknown": (
        "O label `{label}` não é um canal de pré-release deste projeto ({accepted}): ele não pede versão."
    ),
    "evidence.version.prerelease": (
        "**Versão:** o PR pede uma pré-release do canal `{channel}`. A versão final, com o changelog, sai depois; "
        "a automação de release comenta aqui quando ela sair."
    ),
    "check.request.none": "PR #{pr} sem label de versão: ele não pede versão, nada a conferir.",
    "check.request.ok": "PR #{pr}: o pedido `{label}` pode ser publicado ({tag}).",
    "check.request.inherited": (
        "PR #{pr}: o pedido `{label}` esbarra em {count} problema(s) que já existem sem este PR (acima). O check "
        "não o reprova por eles, mas a release para até serem resolvidos."
    ),
    "check.request.analysis": (
        "PR #{pr}: o pedido `{label}` aguarda a análise de versão (aviso acima). O check não reprova por isso, "
        "porque registrar a análise não o dispara de novo; a release para até ela ser registrada."
    ),
    "check.request.refused": (
        "PR #{pr}: o pedido `{label}` não pode ser publicado ({count} problema(s) acima). Corrija ou retire o label."
    ),
    # === issues.py, text.py, epics.py (#37): as chaves deste módulo ====================================
    # (fim de issues)
    # === config.py, semver.py, gh.py, plan.py (#38): as chaves deste módulo ==============================
    # (fim de plan)
    # === release.py (#39): as chaves deste módulo =====================================================
    # --- execução: mensagens de quem opera -------------------------------------------------------
    "release.error": "ERRO: {text}",
    "release.warning": "aviso: {text}",
    "release.push.refused": (
        "o push do commit de release para `{branch}` foi recusado pelo GitHub (proteção de branch ou permissão "
        "do token), não porque a branch andou: {detail}\n"
        "Duas saídas: `release.mode = \"pull-request\"` na configuração, para a release chegar à branch por um PR; "
        "ou um segredo `RELEASE_TOKEN` com permissão de escrever nela (por exemplo, de quem pode passar pela "
        "proteção). Nada foi publicado; rode de novo depois de ajustar."
    ),
    "release.push.moved": "A branch remota avançou durante a release; recalculando.",
    "release.unstable": "a release não estabilizou; rode de novo e confira o estado da branch.",
    "release.analysis.missing": "o arquivo de análise `{path}` não existe.",
    "release.analysis.encoding": "o arquivo de análise `{path}` não está em UTF-8.",
    "release.analysis.unreadable": "não consegui ler o arquivo de análise `{path}`: {error}.",
    "release.analysis.invalid": "o arquivo de análise `{path}` não é JSON válido: {error}.",
    "release.analysis.refused": "Análise inválida: {error}",
    "release.analysis.head_filled": (
        "A análise não diz o `head` analisado; registrada para a ponta atual do PR ({sha})."
    ),
    "release.analysis.no_head": "Aviso: a análise não diz o `head` analisado; ela não vai contar na release.",
    "release.analysis.recorded": "Análise gravada no PR #{pr}: nível {level}, {count} mudança(s).",
    "release.files.count": (
        "{path}: esperava {expected} ocorrência(s) de `{needle}`, encontrei {found}. "
        "O arquivo divergiu da versão corrente ou o padrão em `versioning.files` está errado."
    ),
    "release.files.count_regex": "{path}: esperava {expected} ocorrência(s) de /{regex}/, encontrei {found}.",
    "release.files.encoding": "{path}: não está em UTF-8; converta o arquivo (a versão é escrita em UTF-8).",
    "release.files.unreadable": "{path}: não consegui ler ({error}).",
    "release.files.drift": "{path}: o conteúdo não corresponde à versão {version}.",
    "release.forged.merge": "chegou pelo merge {sha}, que não é do PR de release (`{branch}` deste repositório)",
    "release.forged.not_pr": "chegou pelo merge {sha}, que não é de um PR",
    "release.forged.other_pr": "chegou pelo PR #{number}, que não é o PR de release (`{branch}` deste repositório)",
    "release.forged.ignored": "Commit de release {sha} ({tag}) ignorado: {reason}. Nenhuma versão sai dele.",
    "release.mark.failed": "não consegui marcar #{number}: {error}",
    "release.tag.created": "Tag {tag} criada em {sha}.",
    "release.github.created": "GitHub Release {tag} criada.",
    "release.dispatch.done": "Workflow {workflow} disparado para {tag}.",
    "release.dispatch.failed": "não consegui disparar {workflow}: {error}",
    "release.pr.updated": "PR de release #{number} atualizado para {tag}.",
    "release.pr.opened": "PR de release #{number} aberto para {tag}.",
    "release.reconcile": "A tag {tag} não tem GitHub Release; concluindo a publicação.",
    "release.disabled": "Versionamento desligado em dev-workflow.toml (`versioning.enabled = false`).",
    "release.branch.not_release": "A branch `{branch}` não publica versões (veja `repository.release_branches`).",
    "release.branch.release_pr": (
        "A branch `{branch}` é a do PR de release (`release.pr_branch`): a versão sai quando esse PR é "
        "mesclado, não daqui."
    ),
    "release.override.no_reason": "(motivo não informado)",
    "release.override.manual": "execução manual",
    "release.prepared.publishing": "Commit de release de {tag} sem tag; publicando.",
    "release.preview.no_tag": "Sem tag de versão alcançável: a prévia começa depois de `release.py baseline`.",
    "release.preview.comment_failed": "não consegui comentar a prévia no PR: {error}",
    "release.baseline.exists": "O repositório já tem tags de versão; a tag de base não é necessária.",
    "release.baseline.message": (
        "Linha de base do versionamento automático: o que veio antes desta tag é a versão {version}."
    ),
    "release.baseline.created": "Tag de base {tag} criada em {sha}.",
    "release.baseline.pushed": "Tag enviada ao remoto.",
    "release.check.no_tree": "--tree {tree} não é um diretório.",
    "release.check.pr_tip": ", a maior alcançável da ponta do PR",
    "release.check.initial": "versioning.initial_version (ainda não há tag)",
    "release.check.prepared": (
        "PR de release ({tag}): {count} entrada(s) de arquivo coerentes com a versão {version}, que ele publica."
    ),
    "release.check.ok": "{count} entrada(s) de arquivo coerentes com a versão {version} ({origin}).",
    "release.bump.none": "Nenhum arquivo mudou.",
    "release.level.invalid": "Nível inválido: {level}.",
    "release.cli.description": "Versionamento semântico do projeto.",
    "release.cli.pr": "inclui um PR aberto como se estivesse mesclado",
    "release.cli.base_ref": "com --pr: a branch de destino (padrão: origin/<branch padrão>)",
    "release.cli.head_ref": "com --pr: a ponta do PR",
    "release.cli.tree": "confere os arquivos de outra árvore (checkout do PR), com a configuração desta",
    "release.cli.check": "não comenta: falha se o pedido de versão deste PR não pode ser publicado",
    "release.cli.force": "publica o acumulado mesmo sem PR marcado",
    "release.cli.prerelease": "canal de pré-release, por exemplo rc; implica --force",
    # --- relatório do plano (`release.py plan`, `run`) -----------------------------------------
    "release.report.nothing": "Nada acumulado desde {base}.",
    "release.report.next.title": "### Próxima versão: **{tag}** ({level}) — {state}",
    "release.report.next.will": "será publicada",
    "release.report.next.would": "seria publicada (nenhum PR pediu versão ainda)",
    "release.report.requested_by": "Versão pedida por: {changes}.",
    "release.report.problems": "**Problemas que impedem a release**",
    # (fim de release)
    # === bootstrap.py (#40): as chaves deste módulo =================================================
    # (fim de bootstrap)
    # --- labels (o GitHub limita a descrição a 100 caracteres) ----------------------------------
    "label.prerelease": "O merge publica uma pré-release {channel} com tudo que está acumulado",
    "label.epic": "Acompanhamento de um plano com várias issues",
    "label.release": "O merge publica uma versão com tudo que está acumulado; sem este label, o PR fica acumulado",
    "label.breaking": "Quebra de compatibilidade para quem usa o projeto",
    "label.override": "Sobrepõe o nível calculado: {level} ({meaning})",
    "label.override.major": "incompatível",
    "label.override.minor": "funcionalidade",
    "label.override.patch": "correção",
}
