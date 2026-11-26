from pathlib import Path
import sys,subprocess,re,json
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'engineering_support'))
from execute import ENV
a=Path(__file__).resolve().parent;f=a/'TaskB4'
cmd=[str(a/'build/TaskB4_nightly_report.exe'),'stream'];p=subprocess.run(cmd,cwd=a,env=ENV,capture_output=True,timeout=30);assert p.returncode==0
(f/'outputs/stream.stdout.txt').write_bytes(p.stdout);(f/'outputs/stream.stderr.txt').write_bytes(p.stderr);(f/'outputs/stream.transcript.txt').write_bytes(('$ '+subprocess.list2cmdline(cmd)+'\n').encode()+p.stdout+p.stderr)
mem=(f/'outputs/nightly_report.stdout.txt').read_bytes();assert re.search(rb'eligible=(\d+) youngest_id=(\d+)',mem).groups()==re.search(rb'eligible=(\d+) youngest_id=(\d+)',p.stdout).groups()
assert re.findall(rb'HOSPITAL.*',mem)==re.findall(rb'HOSPITAL.*',p.stdout)
cmd=['gcc','-std=c11','-Wall','-Wextra','-fsanitize=address,leak','TaskB4/nightly_report.c','-o','build/asan_nightly.exe','-lpsapi'];p=subprocess.run(cmd,cwd=a,env=ENV,capture_output=True)
log=('$ '+' '.join(cmd)+'\n').encode()+p.stdout+p.stderr+f'EXIT_CODE {p.returncode}\n'.encode()
if p.returncode==0:
    q=subprocess.run([str(a/'build/asan_nightly.exe')],cwd=a,env=ENV,capture_output=True,timeout=60);log+=q.stdout+q.stderr+f'EXIT_CODE {q.returncode}\n'.encode()
(f/'outputs/sanitizer_probe.transcript.txt').write_bytes(log);print(log.decode(errors='replace'));print('Memory/stream eligibility and all 25 hospital totals: PASS')
