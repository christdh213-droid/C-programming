"""Execute all C experiments for real; preserve exact stdout, diagnostics and commands."""
from pathlib import Path
import argparse,hashlib,json,subprocess
R=Path(__file__).resolve().parent
def run(q):
    folder=R/q; (R/'build').mkdir(exist_ok=True)
    results=[]
    for source in sorted(folder.glob('*.c')):
        out=f'build/{q}_{source.stem}.exe'
        cmd=['gcc','-std=c11','-O2','-Wall','-Wextra',f'{q}/{source.name}','-o',out]
        if '#include <math.h>' in source.read_text(): cmd+=['-lm']
        comp=subprocess.run(cmd,cwd=R,capture_output=True)
        prefix=folder/'outputs'/source.stem
        prefix.with_suffix('.compiler.txt').write_bytes(comp.stdout+comp.stderr)
        assert comp.returncode==0 and not comp.stdout and not comp.stderr,comp.stderr.decode(errors='replace')
        inp=folder/(source.stem+'.input.txt')
        if not inp.exists(): inp=folder/'input.txt'
        proc=subprocess.run([str(R/out)],input=inp.read_bytes(),capture_output=True,cwd=R,timeout=180)
        prefix.with_suffix('.stdout.txt').write_bytes(proc.stdout)
        prefix.with_suffix('.stderr.txt').write_bytes(proc.stderr)
        assert proc.returncode==0,(q,source.name,proc.stderr)
        transcript=('$ '+subprocess.list2cmdline(cmd)+'\n$ '+out+' < '+str(inp.relative_to(R)).replace('\\','/')+'\n').encode()+proc.stdout+proc.stderr
        prefix.with_suffix('.transcript.txt').write_bytes(transcript)
        expected=folder/'expected'/f'{source.stem}.txt'
        if expected.exists(): assert proc.stdout==expected.read_bytes(),(q,source.name,'expected stdout mismatch')
        results.append(dict(source=source.name,compile=cmd,input=str(inp.relative_to(R)),exit_code=proc.returncode,stdout_sha256=hashlib.sha256(proc.stdout).hexdigest(),expected_bytes_match=expected.exists()))
        print(f'{q}/{source.name}: PASS, stdout bytes={len(proc.stdout)}',flush=True)
    (folder/'outputs/manifest.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('questions',nargs='*',default=[f'Q{i}' for i in range(1,8)])
    for q in p.parse_args().questions: run(q)
