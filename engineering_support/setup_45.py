from pathlib import Path
import subprocess,shutil,sys
import pypdf
R=Path(__file__).resolve().parent.parent
env=R/'engineering_support/environment';env.mkdir(parents=True,exist_ok=True)
gcc=r'C:\msys64\ucrt64\bin\gcc.exe'
result=subprocess.run([gcc,'--version'],capture_output=True,check=True)
(env/'gcc.txt').write_bytes(result.stdout+result.stderr)
for number,tasks in [(4,[f'Task{i:02}' for i in range(1,7)]),(5,[f'TaskB{i}' for i in range(1,5)])]:
    a=R/f'Assignment{number}-CO{number}';(a/'reference').mkdir(parents=True,exist_ok=True)
    source=Path(r'C:\Users\Chris\Downloads')/f'CO{number}_Assignment_{number}.docx.pdf'
    shutil.copy2(source,a/'reference'/source.name)
    text='\n'.join(p.extract_text() for p in pypdf.PdfReader(source).pages)
    (a/'reference/assignment.txt').write_text(text,encoding='utf-8')
    for task in tasks:
        for directory in ('outputs','screenshots'): (a/task/directory).mkdir(parents=True,exist_ok=True)
        (a/task/'input.txt').touch()
    for directory in ('charts','qa'): (a/directory).mkdir(exist_ok=True)
print(result.stdout.decode())
