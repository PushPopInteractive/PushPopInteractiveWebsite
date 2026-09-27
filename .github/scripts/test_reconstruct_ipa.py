import hashlib,importlib.util,json,tempfile,unittest,zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('assembler',Path(__file__).with_name('reconstruct-ipa.py'));assembler=importlib.util.module_from_spec(spec);spec.loader.exec_module(assembler)
class ExactPackage(unittest.TestCase):
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
