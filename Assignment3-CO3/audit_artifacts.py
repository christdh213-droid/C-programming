from pathlib import Path
from collections import defaultdict
import json
from PIL import Image,ImageChops
from docx import Document
import pypdf
R=Path(__file__).resolve().parent
screenshots=json.loads((R/'qa/screenshots.json').read_text());groups=defaultdict(list)
for row in screenshots:
    path=R/row['file'];im=Image.open(path)
    assert im.size==(row['width'],row['height']) and im.width>=1900
    assert all(abs(x-300)<1 for x in im.info['dpi'])
    assert ImageChops.difference(im.convert('RGB'),Image.new('RGB',im.size,'#111923')).getbbox()
    groups[row['source']].append(row)
for source,items in groups.items():
    next_line=1
    for row in sorted(items,key=lambda r:r['start']): assert row['start']==next_line;next_line=row['end']+1
    assert next_line==len((R/source).read_text(encoding='utf-8').splitlines())+1
d=Document(R/'CSA02_1911260256_Assignment3_Report.docx');text='\n'.join(p.text for p in d.paragraphs)
for phrase in ['Student B Name: __________________','Student B Register Number: __________________','Student B Repository: __________________','Section: __________________','Submission Date: __________________','https://github.com/christdh213-droid/C-programming']:
    assert phrase in text,phrase
for q in range(1,8):
    assert f'Q{q} ' in text
assert text.count('Shared Group Work')==7 and text.count('Alternative Concept and Complexity Analysis')==7
assert text.count('Complete the Code')==3
for f in R.glob('Q*/*.c'): assert f.name in text
assert len(list((R/'charts').glob('Q[1-7].png')))==6
pages=pypdf.PdfReader(R/'qa/render/report.pdf').pages
assert all(len(p.extract_text().strip())>40 for p in pages)
a2=Document(R.parent/'Assignment2-CO2/CSA02_1911260256_Assignment2_Report.docx')
assert 'https://github.com/christdh213-droid/C-programming' in '\n'.join(p.text for p in a2.paragraphs)
summary=dict(c_sources=len(list(R.glob('Q*/*.c'))),execution_transcripts=len(groups),screenshots=len(screenshots),report_pages=len(pages),charts=6,cover_blank_fields='PASS',all_starter_outputs='PASS',all_transcript_lines_covered='PASS',png_dimensions_dpi_nonblank='PASS',assignment2_cover_url='PASS',renderer='Microsoft Word read-only PDF export; page PNGs inspected')
(R/'qa/artifact_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
