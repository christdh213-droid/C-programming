from pathlib import Path
from collections import defaultdict
import sys,json
from PIL import Image,ImageChops,ImageDraw
from docx import Document
import pypdf
number=int(sys.argv[1]);root=Path(__file__).resolve().parent.parent/f'Assignment{number}-CO{number}'
manifest=json.loads((root/'qa/screenshots.json').read_text());groups=defaultdict(list)
for row in manifest:
    im=Image.open(root/row['file']);assert im.size==(row['width'],row['height']) and im.width>=1900
    assert all(abs(x-300)<1 for x in im.info['dpi'])
    assert ImageChops.difference(im.convert('RGB'),Image.new('RGB',im.size,'#101923')).getbbox()
    groups[row['source']].append(row)
for source,rows in groups.items():
    next_line=1
    for row in sorted(rows,key=lambda x:x['start']):assert row['start']==next_line;next_line=row['end']+1
    assert next_line==len((root/source).read_text(encoding='utf-8',errors='replace').splitlines())+1
doc=Document(root/f'CSA02_1911260256_Assignment{number}_Report.docx');text='\n'.join(p.text for p in doc.paragraphs)
for term in ('1911260256','Section: ____________________','Submission Date: ____________________','https://github.com/christdh213-droid/C-programming'):assert term in text
pdf=pypdf.PdfReader(root/'qa/render/report.pdf');pages=len(pdf.pages)
assert all(len(p.extract_text().strip())>25 for p in pdf.pages)
summary=dict(assignment=number,report_pages=pages,transcripts=len(groups),screenshots=len(manifest),dimensions_dpi_nonblank='PASS',transcript_coverage='PASS',cover_fields='PASS')
(root/'qa/artifact_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
columns=6;thumb=Image.new('RGB',(columns*210,((pages+columns-1)//columns)*320),'#bbb');draw=ImageDraw.Draw(thumb)
for i in range(pages):
    path=root/'qa/render'/f'page-{i+1:02}.png';im=Image.open(path);im.thumbnail((210,297));thumb.paste(im,((i%columns)*210,(i//columns)*320+22));draw.text(((i%columns)*210+5,(i//columns)*320+5),str(i+1),fill='black')
thumb.save(root/'qa/render/overview.png')
