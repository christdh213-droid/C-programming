"""Check all rendered evidence dimensions, DPI, coverage and report structure."""
from pathlib import Path
import json
from collections import defaultdict
from PIL import Image,ImageChops
from docx import Document
import pypdf
R=Path(__file__).resolve().parent
rows=json.loads((R/'qa/screenshots.json').read_text()); groups=defaultdict(list)
for row in rows:
    path=R/row['file']; im=Image.open(path).convert('RGB')
    assert im.size==(row['width'],row['height']) and im.width>=1800
    assert ImageChops.difference(im,Image.new('RGB',im.size,'#101720')).getbbox()
    assert all(abs(v-300)<1 for v in Image.open(path).info['dpi'])
    groups[row['source']].append(row)
for source,items in groups.items():
    next_line=1
    for row in sorted(items,key=lambda r:r['line_start']):
        assert row['line_start']==next_line
        next_line=row['line_end']+1
    assert next_line==len((R/source).read_text(encoding='utf-8').splitlines())+1
report=R/'CSA02_1911260256_Assignment2_Report.docx'
d=Document(report)
assert len(d.inline_shapes)==15  # 12 transcript images + 3 charts
text='\n'.join(p.text for p in d.paragraphs)
assert 'Chris Abraham George' in text and '1911260256' in text
assert 'Section:' not in text or 'Section: ____________________' in text
assert 'Submission Date:' not in text or 'Submission Date: ____________________' in text
assert 'https://github.com/christdh213-droid/C-programming' in text
pdf=pypdf.PdfReader(R/'qa/render/report.pdf')
assert all(len(p.extract_text().strip())>30 for p in pdf.pages)
source_count=len(list(R.glob('Q*/*.c')))
summary=dict(c_sources=source_count,transcript_images=len(rows),transcripts=len(groups),report_pages=len(pdf.pages),embedded_images=len(d.inline_shapes),image_dimensions_dpi_nonblank='PASS',all_transcript_lines_covered='PASS',cover_metadata='PASS',visual_review='All pages inspected; no clipping or overlap in final render. Renderer fallback: Microsoft Word read-only PDF export; bundled LibreOffice unavailable.')
(R/'qa/artifact_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
