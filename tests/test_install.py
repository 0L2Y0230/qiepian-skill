"""Exercise a shipped installer from an isolated ZIP, without calling Agent services."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_release import build
from install_agent import install, target_directory
from verify_package import verify


class InstallationTests(unittest.TestCase):
    def test_zip_installs_complete_resources_for_each_host(self):
        with tempfile.TemporaryDirectory(prefix='切片 install ') as directory:
            temp = Path(directory)
            archive = build(ROOT, temp / 'release')
            manifest = verify(archive)
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(temp / 'unpacked')
            source = temp / 'unpacked' / 'qiepian-skill'
            # Even if a distributor has a local override, it must not be copied.
            (source / 'config.local.json').write_text('{}', encoding='utf-8')
            for agent, variable in (('codex', 'CODEX_HOME'), ('deepseek', 'DSH_HOME'),
                                    ('kimi', 'KIMI_CODE_HOME')):
                with self.subTest(agent=agent):
                    agent_root = temp / (agent + ' data')
                    env = dict(os.environ, **{variable: str(agent_root), 'PYTHONUTF8': '1'})
                    result = subprocess.run(
                        [sys.executable, str(source / 'scripts' / 'install_agent.py'),
                         '--agent', agent], cwd=temp, env=env, capture_output=True, text=True,
                        encoding='utf-8')
                    self.assertEqual(result.returncode, 0, result.stderr)
                    installed = agent_root / 'skills' / 'qiepian-skill'
                    self.assertFalse((installed / 'config.local.json').exists())
                    for relative in manifest['files']:
                        self.assertEqual((source / relative).read_bytes(),
                                         (installed / relative).read_bytes(), relative)
                    self.assertIn('docs/安装与兼容性.md', manifest['files'])
                    repeated = subprocess.run(
                        [sys.executable, str(source / 'scripts' / 'install_agent.py'),
                         '--agent', agent], cwd=temp, env=env, capture_output=True, text=True,
                        encoding='utf-8')
                    self.assertNotEqual(repeated.returncode, 0)
                    self.assertEqual((installed / 'SKILL.md').read_bytes(),
                                     (source / 'SKILL.md').read_bytes())

    def test_project_scope_and_dry_run_do_not_create_state(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            for agent in ('codex', 'deepseek', 'kimi'):
                target = target_directory(agent, 'project', project)
                self.assertEqual(target, project / '.agents' / 'skills' / 'qiepian-skill')
                self.assertGreater(install(ROOT, target, dry_run=True), 0)
                self.assertFalse(target.parent.exists())
            for agent, default in (('codex', '.codex'), ('deepseek', '.dsh'),
                                   ('kimi', '.kimi-code')):
                self.assertEqual(target_directory(agent, environ={}, home=project),
                                 project / default / 'skills' / 'qiepian-skill')

    def test_invalid_destination_and_existing_state_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            target = temp / 'already-installed'
            target.mkdir()
            sentinel = target / 'config.local.json'
            sentinel.write_text('keep my configuration', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                install(ROOT, target)
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'keep my configuration')
            with self.assertRaises(ValueError):
                install(ROOT, ROOT / 'dist' / 'bad-install', dry_run=True)
            with self.assertRaises(ValueError):
                target_directory('kimi', environ={'KIMI_CODE_HOME': 'relative'}, home=temp)
            with self.assertRaises(ValueError):
                target_directory('deepseek', 'project')

    def test_missing_rules_abort_before_creating_target(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            source = temp / 'incomplete'
            source.mkdir()
            target = temp / 'new-agent' / 'skills' / 'qiepian-skill'
            with self.assertRaises(FileNotFoundError):
                install(source, target)
            self.assertFalse(target.parent.exists())


if __name__ == '__main__':
    unittest.main()
