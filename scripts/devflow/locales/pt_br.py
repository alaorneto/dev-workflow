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
    # config.py: forma e tipos (a chave vem antes, em `dev-workflow.toml: `chave` ...`)
    "config.type.bool": "booleano",
    "config.type.int": "inteiro",
    "config.type.float": "número",
    "config.type.str": "texto",
    "config.type.list": "lista",
    "config.type.dict": "tabela",
    "config.type.other": "outro tipo",
    "config.shape.table": "deve ser uma tabela, não {got}.",
    "config.shape.type": "deve ser {expected}, não {got}.",
    "config.key.unknown_close": "não é uma chave conhecida. Você quis dizer `{close}`?",
    "config.key.unknown": "não é uma chave conhecida. Aceitas: {accepted}.",
    # config.py: valores
    "config.schema": "deve ser 1.",
    "config.types.empty": "precisa de ao menos um tipo.",
    "config.changelog.section_missing": "precisa de uma seção com id `{id}`.",
    "config.one_of": "deve ser um de {accepted}.",
    "config.types.prefixes": "precisa de ao menos um prefixo de commit e branch.",
    "config.types.section": "não corresponde a um id de `changelog.sections`.",
    "config.regex.invalid": "não é uma expressão regular válida: {error}.",
    "config.initial_version": "não é uma versão SemVer.",
    "config.required": "é obrigatório.",
    "config.files.search_or_regex": "precisa de exatamente um entre `search` e `regex`.",
    "config.files.replace": "é obrigatório com `regex`.",
    "config.files.marker": (
        "precisa de um marcador `{{current…}}` (por exemplo `version = \"{{current}}\"`): sem ele a troca "
        "não muda nada."
    ),
    "config.files.count": "deve ser um inteiro maior que zero.",
    "config.globs.empty": "precisa de ao menos um padrão.",
    "config.floors.group": "precisa de um grupo de captura com a versão.",
    "config.commit_message.tag": "precisa conter `{{tag}}`.",
    "config.release.mark": "aceita `comment` e `milestone`.",
    "config.file.not_utf8": "{path}: não está em UTF-8; salve o arquivo em UTF-8.",
    # semver.py
    "semver.parse": "'{text}' não é uma versão SemVer (major.minor.patch[-pre][+build]).",
    "semver.bump": "Nível '{level}' não incrementa a versão.",
    "semver.level.unknown": "Nível desconhecido: '{level}'. Use um de {accepted}.",
    "semver.zero_major.unknown": "Política de 0.x desconhecida: '{policy}'.",
    "semver.channel.invalid": "Canal de pré-release inválido: '{channel}'.",
    "semver.channel.outside": "Canal de pré-release '{channel}' fora da lista do projeto ({accepted}).",
    "semver.channel.empty_list": "vazia",
    # gh.py
    "gh.exit": "saída {code}",
    "gh.missing.gh": (
        "`{command}` não foi encontrado: a CLI do GitHub é necessária (https://cli.github.com, depois "
        "`gh auth login`). Para seguir só com o git, sem GitHub, use {env}=1."
    ),
    "gh.missing.tool": "`{command}` não foi encontrado no PATH; instale-o ou confira o PATH.",
    "gh.timeout": "não respondeu em {seconds} s; aumente {env} se a rede estiver lenta.",
    "gh.env.invalid": "{env} deve ser uma lista JSON de strings.",
    "gh.api.failed": "o GitHub respondeu {shown} em {route}: {detail}",
    "gh.api.failed_after": "o GitHub respondeu {shown} em {route} depois de {count} tentativas: {detail}",
    "gh.api.not_json": "a resposta de {route} não é JSON válido: {body}",
    # plan.py: sinais (o detalhe de cada `Signal`; o código em `source` não muda com o idioma)
    "plan.signal.issue": "#{number} tem o label `{label}`",
    "plan.signal.pr_title": "título do PR",
    "plan.signal.commit": "`{type}` em {where}",
    "plan.signal.bang": "`!` em {where}: {description}",
    "plan.signal.breaking_commit": "BREAKING CHANGE em {where}: {note}",
    "plan.signal.label": "label `{label}`",
    "plan.signal.breaking_body": "BREAKING CHANGE no corpo do PR: {note}",
    "plan.signal.surface_added": "`{path}` acrescentado em «{surface}»",
    "plan.signal.surface_modified": "`{path}` alterado em «{surface}»",
    "plan.signal.surface_removed": "`{path}` removido em «{surface}»",
    # plan.py: notas
    "plan.none": "nenhum",
    "plan.note.issue_type": (
        "#{number} (citada por {change}) não tem exatamente um label de tipo ({found}): ela não "
        "decide o nível nem a seção do changelog. Deixe um só tipo na issue."
    ),
    "plan.note.reverted": (
        "{revert} reverte {original} ({title}) antes da release: os dois saem do cálculo do nível e do changelog."
    ),
    "plan.note.stale_analysis": (
        "{change}: análise anterior ao último commit do PR; ela não conta e a mudança fica sem "
        "análise até uma nova ser registrada."
    ),
    "plan.note.at_least_patch": "Nenhum sinal pede incremento; uma versão publicada sobe ao menos o patch.",
    "plan.note.zero_major": (
        "Versão 0.x: a quebra de compatibilidade sobe o minor. Para declarar a API estável e ir a 1.0.0, "
        "use o label `{label}` no PR de release."
    ),
    "plan.note.floor_raised": "`{path}` declara o piso {version}: o nível sobe de {old} para {new}.",
    "plan.override.source": "label `{label}` em {change}",
    "plan.override.no_reason": "(motivo não informado)",
    # plan.py: problemas
    "plan.problem.nothing": "Nada se acumulou desde a última versão; não há o que publicar.",
    "plan.problem.floor": (
        "`{path}` declara o piso {version}, maior que a versão {target} que seria publicada. "
        "Corrija o piso ou classifique a mudança de modo que a versão o alcance."
    ),
    "plan.problem.tag_exists": (
        "A tag {tag} já existe. Numa branch de manutenção só cabem correções; "
        "confira a branch e o nível calculado."
    ),
    "plan.problem.analysis_missing": (
        "Mudanças em superfícies públicas sem análise registrada: {changes}. Registre a análise "
        "(`release.py record-analysis`) ou sobreponha o nível com motivo."
    ),
    # plan.py: análise gravada (erros de formato)
    "plan.analysis.schema": 'A análise precisa de `"schema": 1` e de uma lista `changes`.',
    "plan.analysis.object": "{where} deve ser um objeto.",
    "plan.analysis.reference": "{where} precisa de `pr` (número) ou `commit` (SHA com 7 caracteres ou mais).",
    "plan.analysis.level": "{where}.level deve ser um de {accepted}.",
    "plan.analysis.summary": "{where}.summary é obrigatório: uma frase com o motivo do nível.",
    "plan.analysis.evidence": "{where}.evidence deve ser uma lista de textos.",
    # plan.py: changelog e justificativa do número
    "plan.changelog.part_of": "— parte de {issues}",
    "plan.changelog.empty": "Sem mudanças visíveis para quem usa o projeto.",
    "plan.origin.initial": "{version} (versão inicial, sem tag)",
    "plan.justification.headline": "**{origin} → {target}** — nível **{level}**.",
    "plan.justification.override": (
        "Nível sobreposto para **{level}** ({source}); o cálculo dava **{natural}**. Motivo: {reason}"
    ),
    "plan.justification.table_header": "| Mudança | Nível | Sinais |",
    "plan.justification.unanalyzed": "superfície pública tocada sem análise: {paths}",
    "plan.justification.analysis_all": "Análise por agente: cobre todas as mudanças.",
    "plan.justification.analysis_some": (
        "Análise por agente: cobre {analyzed} de {total} mudanças; as demais só têm sinais determinísticos."
    ),
    "plan.justification.analysis_none": "Análise por agente: ausente; o nível vem só dos sinais determinísticos.",
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
