"""Actual GCC compilation and subprocess execution with byte-exact evidence."""
from pathlib import Path
import subprocess,json,hashlib,os,argparse
R=Path(__file__).resolve().parent.parent
ENV=dict(os.environ);ENV['PATH']=r'C:\msys64\ucrt64\bin'+os.pathsep+ENV.get('PATH','')
def record(folder,name,command,proc):
    (folder/'outputs'/f'{name}.stdout.txt').write_bytes(proc.stdout)
    (folder/'outputs'/f'{name}.stderr.txt').write_bytes(proc.stderr)
    (folder/'outputs'/f'{name}.transcript.txt').write_bytes(('$ '+subprocess.list2cmdline(command)+'\n').encode()+proc.stdout+proc.stderr)
def task(number,task):
    a=R/f'Assignment{number}-CO{number}';folder=a/task;(a/'build').mkdir(exist_ok=True)
    results=[]
    for source in sorted(folder.glob('*.c')):
        name=source.stem
        command=['gcc','-std=c11','-Wall','-Wextra',f'{task}/{source.name}']
        if name=='extern_store':
            command+=['-c','-o',f'build/{task}_{name}.o']
        else:
            if name=='counter_four_ways':command+=[f'{task}/extern_store.c']
            command+=['-o',f'build/{task}_{name}.exe']
            if name=='nightly_report':command+=['-lpsapi']
        comp=subprocess.run(command,cwd=a,env=ENV,capture_output=True)
        (folder/'outputs'/f'{name}.compiler.txt').write_bytes(comp.stdout+comp.stderr)
        if name=='forensics_bug':
            assert comp.returncode!=0 and b'pointer' in comp.stderr
            (folder/'outputs/compile_error.txt').write_bytes(comp.stdout+comp.stderr)
            record(folder,'compile_error',command,comp)
            results.append(dict(source=source.name,compile=command,compile_exit=comp.returncode,intentional_error=True));continue
        assert comp.returncode==0 and not comp.stdout and not comp.stderr,comp.stderr.decode(errors='replace')
        row=dict(source=source.name,compile=command,compile_exit=0)
        if name=='extern_store':row['object_only']=True;results.append(row);continue
        exe=f'build/{task}_{name}.exe';args=[]
        if name=='stack_limit':args=['iterative','0']
        if name=='bloodbank_cli':args=['init']
        cmd=[str(a/exe),*args]
        data=(folder/'input.txt').read_bytes()
        proc=subprocess.run(cmd,input=data,cwd=a,env=ENV,capture_output=True,timeout=180)
        assert proc.returncode==0,(source.name,proc.returncode,proc.stderr)
        stdout=folder/'outputs'/f'{name}.stdout.txt';stdout.write_bytes(proc.stdout)
        (folder/'outputs'/f'{name}.stderr.txt').write_bytes(proc.stderr)
        transcript=('$ '+subprocess.list2cmdline(command)+'\n$ '+subprocess.list2cmdline([exe,*args])+f' < {task}/input.txt\n').encode()+proc.stdout+proc.stderr
        (folder/'outputs'/f'{name}.transcript.txt').write_bytes(transcript)
        expected=folder/'expected'/f'{name}.txt'
        if expected.exists():assert proc.stdout==expected.read_bytes(),(task,name,'stdout mismatch')
        row.update(exit_code=proc.returncode,stdout_sha256=hashlib.sha256(proc.stdout).hexdigest(),exact_expected=expected.exists())
        results.append(row);print(f'CO{number} {task}/{source.name}: PASS',flush=True)
    (folder/'outputs/manifest.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('assignment',type=int);p.add_argument('task');v=p.parse_args();task(v.assignment,v.task)
