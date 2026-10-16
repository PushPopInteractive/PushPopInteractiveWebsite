"""Reassemble an already-signed IPA from verified bytes; never build or resign it."""
import hashlib,json,os,re,shutil,subprocess,urllib.request,urllib.error,zipfile
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

def download_delta(base_url,patch,parts):
    if parts=='auto':
        try:
            download(base_url+patch.name,patch)
            return
        except urllib.error.HTTPError as error:
            if error.code!=404:raise
        with urllib.request.urlopen(base_url+patch.name+'.parts.json',timeout=30) as response:
            parts=str(json.loads(response.read(4096))['parts'])
    if not re.fullmatch(r'[1-9]|1[0-6]',parts):
        raise ValueError('Delta parts must be between 1 and 16')
    if parts=='1':
        download(base_url+patch.name,patch)
        return
    # Parts are only a transfer mechanism. The complete delta hash below remains mandatory.
    with patch.open('wb') as output:
        for index in range(1,int(parts)+1):
            with urllib.request.urlopen(base_url+patch.name+f'.part{index:02}',timeout=180) as response:
                shutil.copyfileobj(response,output)

def package_parts(path,part_bytes=1500000000):
    """Split signed bytes for hosting, without changing or resigning the IPA."""
    parts=[]
    with path.open('rb') as source:
        index=0
        while True:
            first=source.read(min(1024*1024,part_bytes))
            if not first:break
            index+=1;name=path.name+f'.part{index:02}';target=path.with_name(name);h=hashlib.sha256();size=0
            with target.open('wb') as output:
                block=first
                while block:
                    output.write(block);h.update(block);size+=len(block)
                    if size==part_bytes:break
                    block=source.read(min(1024*1024,part_bytes-size))
            parts.append({'name':name,'bytes':size,'sha256':h.hexdigest()})
    result={'bytes':path.stat().st_size,'sha256':digest(path),'parts':parts}
    path.with_name(path.name+'.parts.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def download_package(base_url,target):
    try:
        download(base_url+target.name,target)
        return
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
    with urllib.request.urlopen(base_url+target.name+'.parts.json',timeout=30) as response:record=json.loads(response.read(16384))
    if not isinstance(record.get('parts'),list) or not 1<=len(record['parts'])<=8:raise ValueError('Invalid package descriptor')
    with target.open('wb') as output:
        for index,part in enumerate(record['parts'],1):
            if part['name']!=target.name+f'.part{index:02}' or not isinstance(part['bytes'],int) or not 0<part['bytes']<2**31 or not re.fullmatch(r'[a-f0-9]{64}',part['sha256']):raise ValueError('Invalid package part')
            h=hashlib.sha256();size=0
            with urllib.request.urlopen(base_url+part['name'],timeout=180) as response:
                while block:=response.read(1024*1024):
                    size+=len(block)
                    if size>part['bytes']:raise ValueError('Package part exceeds descriptor')
                    h.update(block);output.write(block)
            if size!=part['bytes'] or h.hexdigest()!=part['sha256']:raise ValueError('Package part checksum mismatch')
    if target.stat().st_size!=record['bytes'] or digest(target)!=record['sha256']:raise ValueError('Package checksum mismatch')

def main():
    build=os.environ['RELEASE_BUILD'];patch_hash=os.environ['DELTA_SHA256'];expected=os.environ['IPA_SHA256']
    if not re.fullmatch(r'[1-9][0-9]*',build) or not all(re.fullmatch(r'[a-f0-9]{64}',h) for h in [patch_hash,expected]):
        raise ValueError('Invalid release inputs')
    base_build=os.environ['BASE_BUILD']
    if not re.fullmatch(r'[1-9][0-9]*',base_build) or int(base_build)>=int(build):raise ValueError('Invalid base build')
    base_url='https://github.com/PushPopInteractive/PushPopInteractiveWebsite/releases/download/install-fireside/'
    patch=Path(f'Fireside-{build}-delta-from-{base_build}.zip');download_delta(base_url,patch,os.environ.get('DELTA_PARTS') or 'auto')
    if digest(patch)!=patch_hash:raise ValueError('Delta checksum mismatch')
    with zipfile.ZipFile(patch) as archive:recipe=json.loads(archive.read('recipe.json'))
    base=Path(f'Fireside-{base_build}.ipa');output=Path(f'Fireside-{build}.ipa')
    if recipe['baseAsset']!=base.name or recipe['outputAsset']!=output.name:raise ValueError('Unexpected asset names')
    download_package(base_url,base);reconstruct(base,patch,output,expected)
    print(json.dumps({'output':str(output),'bytes':output.stat().st_size,'sha256':digest(output),'byteIdentical':True}),flush=True)
    if os.environ.get('PUBLISH_VERIFIED_IPA')=='1':
        repo='PushPopInteractive/PushPopInteractiveWebsite'
        def publish(asset,expected_hash):
            def remote():
                assets=json.loads(subprocess.check_output(['gh','release','view','install-fireside','--repo',repo,'--json','assets']))['assets']
                return next((a for a in assets if a['name']==asset.name),None)
            existing=remote()
            if existing:
                if existing.get('digest')!='sha256:'+expected_hash:raise ValueError('Existing immutable asset differs')
            else:subprocess.run(['gh','release','upload','install-fireside',str(asset),'--repo',repo],check=True)
            if (remote() or {}).get('digest')!='sha256:'+expected_hash:raise ValueError('Remote asset checksum mismatch')
        if output.stat().st_size>=2**31:
            record=package_parts(output)
            for part in record['parts']:publish(output.with_name(part['name']),part['sha256'])
            descriptor=output.with_name(output.name+'.parts.json');publish(descriptor,digest(descriptor))
            print('Published verified signed package parts: '+output.name,flush=True)
        else:
            publish(output,expected)
            print('Published verified '+output.name,flush=True)
if __name__=='__main__':main()
