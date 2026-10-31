"""Install this complete skill into a supported Agent directory without overwrites."""
import argparse
import os
from pathlib import Path
import sys

from build_release import release_files

SKILL_NAME = 'qiepian-skill'
AGENTS = ('codex', 'deepseek', 'kimi')
REQUIRED_RULES = ('执行环境与规则来源.md', '独立版总控执行卡.md',
                  '切片文案执行卡.md', '切片文案.md', '独立版强制验收卡.md')


def target_directory(agent, scope='user', project=None, environ=None, home=None):
    if agent not in AGENTS:
        raise ValueError('Unsupported Agent; import into Doubao Work through its UI')
    if scope not in ('user', 'project'):
        raise ValueError('Unknown installation scope')
    if scope == 'project':
        if project is None:
            raise ValueError('--project-dir is required for project scope')
        project = Path(project).expanduser().resolve()
        if not project.is_dir():
            raise ValueError('Project directory does not exist')
        return project / '.agents' / 'skills' / SKILL_NAME
    if project is not None:
        raise ValueError('--project-dir requires --scope project')
    env = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    env_name, default = {
        'codex': ('CODEX_HOME', '.codex'),
        'deepseek': ('DSH_HOME', '.dsh'),
        'kimi': ('KIMI_CODE_HOME', '.kimi-code'),
    }[agent]
    configured = env.get(env_name)
    base = Path(configured).expanduser() if configured else home / default
    if not base.is_absolute():
        raise ValueError(env_name + ' must be an absolute path')
    return base / 'skills' / SKILL_NAME


def install(source, target, dry_run=False):
    source, target = Path(source).resolve(), Path(target).absolute()
    if target.exists() or target.is_symlink():
        raise FileExistsError('Target already exists; back up and handle it manually: ' + str(target))
    if target.resolve().is_relative_to(source):
        raise ValueError('Install destination must be outside this skill directory')
    for name in REQUIRED_RULES:
        if not (source / 'references' / name).read_text(encoding='utf-8').strip():
            raise ValueError('Required rule file is empty: ' + name)
    payloads = [(p.relative_to(source), p.read_bytes()) for p in release_files(source)]
    if dry_run:
        return len(payloads)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    try:
        for relative, data in payloads:
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('xb') as stream:
                stream.write(data)
    except Exception:
        print('Installation incomplete at ' + str(target) + '; inspect before retrying.', file=sys.stderr)
        raise
    return len(payloads)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=AGENTS, required=True)
    parser.add_argument('--scope', choices=('user', 'project'), default='user')
    parser.add_argument('--project-dir', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        target = target_directory(args.agent, args.scope, args.project_dir)
        count = install(Path(__file__).resolve().parents[1], target, args.dry_run)
    except (ValueError, OSError) as error:
        parser.exit(1, 'ERROR: ' + str(error) + '\n')
    print(('DRY RUN: ' if args.dry_run else 'COPIED: ') + str(target) + ' (' + str(count) + ' files)')
    print('Next: open the Agent, confirm skill discovery and run installation self-check.')


if __name__ == '__main__':
    main()
