from pathlib import Path
import sys,subprocess,json
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'engineering_support'))
from execute import ENV,record
a=Path(__file__).resolve().parent;f=a/'TaskB1';rows=[];trans=[]
for n in [1000*2**i for i in range(12)]:
    cmd=[str(a/'build/TaskB1_stack_limit.exe'),'linear',str(n)];p=subprocess.run(cmd,cwd=a,env=ENV,capture_output=True,timeout=30)
    trans.append(('$ '+' '.join(cmd)+'\n').encode()+p.stdout+p.stderr+f'EXIT_CODE {p.returncode} (0x{p.returncode&0xffffffff:08X})\n'.encode());rows.append(dict(n=n,exit=p.returncode))
    if p.returncode:
        assert p.returncode&0xffffffff==0xC00000FD,rows[-1]
        for m in [n,2*n]:
            cmd=[str(a/'build/TaskB1_stack_limit.exe'),'iterative',str(m)];q=subprocess.run(cmd,cwd=a,env=ENV,capture_output=True,timeout=30);assert q.returncode==0
            trans.append(('$ '+' '.join(cmd)+'\n').encode()+q.stdout+q.stderr+b'EXIT_CODE 0\n')
        break
else:raise AssertionError('No observed stack overflow in bounded sweep')
(f/'outputs/stack_stress.transcript.txt').write_bytes(b''.join(trans));(f/'outputs/stack_stress.json').write_text(json.dumps(rows,indent=2)+'\n');print(b''.join(trans).decode())
