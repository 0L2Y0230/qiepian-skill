"""Verify a downloaded release ZIP without extracting it or reading external rules."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def verify(archive):
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(set(names)) != len(names):
            raise ValueError('Duplicate ZIP entries')
        prefix = 'qiepian-skill/'
        for name in names:
            parts = PurePosixPath(name).parts
            if not name.startswith(prefix) or '\\' in name or '..' in parts or ':' in name:
                raise ValueError('Unsafe ZIP path')
        manifest = json.loads(bundle.read(prefix + 'manifest.json'))
        expected = {prefix + path for path in manifest['files']} | {prefix + 'manifest.json'}
        if set(names) != expected:
            raise ValueError('Unexpected or missing package files')
        for path, expected_hash in manifest['files'].items():
            if hashlib.sha256(bundle.read(prefix + path)).hexdigest() != expected_hash:
                raise ValueError('Checksum mismatch: ' + path)
        version = json.loads(bundle.read(prefix + 'VERSION.json'))
        if any(manifest[key] != version[key] for key in ('skill_version', 'rules_version', 'release_date')):
            raise ValueError('Version metadata mismatch')
        for path in ('SKILL.md', 'references/执行环境与规则来源.md',
                     'references/独立版总控执行卡.md', 'references/切片文案执行卡.md',
                     'references/切片文案.md', 'references/独立版强制验收卡.md'):
            if not bundle.read(prefix + path).decode('utf-8').strip():
                raise ValueError('Required rule file empty: ' + path)
        if prefix + 'config.local.json' in expected or any('/.git/' in name for name in names):
            raise ValueError('Private installation state must not ship')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    result = verify(args.archive)
    print('PASS: skill ' + result['skill_version'] + ', rules ' + result['rules_version']
          + ', verified ' + str(len(result['files'])) + ' files')
