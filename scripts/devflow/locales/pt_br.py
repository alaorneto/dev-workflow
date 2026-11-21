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
    # hook commit-msg
    "issues.commit_msg.added": "commit-msg: 'Refs: #{issue}' acrescentado a partir da branch {branch}.",
    "issues.commit_msg.missing": (
        "commit-msg: o commit precisa referenciar uma issue do GitHub.\n"
        "  Acrescente um trailer 'Refs #N' (ou trabalhe numa branch <prefixo>/<N>-<slug>, com o prefixo de um\n"
        "  tipo: {prefixes}). O sufixo '(#N)' e 'outro/repo#N' não contam.\n"
        "  Sem issue? Crie uma antes: veja o skill dev-workflow."
    ),
    # check-pr
    "check.links.none": (
        "O corpo do PR não referencia issue: use `Closes #N` (entrega completa) ou `Refs #N` (parcial)."
    ),
    "check.links.missing": "#{number} não existe em {repository}.",
    "check.links.pull_request": "#{number} é um pull request, não uma issue.",
    "check.links.type": "#{number} precisa de exatamente um label de tipo ({types}); encontrado: {found}.",
    "check.links.no_type": "nenhum",
    "check.links.only_epics": "O PR referencia apenas epics; cite a issue filha entregue (`Closes #N`).",
    "check.exempt.author": "PR de {author}: isento do fluxo de issues.",
    "check.exempt.release": "PR de release gerado pela automação: isento.",
    "check.closing_list": (
        "#{number} está numa lista de fechamento (`Closes #A, #{number}`), mas o GitHub só fecha a primeira "
        "issue da lista: repita a palavra-chave (`Closes #{number}`) ou use `Refs #{number}` se a entrega "
        "é parcial."
    ),
    "check.section.missing": "Falta a seção `## {name}` no corpo do PR (use o modelo de PR).",
    "check.section.empty": "A seção `## {name}` está vazia: preencha ou escreva `Não se aplica — motivo`.",
    "check.override.many": "Mais de um label de sobreposição ({levels}); deixe só um.",
    "check.override.level": "`{label}` não é major, minor nem patch.",
    "check.override.channels": " ou com um label de canal ({labels})",
    "check.override.needs_release": (
        "`{label}` só vale em PR marcado com `{release}`{also}: a sobreposição "
        "decide o número da versão que este PR publica."
    ),
    "check.override.reason": (
        "Sobreposição de versão sem motivo: escreva `{marker}: <motivo>` na seção `## {section}`."
    ),
    "check.forged.title": (
        "O título `{subject}` tem o formato do commit de release, que só a automação cria: ele não "
        "publica versão e some do changelog. Troque o texto; para publicar, use o label `{release}`."
    ),
    "check.forged.commit": (
        "O commit `{subject}` tem o formato do commit de release, que só a automação cria: ele não "
        "publica versão e some do changelog. Troque o texto; para publicar, use o label `{release}`."
    ),
    "check.title": (
        "O título `{title}` não segue Conventional Commits (`<tipo>(<escopo>): <assunto>`); ele vira o commit "
        "de um squash e entra no changelog."
    ),
    "check.issue.sections": "#{number} está sem as seções do modelo: {missing} (use `Não se aplica — motivo`).",
    "check.issue.criteria": (
        "#{number} tem {pending} de {total} critérios de aceite sem marcar; marque os "
        "verificados ou registre a dispensa na issue antes do merge."
    ),
    "check.type_mismatch": (
        "O título usa `{type}`, mas as issues vinculadas são de tipo {types} "
        "(prefixos esperados: {prefixes}). Confira a classificação."
    ),
    "check.annotation.title": "Verificação do PR",
    "check.annotation.error": "ERRO",
    "check.annotation.warning": "aviso",
    "check.usage": "uso: github_issues.py check-pr --pr N (ou PR_NUMBER), com GITHUB_REPOSITORY ou `gh` autenticado",
    "check.channels.none": "—",
    "check.pr.not_found": "PR #{number} não encontrado em {repository}.",
    "check.done": "PR #{number} verificado: {count} aviso(s).",
    # comentário de evidências (pr-merged)
    "evidence.delivered.by": "**Entregue pelo PR #{number}**, mesclado por @{merged_by}.",
    "evidence.delivered": "**Entregue pelo PR #{number}.**",
    "evidence.partial": (
        "**Entrega parcial pelo PR #{number}** (o PR cita esta issue com `Refs`; ela continua aberta)."
    ),
    "evidence.commits": "**Commits**",
    "evidence.commits.unreadable": "- (a lista de commits não pôde ser lida; veja o PR)",
    "evidence.tests": "Testes executados",
    "evidence.docs": "Documentação",
    "evidence.declared": "**{label}** (declarado no PR)",
    "evidence.not_stated": "- Não informado no PR.",
    "evidence.criteria.none": "**Critérios de aceite:** a issue não tem lista de critérios.",
    "evidence.criteria.pending": "**Critérios de aceite:** {pending} de {total} sem marcar no momento do merge:",
    "evidence.criteria.pending_hint": "Marque-os se foram verificados, ou reabra a issue e registre o que falta.",
    "evidence.criteria.done": "**Critérios de aceite:** os {total} marcados.",
    "evidence.version.release": (
        "**Versão:** o PR está marcado para versionar; a automação de release comenta aqui quando a versão sair."
    ),
    "evidence.version.none": (
        "**Versão:** o PR não gera versão; esta entrega fica acumulada e entra na próxima versão publicada."
    ),
    "issues.merged.not_found": "PR #{number} não encontrado.",
    "issues.merged.not_merged": "PR #{number} não foi mesclado; nada a registrar.",
    "issues.merged.already": "#{issue}: evidências do PR #{number} já registradas.",
    "issues.merged.recorded": "#{issue}: evidências do PR #{number} registradas.",
    # start e sync-labels
    "issues.start.untyped": (
        "#{number} precisa de exatamente um label de tipo ({types}) antes de virar branch."
    ),
    "issues.start.not_issue": "#{number} não é uma issue de {repository}.",
    "issues.start.dirty": (
        "A árvore de trabalho tem mudanças: commit, descarte ou use outro worktree antes de trocar de branch."
    ),
    "issues.start.exists": "A branch {name} já existe; trocado para ela.",
    "issues.start.created": "Branch {name} criada a partir de {base}.",
    "issues.labels.ok": "label {name} ok",
    "issues.labels.failed": "label {name} ERRO: {error}",
    # linha de comando
    "issues.cli.not_a_number": "`{value}` não é um número de issue",
    "issues.cli.description": (
        "Issues, PRs e epics do fluxo dev-workflow. Saída: 0 ok, 1 falha, 2 uso ou configuração."
    ),
    "issues.cli.command": "comando",
    "issues.cli.commit_msg": "hook do git: exige referência a uma issue na mensagem",
    "issues.cli.commit_msg.file_metavar": "ARQUIVO",
    "issues.cli.commit_msg.file": "o arquivo da mensagem que o git passa ao hook",
    "issues.cli.check_pr": "a verificação do PR (vínculo, seções, labels, título)",
    "issues.cli.pr": "número do PR (padrão: PR_NUMBER)",
    "issues.cli.pr_merged": "comenta as evidências do PR mesclado nas issues citadas",
    "issues.cli.start": "cria (ou troca para) a branch <prefixo>/<N>-<slug> da issue",
    "issues.cli.start.dry_run": "só mostra o nome da branch",
    "issues.cli.sync_labels": "cria ou atualiza os labels que o fluxo usa",
    "issues.cli.sync_epic": "cria sub-issues e 'blocked by' a partir da seção Itens",
    "issues.cli.all": "todas as issues com o label de epic",
    "issues.cli.sync_checklist": "acerta as caixas da seção Itens dos epics",
    "issues.cli.parent_of": "o epic pai da issue N",
    "issues.cli.close_epic": "fecha o epic pai quando a última filha fecha",
    "issues.cli.repository": "não consegui identificar o repositório (GITHUB_REPOSITORY, remoto origin ou `gh`).",
    "issues.cli.choose": "{command}: use exatamente um entre {options}",
    "issues.cli.choose.epic": "N [N...] ou --all",
    "issues.cli.choose.checklist": "N [N...], --all ou --parent-of N",
    "issues.cli.pr_merged.number": "pr-merged: informe --pr N (ou PR_NUMBER)",
    "issues.error": "ERRO: {error}",
    # text.py
    "text.slug.fallback": "trabalho",
    # epics.py: vínculos
    "epics.operation.sub_issue": "#{ref} vira sub-issue de #{target}",
    "epics.operation.blocked_by": "#{target} fica bloqueada por #{ref}",
    "epics.item.foreign": "item de outro repositório ignorado: {item}",
    "epics.item.repeated": "#{number} aparece mais de uma vez na lista",
    "epics.item.foreign_dependency": "#{number}: dependência de outro repositório ignorada ({ref})",
    "epics.item.self_dependency": "#{number} depende de si mesma",
    "epics.not_issue": "#{number} não existe ou não é uma issue",
    "epics.lists_itself": "#{epic} lista a si mesmo como item",
    "epics.other_parent": "#{number} já é sub-issue de {parent}; parent não alterado",
    "epics.missing_dependency": "#{number} depende de #{dep}, que não existe ou não é uma issue",
    "epics.unlisted": "{ref} é sub-issue de #{epic} mas não está na seção Itens",
    "epics.truncated": (
        "#{number} tem mais de 100 sub-issues ou bloqueios; a leitura está incompleta "
        "e nenhuma ação automática é segura."
    ),
    "epics.graphql_failed": "gh api graphql falhou: {error}",
    "epics.repository_unreachable": "repositório {repository} inacessível: {error}",
    # epics.py: caixas da seção de itens
    "epics.checklist.check": "{prefix}marcar #{number} na seção Itens",
    "epics.checklist.uncheck": "{prefix}desmarcar #{number} na seção Itens",
    "epics.checklist.write_failed": "ERRO ao atualizar a seção Itens de #{epic}: {error}",
    "epics.checklist.unstable": "ERRO: a seção Itens de #{epic} não estabilizou após {attempts} tentativas",
    "epics.checklist.no_parent": "#{issue} não é sub-issue de um epic deste repositório; nada a fazer.",
    # epics.py: fechamento automático
    "epics.close.no_parent": "#{issue} não é sub-issue de um epic deste repositório; nada a fechar.",
    "epics.close.not_epic": "#{parent} não tem o label epic; não é fechado automaticamente.",
    "epics.close.already_closed": "#{parent} já está fechado.",
    "epics.close.no_children": "#{parent} não tem sub-issues nativas; nada a fechar.",
    "epics.close.foreign": "#{parent} tem sub-issues de outro repositório ({foreign}); feche-o à mão.",
    "epics.close.pending": "#{parent} continua aberto: {pending} ainda aberta(s).",
    "epics.close.dry_run": "[dry-run] fecharia #{parent} como {reason}:\n{comment}",
    "epics.close.raced": "#{parent} já foi fechado por outra execução.",
    "epics.close.failed": "ERRO ao fechar #{parent}: {error}",
    "epics.close.done": "#{parent} fechado como {reason}.",
    "epics.close.too_deep": "ERRO: a cadeia de epics acima de #{issue} passa de {depth} níveis.",
    "epics.summary.head": "Fechado automaticamente pelo fluxo de epics: as {count} sub-issues estão fechadas.",
    "epics.summary.item": "- #{number} {title} — {state}",
    "epics.summary.completed": "concluída",
    "epics.summary.not_planned": "dispensada",
    "epics.summary.foot": "Se algum critério de conclusão do epic ainda faltar, reabra o epic e registre o que falta.",
    # epics.py: sync-epic
    "epics.sync.not_epic": "#{epic} não tem o label epic",
    "epics.sync.shared": "#{number} está em mais de um epic ({epics}); vincule à mão",
    "epics.sync.summary": "#{epic}: {items} itens, {links} vínculos a criar",
    "epics.sync.candidates": ", {count} candidatos sem issue",
    "epics.sync.failed": "ERRO {operation}: {error}",
    "epics.sync.problem": "divergência: {problem}",
    # (fim de issues)
    # === config.py, semver.py, gh.py, plan.py (#38): as chaves deste módulo ==============================
    # (fim de plan)
    # === release.py (#39): as chaves deste módulo =====================================================
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
