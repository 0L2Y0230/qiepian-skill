"""Release portability and integrity tests; these do not evaluate model behavior."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load('build_release')
verifier = load('verify_package')


class ReleaseTests(unittest.TestCase):
    def test_isolated_reproducible_package_excludes_local_state(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            isolated = temp / 'isolated-skill'
            isolated.mkdir()
            for path in builder.release_files(ROOT):
                destination = isolated / path.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
            # This isolated copy has no external rules, Git metadata, or local config.
            a = builder.build(isolated, temp / 'a')
            b = builder.build(isolated, temp / 'b')
            self.assertEqual(a.read_bytes(), b.read_bytes())
            manifest = verifier.verify(a)
            self.assertNotIn('config.local.json', manifest['files'])
            self.assertFalse(any('.git' in Path(p).parts for p in manifest['files']))
            with zipfile.ZipFile(a) as bundle:
                bundle.extractall(temp / 'installed')
            installed = temp / 'installed' / 'qiepian-skill'
            config = json.loads((installed / 'config.example.json').read_text(encoding='utf-8'))
            self.assertFalse(Path(config['rules_root']).is_absolute())
            self.assertTrue((installed / config['rules_root'] / '切片文案.md').is_file())
            for path in manifest['files']:
                text = (installed / path).read_text(encoding='utf-8')
                self.assertNotIn('D:\\Daihuo', text)
                self.assertNotIn('D:\\GPTWork', text)
            with self.assertRaises(FileExistsError):
                builder.build(isolated, temp / 'a')

    def test_tampered_or_unsafe_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            original = builder.build(ROOT, temp / 'source')
            for changed_path in ('qiepian-skill/SKILL.md', '../escape'):
                modified = temp / ('tampered.zip' if 'SKILL' in changed_path else 'unsafe.zip')
                with zipfile.ZipFile(original) as src, zipfile.ZipFile(modified, 'w') as dst:
                    for item in src.infolist():
                        dst.writestr(item, b'changed' if item.filename == changed_path else src.read(item.filename))
                    if changed_path == '../escape':
                        dst.writestr(changed_path, b'unsafe')
                with self.assertRaises(ValueError):
                    verifier.verify(modified)


if __name__ == '__main__':
    unittest.main()
