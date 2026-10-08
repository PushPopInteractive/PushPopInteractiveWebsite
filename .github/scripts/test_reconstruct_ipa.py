import hashlib,importlib.util,json,tempfile,unittest,zipfile,io
from unittest.mock import patch
from pathlib import Path
spec=importlib.util.spec_from_file_location('assembler',Path(__file__).with_name('reconstruct-ipa.py'));assembler=importlib.util.module_from_spec(spec);spec.loader.exec_module(assembler)
class ExactPackage(unittest.TestCase):
    def test_multipart_download_preserves_order(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'delta.zip'
            with patch.object(assembler.urllib.request,'urlopen',side_effect=[io.BytesIO(b'abc'),io.BytesIO(b'def')]) as get:
                assembler.download_delta('https://example.test/',output,'2')
            self.assertEqual(output.read_bytes(),b'abcdef')
            self.assertEqual([c.args[0] for c in get.call_args_list],['https://example.test/delta.zip.part01','https://example.test/delta.zip.part02'])
    def test_invalid_part_counts_never_download(self):
        with patch.object(assembler.urllib.request,'urlopen') as get:
            for value in ['0','17','-1','2.5','01','x']:
                with self.assertRaises(ValueError):assembler.download_delta('https://example.test/',Path('unused'),value)
            get.assert_not_called()
    def fixture(self,root,data=b'XY',segments=None):
        base=root/'base';base.write_bytes(b'abcdefgh');patch=root/'patch.zip';expected=hashlib.sha256(b'abcXYfgh').hexdigest()
        recipe={'baseSha256':assembler.digest(base),'outputSha256':expected,'outputBytes':8,'segments':segments or [['base',0,3],['patch',0,2],['base',5,3]]}
        with zipfile.ZipFile(patch,'w') as z:z.writestr('recipe.json',json.dumps(recipe));z.writestr('data.bin',data)
        return base,patch,root/'output',expected
    def test_exact_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            args=self.fixture(Path(d));assembler.reconstruct(*args);self.assertEqual(args[2].read_bytes(),b'abcXYfgh')
    def test_changed_data_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'byte-identical'):assembler.reconstruct(*self.fixture(Path(d),b'XZ'))
    def test_out_of_bounds_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'exceeds'):assembler.reconstruct(*self.fixture(Path(d),segments=[['base',99,1]]))
if __name__=='__main__':unittest.main()
