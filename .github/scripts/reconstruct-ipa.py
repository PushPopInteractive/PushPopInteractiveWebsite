"""Reassemble an already-signed IPA from verified bytes; never build or resign it."""
import hashlib,json,os,re,shutil,subprocess,urllib.request,zipfile
from pathlib import Path

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def reconstruct(base,patch,output,expected):
    with zipfile.ZipFile(patch) as archive:
        if set(archive.namelist()) != {'data.bin','recipe.json'}:
            raise ValueError('Unexpected delta contents')
        recipe=json.loads(archive.read('recipe.json'))
        if recipe['outputSha256'] != expected or digest(base) != recipe['baseSha256']:
            raise ValueError('Input checksum mismatch')
        with archive.open('data.bin') as data, open(str(output)+'.delta','wb') as tmp:
            shutil.copyfileobj(data,tmp)
    delta=Path(str(output)+'.delta')
    try:
        with base.open('rb') as source,delta.open('rb') as changed,output.open('wb') as result:
            streams={'base':source,'patch':changed}
            for kind,start,length in recipe['segments']:
                if kind not in streams or not isinstance(start,int) or not isinstance(length,int) or start<0 or length<0:
                    raise ValueError('Invalid delta range')
                stream=streams[kind];stream.seek(start)
                remaining=length
                while remaining:
                    block=stream.read(min(remaining,1024*1024))
                    if not block:raise ValueError('Delta range exceeds input')
                    result.write(block);remaining-=len(block)
        if output.stat().st_size != recipe['outputBytes'] or digest(output) != expected:
            raise ValueError('Reconstructed IPA is not byte-identical')
    finally:
        delta.unlink(missing_ok=True)
    return recipe

def download(url,target):
    with urllib.request.urlopen(url,timeout=180) as response,target.open('wb') as output:
        shutil.copyfileobj(response,output)

def main():
    build=os.environ['RELEASE_BUILD'];patch_hash=os.environ['DELTA_SHA256'];expected=os.environ['IPA_SHA256']
    if not re.fullmatch(r'[1-9][0-9]*',build) or not all(re.fullmatch(r'[a-f0-9]{64}',h) for h in [patch_hash,expected]):
        raise ValueError('Invalid release inputs')
    base_build=os.environ['BASE_BUILD']
    if not re.fullmatch(r'[1-9][0-9]*',base_build) or int(base_build)>=int(build):raise ValueError('Invalid base build')
    base_url='https://github.com/PushPopInteractive/PushPopInteractiveWebsite/releases/download/install-fireside/'
    patch=Path(f'Fireside-{build}-delta-from-{base_build}.zip');download(base_url+patch.name,patch)
    if digest(patch)!=patch_hash:raise ValueError('Delta checksum mismatch')
    with zipfile.ZipFile(patch) as archive:recipe=json.loads(archive.read('recipe.json'))
    base=Path(f'Fireside-{base_build}.ipa');output=Path(f'Fireside-{build}.ipa')
    if recipe['baseAsset']!=base.name or recipe['outputAsset']!=output.name:raise ValueError('Unexpected asset names')
    download(base_url+base.name,base);reconstruct(base,patch,output,expected)
    print(json.dumps({'output':str(output),'bytes':output.stat().st_size,'sha256':digest(output),'byteIdentical':True}),flush=True)
    if os.environ.get('PUBLISH_VERIFIED_IPA')=='1':
        repo='PushPopInteractive/PushPopInteractiveWebsite'
        def remote():
            assets=json.loads(subprocess.check_output(['gh','release','view','install-fireside','--repo',repo,'--json','assets']))['assets']
            return next((a for a in assets if a['name']==output.name),None)
        existing=remote()
        if existing:
            if existing.get('digest')!='sha256:'+expected:raise ValueError('Existing immutable IPA differs')
        else:subprocess.run(['gh','release','upload','install-fireside',str(output),'--repo',repo],check=True)
        if (remote() or {}).get('digest')!='sha256:'+expected:raise ValueError('Remote IPA checksum mismatch')
        print('Published verified '+output.name,flush=True)
if __name__=='__main__':main()
