"""Build an immutable, portable release ZIP using only the Python standard library."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT_FILES = ('SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION.json', 'config.example.json')
RESOURCE_DIRS = {'agents': {'.yaml'}, 'references': {'.md'},
                 'scripts': {'.py'}, 'tests': {'.py', '.md', '.srt'}}


def release_files(root):
    paths = [root / name for name in ROOT_FILES]
    for directory, suffixes in RESOURCE_DIRS.items():
        paths.extend(p for p in (root / directory).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts
                     and not any(part.startswith('.') for part in p.relative_to(root).parts)
                     and p.suffix in suffixes
                     and not p.name.endswith(('.pyc', '.pyo', '.local.json')))
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Release file escapes skill root')
    return sorted(paths)


def build(root, output):
    root = root.resolve()
    version = json.loads((root / 'VERSION.json').read_text(encoding='utf-8'))
    number = version['skill_version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', number):
        raise ValueError('skill_version must be a numeric semantic version')
    files = release_files(root)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / ('qiepian-skill-v' + number + '.zip')
    checksum = output / 'SHA256SUMS.txt'
    if archive.exists() or checksum.exists():
        raise FileExistsError('Release output exists; choose a new empty output directory')
    manifest = dict(version, files={})
    payloads = {}
    for path in files:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        payloads[relative] = data
        manifest['files'][relative] = hashlib.sha256(data).hexdigest()
    payloads['manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    # Stable timestamps and ordering make repeated builds reproducible.
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as bundle:
        for relative, data in sorted(payloads.items()):
            info = zipfile.ZipInfo('qiepian-skill/' + relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    checksum.write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n', encoding='utf-8')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path('dist'))
    args = parser.parse_args()
    print(build(Path(__file__).resolve().parents[1], args.output_dir))
