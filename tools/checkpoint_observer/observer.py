#!/usr/bin/env python3
"""Deterministic evidence index. Never a mathematical proof evaluator."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request

BASELINE = 'a4d881d272a1f67705af0bd81b1f6e9013023ba2'
REPO = 'Hawkar-usls/Janus-Fundamentum'
ROOT = f'https://github.com/{REPO}'

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def relevant(path):
    return (path.startswith(('research/', 'registry/', 'docs/'))
            and path.endswith(('.md', '.json'))
            and bool(re.search(r'R5_|TRUMP|CHECKPOINT|P_VS_NP', path, re.I)))

def source(sha, path):
    try:
        return subprocess.check_output(['git', 'show', f'{sha}:{path}']).decode('utf-8')
    except subprocess.CalledProcessError:
        return None  # deletion is retained as a change, not a scientific retraction

def evidence_lines(content):
    # These are attributed excerpts, NEVER inferred gate transitions.
    pattern = r'gate|locked|open|failed|passed|proof|certificate|counterexample|obstruction|heuristic|observation|next|not.prov|not.claim|limitation|scientific|status|theorem'
    return [{'line': i, 'text': line[:600]} for i, line in enumerate(content.splitlines(), 1)
            if re.search(pattern, line, re.I)][:24]

def runs(sha):
    found = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{REPO}/actions/runs?head_sha={sha}&per_page=100&page={page}'
        req = urllib.request.Request(url, headers={
            'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'})
        with urllib.request.urlopen(req, timeout=30) as response:
            batch = json.load(response)['workflow_runs']
        found.extend({'id': r['id'], 'attempt': r['run_attempt'], 'name': r['name'],
                      'status': r['status'], 'conclusion': r['conclusion'],
                      'url': r['html_url'], 'head_sha': r['head_sha']}
                     for r in batch if r['name'] == 'R5 Frontier Verification')
        if len(batch) < 100:
            return sorted(found, key=lambda r: (r['id'], r['attempt']))
        page += 1

def record(sha, parent, paths, ci):
    files = []
    for path in paths:
        current, previous = source(sha, path), source(parent, path)
        files.append({'path': path, 'url': f'{ROOT}/blob/{sha}/{path}',
                      'previous_url': f'{ROOT}/blob/{parent}/{path}',
                      'change': 'deleted' if current is None else 'added' if previous is None else 'modified',
                      'sha256': hashlib.sha256(current.encode()).hexdigest() if current is not None else None,
                      'previous_sha256': hashlib.sha256(previous.encode()).hexdigest() if previous is not None else None,
                      'source_reported_excerpts': evidence_lines(current or ''),
                      'previous_source_reported_excerpts': evidence_lines(previous or '')})
    return {'schema_version': 1, 'repository': REPO, 'commit': sha, 'parent': parent,
            'commit_url': f'{ROOT}/commit/{sha}', 'files': files, 'r5_runs_exact_commit': ci,
            'scientific_delta': 'REQUIRES_SCIENTIFIC_REVIEW',
            'gate_authority': 'SOURCE_REPORTED_ONLY', 'independent_proof_verification': 'NOT_PERFORMED',
            'p_vs_np': 'OPEN', 'universal_solver': 'NOT_ESTABLISHED_BY_THIS_OBSERVER',
            'next_allowed_step': 'Review exact source delta and certificates; keep existing gates until justified. Missing or failed CI is not UNSAT.'}

def render(r):
    lines = [f"# TRUMP/JANUS — {r['commit'][:12]}", '',
             f"[Commit]({r['commit_url']}) · parent `{r['parent']}`", '',
             '**P vs NP: OPEN. Универсальный solver этим отчётом не установлен.**', '',
             'Научная дельта: **REQUIRES_SCIENTIFIC_REVIEW**. Ни повышение, ни отсутствие изменения научного статуса автоматически не утверждается.', '',
             'Gates: **SOURCE_REPORTED_ONLY**; неподтверждённые переходы — **UNKNOWN**.',
             'HEURISTIC / OBSERVATION: ниже приведены изменения источников и наблюдаемый статус CI.',
             'PROOF / CERTIFICATE: независимая математическая проверка **NOT_PERFORMED**. Слова proof/theorem в источнике не повышают статус.', '',
             '## R5 на точном commit', '']
    for ci in r['r5_runs_exact_commit']:
        lines.append(f"- [Run {ci['id']}, attempt {ci['attempt']}]({ci['url']}): {ci['status']} / {ci['conclusion']}")
    if not r['r5_runs_exact_commit']:
        lines.append('UNKNOWN / NO_RUN_ON_EXACT_COMMIT. Успех другого SHA не переносится.')
    lines += ['', 'CI PASS ≠ универсальное доказательство; timeout/FAIL ≠ UNSAT.', '', '## Изменения и заявления источников', '']
    for f in r['files']:
        lines += [f"### {f['path']}", f"{f['change']} · [после]({f['url']}) · [до]({f['previous_url']})", f"SHA-256: `{f['sha256']}`", '']
        for label, key in [('До', 'previous_source_reported_excerpts'), ('После', 'source_reported_excerpts')]:
            lines += [f'{label} — выборочные строки источника (не полная семантическая сводка):', '']
            lines.extend('    L' + str(e['line']) + ': ' + e['text'] for e in f[key])
            lines.append('')
    lines += ['## Следующий допустимый шаг', '',
              'Проверить научную дельту по ссылкам, область применимости и сертификаты. Сохранить прежние LOCKED/OPEN/FAILED до обоснованного перехода. Частный terminal/FPT/реформулировка не достигают цели универсального SolveLinearCubicXSAT.', '']
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-dir', required=True)
    args = parser.parse_args()
    state = Path(args.state_dir)
    state.mkdir(parents=True, exist_ok=True)
    manifest_path = state / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'cursor': BASELINE, 'reports': []}
    tip = git('rev-parse', 'origin/main')
    subprocess.run(['git', 'merge-base', '--is-ancestor', manifest['cursor'], tip], check=True)
    commits = git('rev-list', '--first-parent', '--reverse', f"{manifest['cursor']}..{tip}").splitlines()
    updated = []
    # Refresh all indexed checkpoints for delayed CI; no cursor advance on API failure.
    for sha in manifest['reports']:
        p = state / f'{sha}.json'
        old = json.loads(p.read_text())
        ci = runs(sha)
        if ci != old['r5_runs_exact_commit']:
            old['r5_runs_exact_commit'] = ci
            p.write_text(json.dumps(old, ensure_ascii=False, indent=2) + '\n')
            (state / f'{sha}.md').write_text(render(old))
            updated.append(sha)
    for sha in commits:
        parent = git('rev-parse', f'{sha}^1')
        paths = [p for p in git('diff', '--name-only', parent, sha).splitlines() if relevant(p)]
        if not paths:
            continue
        r = record(sha, parent, paths, runs(sha))
        (state / f'{sha}.json').write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n')
        (state / f'{sha}.md').write_text(render(r))
        manifest['reports'].append(sha)
        updated.append(sha)
    manifest['cursor'] = tip
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    index = '# TRUMP/JANUS checkpoint reports\n\nP vs NP: OPEN. Source-attributed reports; not independent proof verification.\n\n'
    index += '\n'.join(f'- [{s[:12]}]({s}.md) ([JSON]({s}.json))' for s in reversed(manifest['reports']))
    (state / 'README.md').write_text(index + '\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write(f'Processed through `{tip}`. New/updated reports: {len(updated)}.\n\n')
            f.write(f'[Persistent reports]({ROOT}/tree/checkpoint-reports)\n\n')
            for sha in updated:
                f.write(f'- [{sha[:12]}]({ROOT}/blob/checkpoint-reports/{sha}.md)\n')
    print(json.dumps({'cursor': tip, 'updated': updated}))

if __name__ == '__main__':
    main()
