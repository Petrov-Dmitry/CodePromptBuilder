import unittest
import tempfile
import shutil
from pathlib import Path
from code_prompt_builder import parse_gitignore, should_ignore, collect_files

class TestCodePromptBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path(tempfile.mkdtemp())
        (cls.test_dir / 'test.txt').write_text("Test content")
        (cls.test_dir / '.gitignore').write_text("*.tmp\nignore_dir/\n!important.tmp")
        (cls.test_dir / 'test.tmp').write_text("Temp file")
        (cls.test_dir / 'important.tmp').write_text("Important temp")
        (cls.test_dir / 'ignore_dir').mkdir()
        (cls.test_dir / 'ignore_dir' / 'file.txt').write_text("Ignored")
        (cls.test_dir / 'binary.data').write_bytes(b'\x00\x01\x02')
        (cls.test_dir / 'файл.txt').write_text("Тест")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)

    def test_parse_gitignore(self):
        patterns = parse_gitignore(self.test_dir / '.gitignore')
        self.assertEqual(sorted(patterns), ['*.tmp', 'ignore_dir/', '!important.tmp'])

    def test_should_ignore(self):
        patterns = parse_gitignore(self.test_dir / '.gitignore')
        self.assertTrue(should_ignore(
            self.test_dir / 'test.tmp',
            patterns,
            self.test_dir
        ))
        self.assertFalse(should_ignore(
            self.test_dir / 'test.txt',
            patterns,
            self.test_dir
        ))
        self.assertFalse(should_ignore(
            self.test_dir / 'important.tmp',
            patterns,
            self.test_dir
        ))

    def test_collect_files(self):
        patterns = parse_gitignore(self.test_dir / '.gitignore')
        files = collect_files(self.test_dir, self.test_dir, patterns)
        file_names = [f.name for f in files]
        self.assertIn('test.txt', file_names)
        self.assertIn('important.tmp', file_names)
        self.assertIn('файл.txt', file_names)
        self.assertIn('binary.data', file_names)
        self.assertNotIn('test.tmp', file_names)
        self.assertNotIn('file.txt', file_names)

    def test_exclude_patterns(self):
        files = collect_files(
            self.test_dir,
            self.test_dir,
            [],
            exclude_patterns=["*.txt"]
        )
        collected_names = [f.name for f in files]
        self.assertIn('important.tmp', collected_names)
        self.assertNotIn('test.txt', collected_names)

    def test_binary_file_handling(self):
        files = collect_files(self.test_dir, self.test_dir, [])
        binary_files = [f for f in files if f.name == 'binary.data']
        self.assertEqual(len(binary_files), 1)

    def test_unicode_filenames(self):
        files = collect_files(self.test_dir, self.test_dir, [])
        unicode_files = [f for f in files if f.name == 'файл.txt']
        self.assertEqual(len(unicode_files), 1)
        self.assertEqual(unicode_files[0].read_text(encoding='utf-8'), "Тест")

if __name__ == '__main__':
    unittest.main()
