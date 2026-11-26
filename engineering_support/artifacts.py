from pathlib import Path
import json,textwrap
from PIL import Image,ImageDraw,ImageFont,ImageChops
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parent.parent
URL='https://github.com/christdh213-droid/C-programming'
def screenshots(root):
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',27);label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22);manifest=[]
    for source in sorted(root.glob('Task*/outputs/*.transcript.txt')):
        lines=source.read_text(encoding='utf-8',errors='replace').splitlines();dest=source.parent.parent/'screenshots';dest.mkdir(exist_ok=True)
        for first in range(0,len(lines),28):
            part=[line.expandtabs(8) for line in lines[first:first+28]];width=max(1900,int(max(font.getlength(line) for line in part))+110);height=110+len(part)*38
            im=Image.new('RGB',(width,height),'#101923');draw=ImageDraw.Draw(im);draw.text((40,22),f'{source.parent.parent.name} | {source.stem} | lines {first+1}-{first+len(part)}',font=label,fill='#91a4b5')
            for j,line in enumerate(part):draw.text((40,75+j*38),line,font=font,fill='#72e3ad' if line.startswith('$ ') else '#edf3f8');assert font.getbbox(line)[2]+40<width-30
            path=dest/f'{source.name.split(".")[0]}_{first//28+1:02}.png';im.save(path,dpi=(300,300));assert ImageChops.difference(im,Image.new('RGB',im.size,'#101923')).getbbox()
            manifest.append(dict(file=str(path.relative_to(root)),source=str(source.relative_to(root)),start=first+1,end=first+len(part),width=width,height=height,dpi=300,nonblank=True))
    (root/'qa/screenshots.json').write_text(json.dumps(manifest,indent=2)+'\n')
class Report:
    def __init__(self,root,number,title):
        self.root=root;self.number=number;self.d=Document();s=self.d.sections[0];s.page_width=Inches(8.27);s.page_height=Inches(11.69);s.top_margin=s.bottom_margin=Inches(.65);s.left_margin=s.right_margin=Inches(.7)
        for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
            style=self.d.styles[name];style.font.name='Calibri';style.font.color.rgb=RGBColor(0,0,0)
        self.d.styles['Normal'].font.size=Pt(10);self.d.styles['Normal'].paragraph_format.space_after=Pt(5);self.d.styles['Normal'].paragraph_format.line_spacing=1.05
        self.d.styles['Title'].font.size=Pt(25)
        for name,size in [('Heading 1',17),('Heading 2',12),('Heading 3',10.5)]:self.d.styles[name].font.size=Pt(size)
        self.d.add_paragraph(f'ASSIGNMENT {number} CO{number}','Title');self.d.add_paragraph(title,'Subtitle')
        self.p('CSA02 C Programming | Maximum Marks 50');self.p('Chris Abraham George\nRegister Number: 1911260256');self.p('Saveetha Institute of Medical and Technical Sciences\nSIMATS Engineering\nProgramme: B.E / B.Tech - CSE');self.p('Section: ____________________\nSubmission Date: ____________________');self.p('GitHub Repository Link: '+URL)
    def p(self,s):return self.d.add_paragraph(s)
    def h(self,s):return self.d.add_heading(s,2)
    def chapter(self,s):p=self.d.add_heading(s,1);p.paragraph_format.page_break_before=not s.startswith('Task05')
    def code(self,s,size=7.4):
        p=self.p('');p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(6);p.paragraph_format.keep_together=len(s.splitlines())<=12
        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F0F2F4');p._p.get_or_add_pPr().append(shade)
        lines=[]
        for line in s.rstrip().splitlines():lines.extend(textwrap.wrap(line.expandtabs(4),width=108,replace_whitespace=False,drop_whitespace=False,subsequent_indent='    ') or [''])
        run=p.add_run('\n'.join(lines));run.font.name='Consolas';run.font.size=Pt(size)
    def table(self,headers,rows):
        t=self.d.add_table(rows=1,cols=len(headers));t.autofit=True
        for c,v in zip(t.rows[0].cells,headers):c.text=str(v)
        for row in rows:
            for c,v in zip(t.add_row().cells,row):c.text=str(v)
        for i,row in enumerate(t.rows):
            pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
            if i==0:pr.append(OxmlElement('w:tblHeader'))
            for c in row.cells:
                cp=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'DCE8F0' if i==0 else ('F4F7F9' if i%2 else 'FFFFFF'));cp.append(sh);b=OxmlElement('w:tcBorders')
                for edge in ['top','left','bottom','right']:
                    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
                cp.append(b)
                for p in c.paragraphs:
                    p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(3)
                    for r in p.runs:r.font.size=Pt(8.5);r.bold=(i==0)
        self.p('')
    def picture(self,path,caption,width=6.75):
        p=self.p('');p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str(self.root/path),width=Inches(width));p=self.p(caption)
        for r in p.runs:r.font.size=Pt(8);r.italic=True
    def evidence(self,task):
        self.h('Execution evidence')
        for path in sorted((self.root/task/'outputs').glob('*.transcript.txt')):
            name=path.name.split('.')[0];self.picture(f'{task}/screenshots/{name}_01.png',f'{task} {name}: actual captured command and output. Full transcript and all image pages are stored in the task folder.')
    def sources(self,task):
        self.h('C source code');self.p('Long lines wrap for display. Compile the repository files; their source text is authoritative. The common support header is listed at the end of the report.')
        for source in sorted((self.root/task).glob('*.c')):self.d.add_heading(source.name,3);self.code(source.read_text(),7.0 if task=='Task04' else 7.4)
    def save(self):
        for root in [self.d.styles.element,self.d.element]:
            for border in list(root.iter(qn('w:pBdr'))):border.getparent().remove(border)
        footer=self.d.sections[0].footer.paragraphs[0];footer.alignment=2;r=footer.add_run('Page ');r.font.size=Pt(8);f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');footer._p.append(f)
        self.d.core_properties.author='Chris Abraham George';self.d.core_properties.title=f'CSA02 Assignment {self.number} CO{self.number}'
        path=self.root/f'CSA02_1911260256_Assignment{self.number}_Report.docx';self.d.save(path);return path
def readme(root,number,summary):
    commands=[]
    for manifest in sorted(root.glob('Task*/outputs/manifest.json')):
        for row in json.loads(manifest.read_text()):
            commands.append(' '.join(row['compile']))
            if 'exit_code' in row:commands.append(f"build/{manifest.parent.parent.name}_{Path(row['source']).stem}.exe < {manifest.parent.parent.name}/input.txt")
    compiler=(ROOT/'engineering_support/environment/gcc.txt').read_text().strip()
    (root/'README.md').write_text(f'''# CSA02 Assignment {number} CO{number}

Chris Abraham George | Register Number 1911260256  
SIMATS Engineering | B.E / B.Tech CSE | CSA02 C Programming | 50 Marks  
Repository: {URL}

## Exact detected GCC version

```text
{compiler}
```

## Reproduction

From the repository root use `python engineering_support/execute.py {number} TASK_NAME` for each task.
All C compilations use `-std=c11 -Wall -Wextra`. Inputs, exact stdout/stderr, compiler logs and manifests are retained per task.
Intentional compile failures and isolated stress/sanitizer probes are separately labelled. Zero measured CPU ticks stay zero.
For manual `<` redirection, use cmd.exe or another supporting shell; the Python runner works from PowerShell.

```text
{chr(10).join(commands)}
```

## Results

{summary}

## Evidence

- The Word report contains the full analysis, pseudocode, source code, measured tables and execution images.
- `qa/verification.txt` records independent checks; `qa/screenshots.json` records image dimensions, DPI and transcript-line coverage.
- Transcript images are 300-DPI dark-terminal renderings of actual captured commands/output, not OS-window photographs. Raw bytes remain authoritative.
- Complete-the-Code starters are preserved in `starter.txt`; only TODO blocks were filled. Fixtures include exact spaces and Windows CRLF.
- Cover Section and Submission Date fields are blank. The linked GitHub repository contains progressive task commits.
''',encoding='utf-8')
