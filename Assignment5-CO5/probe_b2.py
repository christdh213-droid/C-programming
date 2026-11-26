from pathlib import Path
import sys,subprocess,json,os,stat,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'engineering_support'))
from execute import ENV
a=Path(__file__).resolve().parent;f=a/'TaskB2';rows=[];trans=[]
(f/'inputs').mkdir(exist_ok=True);long=b'X'*256+b'\n';(f/'inputs/overlong.txt').write_bytes(long);(f/'inputs/name.txt').write_bytes(b'Chris Abraham George\n')
def run(label,args,data=b'',code=0,env=None):
    cmd=[str(a/'build/TaskB2_bloodbank_cli.exe'),*args];p=subprocess.run(cmd,input=data,cwd=a,env=env or ENV,capture_output=True,timeout=20);assert p.returncode==code,(label,p.returncode,p.stderr)
    for ext,b in [('stdout',p.stdout),('stderr',p.stderr)]: (f/'outputs'/f'{label}.{ext}.txt').write_bytes(b)
    trans.append(('$ '+subprocess.list2cmdline(cmd)+f' [case={label}]\n').encode()+p.stdout+p.stderr+f'EXIT_CODE {p.returncode}\n'.encode());rows.append(dict(case=label,args=args,expected=code,actual=p.returncode))
run('find',['find','O+']);run('issue',['issue','A-','2']);run('no_args',[],code=2);run('too_many',['find','O+','extra'],code=2);run('bad_group',['find','ZZ'],code=2)
for units in ['-1','0','two','999999999999999999999','999']:run('units_'+units,['issue','O+',units],code=2)
run('long_name',['register','O+'],long,2);run('valid_name',['register','O+'],b'Chris Abraham George\n');run('pointers',['pointers'])
env=dict(ENV);env['BLOODBANK_STOCK']='TaskB2/missing.bin';run('missing',['find','O+'],code=1,env=env)
readonly=f/'readonly.bin';shutil.copyfile(f/'stock.bin',readonly);os.chmod(readonly,stat.S_IREAD);env['BLOODBANK_STOCK']='TaskB2/readonly.bin'
try:run('readonly',['issue','O+','1'],code=1,env=env)
finally:os.chmod(readonly,stat.S_IWRITE|stat.S_IREAD)
(f/'corrupt.bin').write_bytes(b'bad');env['BLOODBANK_STOCK']='TaskB2/corrupt.bin';run('corrupt',['find','O+'],code=1,env=env)
(f/'outputs/adversarial_cases.transcript.txt').write_bytes(b''.join(trans));(f/'outputs/adversarial_cases.json').write_text(json.dumps(rows,indent=2)+'\n')
# Probe the installed compiler rather than claiming unsupported instrumentation worked.
checks=[]
for source,flags in [('adversarial_scanf_demo.c','address'),('bloodbank_cli.c','address,leak')]:
    cmd=['gcc','-std=c11','-Wall','-Wextra','-fsanitize='+flags,'TaskB2/'+source,'-o','build/asan_'+Path(source).stem+'.exe'];p=subprocess.run(cmd,cwd=a,env=ENV,capture_output=True)
    checks.append(('$ '+' '.join(cmd)+'\n').encode()+p.stdout+p.stderr+f'EXIT_CODE {p.returncode}\n'.encode())
    if p.returncode==0:
        args=['unsafe'] if source.startswith('adversarial') else ['find','O+'];q=subprocess.run([str(a/('build/asan_'+Path(source).stem+'.exe')),*args],input=long,cwd=a,env=ENV,capture_output=True,timeout=20);checks.append(q.stdout+q.stderr+f'EXIT_CODE {q.returncode}\n'.encode())
for tool in ['valgrind','wsl','clang']:checks.append(f'{tool} executable: {shutil.which(tool)}\n'.encode())
(f/'outputs/sanitizer_probe.transcript.txt').write_bytes(b''.join(checks));print(b''.join(checks).decode(errors='replace'))
# Native unsafe child is separate; its result is not a sanitizer diagnosis.
cmd=[str(a/'build/TaskB2_adversarial_scanf_demo.exe'),'unsafe'];p=subprocess.run(cmd,input=long,cwd=a,env=ENV,capture_output=True,timeout=20)
(f/'outputs/unsafe_native.transcript.txt').write_bytes(('$ '+subprocess.list2cmdline(cmd)+' < TaskB2/inputs/overlong.txt\n').encode()+p.stdout+p.stderr+f'EXIT_CODE {p.returncode} (0x{p.returncode&0xffffffff:08X})\nNot sanitizer-instrumented; UB outcome is not portable.\n'.encode())
print('CLI cases:',len(rows),'all expected exit codes; unsafe child:',p.returncode)
