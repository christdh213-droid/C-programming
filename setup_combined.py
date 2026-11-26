from pathlib import Path
import subprocess,shutil
from docx import Document
import pypdf
R=Path(__file__).resolve().parent
def git(*a): subprocess.run(['git',*a],cwd=R,check=True)
dest=R/'Assignment2-CO2'
if (dest/'Q1').exists(): raise SystemExit('Combined layout already exists; no files moved.')
dest.mkdir(exist_ok=True)
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0')
for name in sorted(set(x.split('/')[0] for x in tracked if x)):
    if name.startswith('.'): continue
    git('mv','--',name,'Assignment2-CO2/'+name)
source=R.parent/'CSA02-1911260256-Assignment2'/'CSA02_1911260256_Assignment2_Report.docx'
target=dest/source.name
shutil.copy2(source,target)  # Preserve the user's current report, then edit only its URL.
d=Document(target)
for p in d.paragraphs:
    if 'https://github.com/<your-username>/CSA02-1911260256-Assignment2' in p.text:
        for run in p.runs:
            run.text=run.text.replace('https://github.com/<your-username>/CSA02-1911260256-Assignment2','https://github.com/christdh213-droid/C-programming')
d.save(target)
readme=dest/'README.md'; text=readme.read_text(encoding='utf-8').replace('https://github.com/<your-username>/CSA02-1911260256-Assignment2','https://github.com/christdh213-droid/C-programming')
text=text.replace('No origin was configured during preparation, so the report contains the requested editable GitHub placeholder.','The report cover now points to the combined C-programming GitHub repository.')
text=text.replace('This directory is a separate Git repository on `main`; existing DBMS work in the parent workspace is preserved.','This directory is Assignment 2 within the combined C-programming repository; its earlier progressive Git history is retained.')
readme.write_text(text,encoding='utf-8')
a=R/'Assignment3-CO3'; (a/'reference').mkdir(parents=True,exist_ok=True)
shutil.copy2(r'C:\Users\Chris\Downloads\CO3_Assignment_3.docx.pdf',a/'reference/CO3_Assignment_3.docx.pdf')
pdf=pypdf.PdfReader(a/'reference/CO3_Assignment_3.docx.pdf')
(a/'reference/assignment.txt').write_text('\n'.join(p.extract_text() for p in pdf.pages),encoding='utf-8')
for i in range(1,8):
    for sub in ('outputs','screenshots'): (a/f'Q{i}'/sub).mkdir(parents=True,exist_ok=True)
    (a/f'Q{i}'/'input.txt').write_text('')
(a/'environment').mkdir(exist_ok=True)
for prog in ('gcc','git','python'):
    r=subprocess.run([prog,'--version'],capture_output=True,check=True)
    (a/'environment'/f'{prog}.txt').write_bytes(r.stdout+r.stderr)
(R/'.gitignore').write_text('**/build/\n**/qa/render/\n**/__pycache__/\n*.exe\n~$*\n')
(R/'.gitattributes').write_text('**/outputs/* -text\n**/expected/* -text\n**/environment/* -text\n')
