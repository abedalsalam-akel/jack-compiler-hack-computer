import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CompilerSmokeTests(unittest.TestCase):
    def test_compiler_generates_function_and_return(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / 'Main.jack'
            source.write_text('class Main { function void main() { return; } }\n')
            subprocess.run([sys.executable, str(ROOT / 'project11' / 'Main.py'), str(source)], check=True)
            vm = source.with_suffix('.vm').read_text()
            self.assertIn('function Main.main 0', vm)
            self.assertIn('return', vm)

    def test_vm_translator_produces_hack_assembly(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / 'Simple.vm'
            source.write_text('push constant 7\npush constant 8\nadd\n')
            subprocess.run([sys.executable, str(ROOT / 'project08' / 'Main.py'), str(source)], check=True)
            asm = source.with_suffix('.asm').read_text()
            self.assertIn('@7', asm)
            self.assertIn('@8', asm)
            self.assertIn('M=D+M', asm)


    def test_jack_analyzer_generates_xml_parse_tree(self):
        import xml.etree.ElementTree as ET

        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / 'Main.jack'
            source.write_text('class Main { function void main() { return; } }\n')
            subprocess.run([sys.executable, str(ROOT / 'project10' / 'Main.py'), str(source)], check=True)
            output = source.with_suffix('.xml')
            self.assertTrue(output.is_file())
            tree = ET.parse(output)
            self.assertEqual(tree.getroot().tag, 'class')
            self.assertIsNotNone(tree.find('.//subroutineDec'))
            self.assertIsNotNone(tree.find('.//returnStatement'))


if __name__ == '__main__':
    unittest.main()
