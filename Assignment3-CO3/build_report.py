"""Generate charts, transcript images, README files and the evidence-based Word report."""
from pathlib import Path
import json,re,textwrap,csv,subprocess
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont,ImageChops
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parent
URL='https://github.com/christdh213-droid/C-programming'
FILE='CSA02_1911260256_Assignment3_Report.docx'
DATA=json.loads((R/'qa/data.json').read_text())
def raw(q,name): return (R/q/'outputs'/f'{name}.stdout.txt').read_text()
def rows(q,**filters): return [r for r in DATA[q] if all(r[k]==str(v) for k,v in filters.items())]

def images():
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',27)
    label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',22)
    manifest=[]
    for source in sorted(R.glob('Q*/outputs/*.transcript.txt')):
        lines=source.read_text(encoding='utf-8').splitlines();dest=source.parent.parent/'screenshots'
        for old in dest.glob(source.name.split('.')[0]+'_*.png'): old.unlink()
        for first in range(0,len(lines),30):
            part=[line.expandtabs(8) for line in lines[first:first+30]]
            width=max(1900,int(max(font.getlength(line) for line in part))+100);height=110+len(part)*38
            im=Image.new('RGB',(width,height),'#111923');draw=ImageDraw.Draw(im)
            draw.text((40,22),f'{source.parent.parent.name} | {source.stem} | lines {first+1}-{first+len(part)}',font=label,fill='#91a4b5')
            for j,line in enumerate(part):
                draw.text((40,75+j*38),line,font=font,fill='#73e4af' if line.startswith('$ ') else '#edf2f7')
                assert font.getbbox(line)[2]+40<width-30
            path=dest/f'{source.name.split(".")[0]}_{first//30+1:02}.png';im.save(path,dpi=(300,300))
            assert ImageChops.difference(im,Image.new('RGB',im.size,'#111923')).getbbox()
            manifest.append(dict(file=str(path.relative_to(R)),source=str(source.relative_to(R)),start=first+1,end=first+len(part),width=width,height=height,dpi=300,nonblank=True,tab_stop=8))
    (R/'qa/screenshots.json').write_text(json.dumps(manifest,indent=2)+'\n')

def charts():
    dest=R/'charts';dest.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,q): fig.tight_layout();fig.savefig(dest/f'{q}.png',dpi=300);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.5))
    for method in ['linear','binary','hash','interpolation']:
        r=rows('Q1',query='missing',method=method);ax.plot([int(x['n']) for x in r],[int(x['probes']) for x in r],'o-',label=method)
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Catalogue entries');ax.set_ylabel('Probes for missing key');ax.legend(ncol=2);save(fig,'Q1')
    fig,axes=plt.subplots(2,2,figsize=(7,5))
    for order,ax in zip(['sorted','nearly','reverse','random'],axes.flat):
        for method in ['bubble','selection','insertion','counting']:
            r=rows('Q2',order=order,method=method);ax.plot([int(x['n']) for x in r],[int(x['comparisons']) for x in r],'o-',label=method)
        ax.set_xscale('log');ax.set_yscale('log');ax.set_title(order);ax.set_xlabel('n');ax.set_ylabel('Key comparisons')
    axes[0,0].legend(fontsize=7);save(fig,'Q2')
    fig,axes=plt.subplots(1,2,figsize=(7,3.3))
    for method in ['merge','concat_qsort','inplace']:
        r=rows('Q3',method=method);axes[0].plot([int(x['n']) for x in r],[int(x['comparisons']) for x in r],'o-',label=method)
    for method in ['merge','inplace']:
        r=rows('Q3',method=method);axes[1].plot([int(x['n']) for x in r],[int(x['writes']) for x in r],'o-',label=method)
    for ax,title in zip(axes,['Score comparisons','Known record writes']): ax.set_xscale('log');ax.set_yscale('log');ax.set_title(title);ax.set_xlabel('Entries per campus');ax.legend(fontsize=7)
    save(fig,'Q3')
    fig,ax=plt.subplots(figsize=(7,3.3));r=DATA['Q4'];bars=ax.bar([x['order'] for x in r],[float(x['seconds']) for x in r],color=['#285d83','#b46c32'])
    for bar,x in zip(bars,r): ax.annotate(x['seconds']+' s',(bar.get_x()+bar.get_width()/2,bar.get_height()),ha='center',va='bottom',fontsize=9)
    ax.margins(y=.2);ax.set_ylabel('Measured process CPU seconds');ax.set_title('2000 x 2000 doubles, five traversals');save(fig,'Q4')
    fig,axes=plt.subplots(1,2,figsize=(7,3.3))
    for method in ['direct_insertion','index_insertion','pointer_qsort']:
        r=rows('Q6',method=method);axes[0].plot([int(x['n']) for x in r],[int(x['comparisons']) for x in r],'o-',label=method)
        axes[1].plot([int(x['n']) for x in r],[int(x['copied_chars']) for x in r],'o-',label=method)
    axes[0].set_yscale('log');axes[1].set_yscale('symlog',linthresh=1)
    for ax,title in zip(axes,['strcmp calls','Characters copied incl NUL']): ax.set_xscale('log');ax.set_xlabel('Names');ax.set_title(title)
    axes[0].legend(fontsize=7);save(fig,'Q6')
    fig,ax=plt.subplots(figsize=(7,3.5));labels=[]
    for i,method in enumerate(['count_array','name_search','sort_count']):
        r=[rows('Q7',votes=500000,candidates=c,method=method)[0] for c in [12,500]]
        bars=ax.bar([j+(i-1)*.23 for j in range(2)],[float(x['seconds']) for x in r],.23,label=method)
        for bar,x in zip(bars,r): ax.annotate(x['seconds'],(bar.get_x()+bar.get_width()/2,bar.get_height()),ha='center',va='bottom',fontsize=7,rotation=90)
    ax.set_xticks([0,1],['12 candidates','500 candidates']);ax.set_ylabel('Measured process CPU seconds');ax.margins(y=.35);ax.legend(fontsize=8);save(fig,'Q7')
    for q,records in DATA.items():
        with (dest/f'{q}_measurements.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)

d=Document();sec=d.sections[0];sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
sec.top_margin=sec.bottom_margin=Inches(.65);sec.left_margin=sec.right_margin=Inches(.7)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
    style=d.styles[name];style.font.name='Calibri';style.font.color.rgb=RGBColor(0,0,0)
d.styles['Normal'].font.size=Pt(10);d.styles['Normal'].paragraph_format.space_after=Pt(5);d.styles['Normal'].paragraph_format.line_spacing=1.04
d.styles['Title'].font.size=Pt(25)
for name,size in [('Heading 1',17),('Heading 2',12),('Heading 3',10.5)]: d.styles[name].font.size=Pt(size)
def p(s): return d.add_paragraph(s)
def h(s): return d.add_heading(s,2)
def chapter(s):
    para=d.add_heading(s,1);para.paragraph_format.page_break_before=True
def code(s,size=7.4):
    para=p('');para.paragraph_format.line_spacing=1;para.paragraph_format.space_after=Pt(6)
    para.paragraph_format.keep_together=len(s.splitlines())<12
    pr=para._p.get_or_add_pPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F0F2F4');pr.append(shade)
    lines=[]
    for line in s.rstrip().splitlines():
        lines.extend(textwrap.wrap(line.expandtabs(4),width=110,replace_whitespace=False,drop_whitespace=False,subsequent_indent='    ') or [''])
    run=para.add_run('\n'.join(lines));run.font.name='Consolas';run.font.size=Pt(size)
def table(headers,records,widths=None):
    t=d.add_table(rows=1,cols=len(headers));t.autofit=False
    if widths:
        for c,w in zip(t.columns,widths): c.width=Inches(w)
    for c,v in zip(t.rows[0].cells,headers): c.text=str(v)
    for record in records:
        for c,v in zip(t.add_row().cells,record):c.text=str(v)
    for i,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr();no=OxmlElement('w:cantSplit');trpr.append(no)
        if i==0: trpr.append(OxmlElement('w:tblHeader'))
        for j,c in enumerate(row.cells):
            if widths:c.width=Inches(widths[j])
            pr=c._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DCE8F0' if i==0 else ('F4F7F9' if i%2 else 'FFFFFF'));pr.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                border=OxmlElement('w:'+edge);border.set(qn('w:val'),'single');border.set(qn('w:sz'),'4');border.set(qn('w:color'),'D9D9D9');borders.append(border)
            pr.append(borders)
            margins=OxmlElement('w:tcMar')
            for edge in ['top','bottom','left','right']:
                m=OxmlElement('w:'+edge);m.set(qn('w:w'),'65');m.set(qn('w:type'),'dxa');margins.append(m)
            pr.append(margins)
            for para in c.paragraphs:
                para.paragraph_format.space_before=Pt(2);para.paragraph_format.space_after=Pt(2);para.paragraph_format.line_spacing=1
                for run in para.runs:run.font.size=Pt(8);run.bold=(i==0)
    p('')
def picture(path,caption):
    para=p('');para.paragraph_format.keep_with_next=True;para.add_run().add_picture(str(R/path),width=Inches(6.75))
    para=p(caption)
    for r in para.runs:r.italic=True;r.font.size=Pt(8)
def chart(q): picture(f'charts/{q}.png',f'{q} chart generated from captured measurements. CPU values of zero mean zero measured clock ticks.')
def shots(q):
    h('Execution evidence')
    for source in sorted((R/q).glob('*.c')):
        picture(f'{q}/screenshots/{source.stem}_01.png',f'{source.name}: actual compile command, input redirection and stdout. Full paginated evidence is in {q}/screenshots; exact bytes are in {q}/outputs.')
def sources(q):
    h('C source code')
    p('Long lines wrap for display. Compile the repository files, which retain their exact source text. Sources include the common lab.h helpers listed in the reproduction section.')
    for source in sorted((R/q).glob('*.c')):d.add_heading(source.name,3);code(source.read_text())
def measured(q,fields,headers): table(headers,[[row[k] for k in fields] for row in DATA[q]])

def report():
    d.add_paragraph('ASSIGNMENT 3 CO3','Title');d.add_paragraph('CSA02 C Programming','Subtitle')
    p('Pair Work | Maximum Marks 50')
    p('Saveetha Institute of Medical and Technical Sciences\nSIMATS Engineering')
    p('Programme: B.E / B.Tech - CSE')
    p('Student A: Chris Abraham George\nRegister Number: 1911260256\nRepository: '+URL)
    p('Student B Name: ______________________________\nStudent B Register Number: ____________________\nStudent B Repository: __________________________')
    p('Section: ____________________\nSubmission Date: ____________________')
    chapter('Mark distribution and individual contribution record')
    p('The experiments examine searching, sorting, merging, rainfall arrays, text handling and election counting. All final programs compile with the detected GCC using -std=c11 -O2 -Wall -Wextra and execute without compiler diagnostics. The report separates design, measurements and joint decisions under the prescribed pair-work roles.')
    table(['Question','Area','Level','Marks'],[['Q1','Catalogue search','K4',6],['Q2','Seating sorts','K4',7],['Q3','Merit merging','K4',7],['Q4','Rainfall arrays','K4',7],['Q5','Character processing','K4',6],['Q6','Name directory','K4',7],['Q7','Election design','K5',10],['Total','','',50]],[.65,4.75,.65,.65])
    h('Individual Contribution Record')
    p('The record identifies each role’s primary responsibility for every question. The following chapters contain the corresponding design and evidence for pair review.')
    table(['Question','Student A primary responsibility','Student B primary responsibility','Joint'],[
        ['Q1','Search pseudocode; mathematical comparison bounds','Generated catalogue measurements and charts','Daily insertion trade-off'],
        ['Q2','Hand traces; early exit; stability','Four input orders; counts; comparisons','20 late registrations'],
        ['Q3','Bounds; counts; storage; edge cases','Stable merge design; tail handling','In-place merge decision'],
        ['Q4','Row-major addresses; cache; 3D extension','Four computations; hand check; timing','2D versus separate rows'],
        ['Q5','NUL; manual algorithms; length and mutability','Library comparison; safe truncation','Custom versus standard library'],
        ['Q6','Copy/count measurements; length boundaries; search','Ordering; case folding; duplicates','Index and pointer trade-off'],
        ['Q7','Stage 2 count, ranking and tie design','Stage 3 implementation and measurement','Stage 1 requirements and Stage 4 defence']],[.55,2.2,2.35,1.6])
    h('Environment and measurement method')
    code((R/'environment/gcc.txt').read_text(),8)
    p((R/'environment/git.txt').read_text().strip()+'; '+(R/'environment/python.txt').read_text().strip()+'. clock() reports process CPU time with CLOCKS_PER_SEC=1000 on this target. Times are single captured runs or explicitly labelled repeated batches, not statistical estimates. Zero denotes zero measured ticks; no nonzero value is substituted. Counts are source-level operations, and instrumentation contributes to runtime.')
    p('PREDICTIONS.md records predictions before execution. Complete-the-Code checks preserve the supplied main functions and compare raw stdout including trailing spaces and CRLF newlines. Separate driver files add tests without editing those main functions. Transcript PNGs render the real captured commands and output at 300 DPI; tabs use terminal tab stops of eight columns. Hashes and the independent verification summary accompany the evidence.')
    chapter('Q1 Searching a Library Catalogue')
    h('Shared Group Work')
    p('The ten-book trial searches an unsorted list linearly and a sorted copy with binary search. Successful keys occur at the beginning, middle and end of the unsorted trial; 1400 is missing. Linear search needs 1,6,10,10 equality tests respectively; binary search on the sorted catalogue needs 3,3,1,4 midpoint visits for these same four keys. A midpoint visit is the assignment’s “comparison” unit; it may execute both == and < in C.')
    h('Student A')
    code('LINEAR(a,n,key):\n  for i = 0..n-1: if a[i] == key: return i\n  return -1\nBINARY(a,n,key):\n  low=0; high=n-1\n  while low<=high:\n    mid=low+(high-low)/2\n    if a[mid]==key: return mid\n    if a[mid]<key: low=mid+1\n    else: high=mid-1\n  return -1',8)
    p('Linear search has best 1 and worst n comparisons. For a uniformly selected successful position, the mean is (1+2+...+n)/n=(n+1)/2; a missing key needs n. Binary search requires sorted order because discarding half the array relies on every value on that side being smaller or larger. Its best case is one midpoint visit. Repeated halving gives worst floor(log2 n)+1 visits for nonempty n; its uniform successful average is the mean depth of the balanced search tree, Θ(log n). For a perfect tree n=2^h-1, the exact mean is ((h-1)2^h+1)/(2^h-1).')
    p('For 100000 entries, the prediction is linear worst 100000 and mean 50000.5; binary worst 17 and mean on the order of 16. low+(high-low)/2 avoids the possible signed overflow in low+high when bounds are valid nonnegative indices. Generated arrays have values 1000+2i, so both interpolation and modular hashing receive a favourable regular distribution.')
    h('Student B')
    measured('Q1',['n','query','method','found','probes','reps','seconds'],['n','Query','Method','Found','Probes','Batch reps','Batch CPU s'])
    for line in raw('Q1','library_search_lab').splitlines():
        if line.startswith('AVERAGE'):p(line)
    p('Every successful key is measured for the exact binary mean: 15.689460 visits at 100000 entries, agreeing with the logarithmic prediction. Last-key and missing-key searches reach 17 visits at that size. A missing key does not always follow the deepest path: the generated 10000-entry missing query takes 13 visits, whereas its last key takes 14. The supplied ten-book missing key 1400 does follow a deepest four-visit path.')
    chart('Q1')
    h('Complete the Code')
    code(raw('Q1','complete_the_code'),8)
    p('The exact output fixture passes: key/index/steps are 1021/0/3, 1305/5/3, 1533/9/4 and 1400/-1/4. The fourth search empties the interval after four midpoint comparisons, matching the worst successful depth for this catalogue.')
    h('Joint Conclusion and Decision')
    p('Keep a sorted array when searches greatly outnumber additions. Inserting one book can shift O(n) elements, so the decision needs the daily query/addition counts, catalogue size, batch-update opportunities, latency target and memory budget. Batch append followed by sorting or merging can amortize additions; a hash index offers faster average lookup if sorted traversal is unnecessary.')
    h('Alternative Concept and Complexity Analysis')
    p('The hash table uses key % capacity, then probes consecutive slots until it finds the key or an empty slot. Capacity is 2n+1 and zero is reserved as empty because accession numbers are positive. It uses O(n) extra storage, expected O(1) lookup at controlled load, and O(n) worst-case probes. The collision test with 11,22,33,44,55 in capacity 11 needs five probes for 55 and six for missing 66, demonstrating clustering. Interpolation estimates position from endpoint values; it has expected O(log log n) lookup for approximately uniform keys, O(n) worst case and O(1) auxiliary space. Endpoint guards, equal-endpoint handling and widened arithmetic protect the implementation. Binary search guarantees O(log n) time with O(1) auxiliary space on a sorted array; preprocessing costs O(n log n) if sorting is needed. One-probe interpolation results here must not be generalized to skewed catalogues.')
    shots('Q1');sources('Q1')
    chapter('Q2 Sorting the Examination Hall Seating Register')
    h('Shared Group Work')
    p('Bubble, selection and insertion sorts run on identical arrays for n=100,1000,10000. Sorted and reverse inputs are permutations of 0..n-1; nearly sorted inputs use ten deterministic adjacent swaps; random inputs use a fixed-seed shuffle. Counts distinguish key comparisons, exchanges, shifts and writes. Counting sort is also executed; its recorded comparisons are the max-key scan, not a comparison-sort workload.')
    h('Student A')
    table(['Pass','Bubble hand trace','Selection hand trace','Insertion hand trace'],[
        [0,'6 2 5 1 4 3','6 2 5 1 4 3','6 2 5 1 4 3'],[1,'2 5 1 4 3 6','1 2 5 6 4 3','2 6 5 1 4 3'],[2,'2 1 4 3 5 6','1 2 5 6 4 3','2 5 6 1 4 3'],[3,'1 2 3 4 5 6','1 2 3 6 4 5','1 2 5 6 4 3'],[4,'unchanged and stop','1 2 3 4 6 5','1 2 4 5 6 3'],[5,'not executed','1 2 3 4 5 6','1 2 3 4 5 6']])
    p('The executed trace agrees with the hand trace: bubble makes 14 comparisons and 10 swaps; selection makes 15 comparisons and 4 swaps; insertion makes 13 comparisons and 10 shifts. Bubble’s changed flag proves the array is sorted when a full pass makes no exchange. Insertion shifts only elements greater than the current key, so work is O(n+I) for I inversions. Bubble using > and insertion shifting only > are stable; ordinary minimum-swap selection sort can reorder equal keys. Stable order matters if register records have equal priority/marks and their earlier order must be retained.')
    h('Student B')
    measured('Q2',['n','order','method','comparisons','swaps','shifts','writes','seconds'],['n','Order','Method','Comparisons','Swaps','Shifts','Writes','CPU s'])
    chart('Q2')
    p('Selection always makes n(n-1)/2 comparisons, even on sorted input, but moves few records. On sorted input bubble and insertion tie at n-1 comparisons; bubble performs no array writes. For nearly sorted data insertion uses n-1 plus the few shifts, while bubble needs another pass. On reverse input all three comparison sorts make n(n-1)/2 comparisons; insertion shifts instead of exchanging pairs. On random 10000 input insertion uses 23037015 comparisons versus bubble’s 49994504 and selection’s 49995000. Small zero-tick timing ties cannot identify a fastest algorithm. Counting sort benefits from the deliberately small nonnegative key range and is a strong option across all four orders when that range is guaranteed.')
    h('Joint Conclusion and Decision')
    p('For 1000 sorted registrations plus 20 late entries, recommend insertion sort if key range assumptions are unavailable. It shifts only displaced records; the measured test requires 11499 comparisons and 10480 shifts, versus bubble’s 519500 and selection’s 519690 comparisons. Selection’s small swap count is not evidence of low comparison work. Counting sort uses only 1019 max-scan comparisons here, but needs a bounded range and frequency storage. Bubble’s unexpectedly high work on just 20 additions reflects small late keys moving left only one position per pass.')
    h('Alternative Concept and Complexity Analysis')
    code('max = maximum key\nallocate frequency[0..max] initialized to zero\nfor each value: frequency[value]++\nfor value=0..max: emit value frequency[value] times',8)
    p('Counting sort takes O(n+k) time and O(k) frequency space for a range of k possible nonnegative integers. The reconstruction used here sorts bare integers; stable sorting of full records would normally add O(n) output space and cumulative counts. A huge sparse range, negative unadjusted keys or non-integer identifiers makes this simple version unsuitable. Bubble and insertion have O(n) best and O(n²) worst time; selection is Θ(n²) for all orders. Each comparison sort uses O(1) auxiliary space. Swaps, shifts and histogram writes are different units, so no claim treats their counts as interchangeable.')
    shots('Q2');sources('Q2')
    chapter('Q3 Merging Two Merit Lists')
    h('Shared Group Work')
    p('Two descending lists are merged by advancing one source cursor for each output placement. Tagged test entries expose equal-score order: the first 91 comes from Campus A before Campus B, and original order within each campus is preserved. Tests cover unequal lengths, both empty, either empty and all equal scores.')
    h('Student B')
    code('i=j=k=0\nwhile i<m and j<n:\n  if A[i].score >= B[j].score: output[k++]=A[i++]\n  else: output[k++]=B[j++]\nwhile i<m: output[k++]=A[i++]\nwhile j<n: output[k++]=B[j++]',8)
    p('The invariant is that the output prefix contains the largest consumed entries in descending order. Selecting the greater head preserves it, and after one list ends the other tail is already ordered. Each loop placement uses at most one score comparison. An unselected head may be compared repeatedly with several entries from the other list; the assignment’s phrase “each element compared at most once” is therefore not literally true. Each element is copied to output exactly once. Using >= gives Campus A precedence on equal scores and preserves both campuses’ internal order.')
    h('Student A')
    p('For nonempty lists, the best head-comparison count is min(m,n), when one list exhausts immediately; the maximum is m+n-1. An empty list needs zero head comparisons. There are exactly m+n output writes. The interleaved benchmarks attain 2n-1 comparisons; the simple in-place method has the same score-comparison count on these inputs but must move a quadratic number of entries.')
    measured('Q3',['m','n','method','comparisons','writes','aux_bytes','seconds'],['m','n','Method','Comparisons','Known writes','Aux record bytes','CPU s'])
    p('The Entry record is 12 bytes on this target. For n=10000 per campus, merge writes 20000 records into a 240000-byte output, whereas in-place merging writes 50004999 records while using a 12-byte temporary. The in-place buffer holding the already combined records is not counted as auxiliary memory. Concat+qsort includes copying inputs and sorting in its timer; the in-place timer assumes the combined buffer already exists. qsort internal moves and scratch storage are not observable through the comparison callback and are reported as NA/implementation dependent.')
    chart('Q3')
    h('Complete the Code')
    code(raw('Q3','complete_the_code')+raw('Q3','starter_extra_tests'),8)
    p('The supplied main output matches exactly, including the trailing space. The separate driver calls the actual completed merge with an empty Campus A and then with both lists empty. The first copies 95,91,80; the second returns zero. Neither test changes the supplied main.')
    h('Joint Conclusion and Decision')
    p('Use the third-array merge when predictable linear work and stable ties matter. Prefer simple in-place merging only when the combined array already exists, memory is the binding constraint and the extra shifts are acceptable. The measured large case illustrates the cost of removing the output array. More advanced in-place algorithms exist but add implementation complexity beyond this simple redesign.')
    h('Alternative Concept and Complexity Analysis')
    p('Merge is O(m+n) time and O(m+n) output space. Copying both lists and qsort generally costs O((m+n) log(m+n)) comparisons with O(m+n) combined storage, plus implementation-dependent qsort working memory. Standard C does not require qsort to use quicksort or guarantee a particular asymptotic bound; the stated comparison-sort bound is the usual intended model, with the actual callback count recorded separately. qsort is not stable when comparing score alone. The simple in-place insertion merge is O(m*n+m+n) time, commonly written O(m*n) for nonempty growing lists, and O(1) auxiliary storage beyond its combined array.')
    shots('Q3');sources('Q3')
    chapter('Q4 District Rainfall Records in Two Dimensional Arrays')
    h('Shared Group Work')
    p('rain[38][12] stores nonnegative monthly rainfall in millimetres. Separate functions compute annual totals, state monthly averages, the wettest district-month and deficient districts. “Below 60% of the state average” is interpreted as each district’s annual total below 60% of the mean district annual total. Indices printed by the program are zero based.')
    h('Student A')
    p('A contiguous C array is row major: months of one district are adjacent. Address(rain[i][j])=base+((i*12)+j)*sizeof(double). For 3D rain[years][districts][months], the offset is ((year*districts+district)*months+month)*sizeof(element). A year-major, district-major, month-inner loop follows consecutive memory. Row traversal reuses fetched cache lines, while a column traversal over a large matrix takes a full-row stride between loads. Actual hardware, cache size and compiler transformations determine the measured difference.')
    h('Student B')
    table(['District','Hand annual total','Expected deficient'],[[0,100,'No'],[1,0,'Yes'],[2,140,'No']])
    p('The hand 3x4 input is (10,20,30,40), (0,0,0,0), (20,30,40,50). Monthly averages are 10,16.666667,23.333333,30; the maximum is 50 at district 2, month 3. Mean annual rainfall is 80 and the deficiency threshold is 48, so only district 1 qualifies. Independent Python arithmetic checks all full-dataset totals and averages.')
    annual=re.findall(r'^ANNUAL (\d+) ([0-9.]+)$',raw('Q4','rainfall_lab').split('DATASET full')[1],re.M)
    table(['District','Annual mm','District','Annual mm'],[[*annual[i],*annual[i+19]] for i in range(19)])
    monthly=re.findall(r'^MONTHLY (\d+) ([0-9.]+)$',raw('Q4','rainfall_lab').split('DATASET full')[1],re.M)
    table(['Month','State average mm','Month','State average mm'],[[*monthly[i],*monthly[i+6]] for i in range(6)])
    p('The full data are deterministic: value(i,j)=5(i+1)+3(j+1), retained in input.txt. The wettest entry is district 37, month 11, 226 mm. Mean annual total is 1404 mm, threshold 842.4 mm, and districts 0..9 are deficient. Annual totals, monthly averages and maximum scans each visit 456 cells. The deficiency function reads the already computed 38 totals instead of rescanning the matrix.')
    measured('Q4',['order','dimension','reps','cells','bytes','seconds','checksum'],['Order','Dimension','Reps','Cell loads','Data bytes','CPU s','Checksum'])
    layouts=[line.split() for line in raw('Q4','rainfall_lab').splitlines() if re.match(r'^(2D|flat|row_pointers) ',line)]
    table(['Layout','Reps','Visits','Pointer bytes','CPU s','Checksum'],layouts)
    chart('Q4')
    p('The large traversal uses five passes over 2000x2000 doubles, with volatile loads in both orders to ensure the data reads execute. Allocation and initialization are outside the timer. Both orders make 20000000 cell loads from 32000000 data bytes. The row order is faster in this captured run, consistent with spatial locality, but this single run does not establish a portable timing ratio. The small-layout comparison may show equal ticks because it fits in cache; the 1D form and true 2D form use the same consecutive layout. Floating-point summation order can change low bits without changing the underlying data.')
    h('Joint Conclusion and Decision')
    p('A 2D array expresses a regular district-month grid in one declaration and supports simple nested loops. Thirty-eight independently named 1D arrays make iteration and passing data harder; an array of row pointers supports uneven row lengths but adds allocation handling and indirection. For a fixed rectangular rainfall grid, contiguous storage is the simpler choice.')
    h('Alternative Concept and Complexity Analysis')
    p('The flat form accesses data[i*12+j]; the pointer form accesses rows[i][j] after allocating each row separately. All three give O(1) element access and O(D*M) work for a full grid scan. Contiguous storage needs D*M*sizeof(double) bytes; the row-pointer form adds D*sizeof(double*) bytes, measured as 304 bytes for 38 pointers here, excluding allocator metadata. The benchmark keeps all representations simultaneously only for comparison. Annual output is O(D), monthly output O(M); deficiency detection is O(D) given totals. Separate rows can be fragmented in memory and require D allocations/frees; they can be useful if districts have unequal month histories.')
    shots('Q4');sources('Q4')
    chapter('Q5 Processing Text Without string h')
    h('Shared Group Work')
    p('Manual and library-assisted functions count whitespace-separated words, uppercase ASCII test messages, reverse all characters and test palindromes while ignoring case and nonletters. The inputs include multiple spaces, punctuation, tabs, an empty string and punctuation only. Both implementations agree on every test. Library-assisted reversal still needs a loop: standard C string.h has no strrev function, and toupper is declared in ctype.h.')
    h('Student A')
    p('A character string ends at the first NUL byte, \\0; it is distinct from the printable digit 0. Every scan needs a terminator within the allocated object. char s[]="OK" creates a writable three-byte array, while char *s="OK" points at a string literal whose modification is undefined; const char * is appropriate for read-only literals.')
    code('count=0; inside=false\nfor each character until NUL:\n  if whitespace(character): inside=false\n  else if not inside: count++; inside=true\nreturn count',8)
    p('Scan length once before indexing a whole string. Recomputing strlen at every loop test can rescan the complete string n+1 times, giving O(n²) character work in the source model. An optimizing compiler may hoist ordinary strlen, so the benchmark calls the real strlen through a volatile function pointer to force the requested repeated calls. That control intentionally changes optimization opportunities and is documented rather than treating the source expression as a guaranteed machine-level cost.')
    h('Student B')
    code(raw('Q5','sms_analyser_lab').split('STRLEN n')[0],8)
    p('The runtime safety input requires 37 bytes including NUL; an 8-byte destination cannot hold it. Executing that strcpy would overflow and have undefined behaviour, so it is not executed. strncpy with count capacity-1 is followed by an explicit NUL; snprintf returns 36, the required length excluding NUL, exposing truncation of the seven stored characters. fgets reads at most capacity-1 characters and appends NUL; the remaining 29 characters are drained so they do not become the next message. gets cannot know the destination capacity and was removed in C11. Truncation is safe memory handling, but applications should signal it instead of silently accepting a changed message.')
    measured('Q5',['n','method','calls','reps','seconds','checksum'],['Length','Method','strlen calls','Reps','CPU s','Checksum'])
    p('At length 10000 and 100 repetitions, the repeated version makes 1000100 actual strlen calls; cached length makes 100. Both produce the same checksum. Zero cached CPU ticks prevent a defensible numerical speedup ratio. Recursive two-ended reversal reaches 501 active source calls for length 1000 and 5001 for length 10000; post-call work inhibits tail-call removal in this implementation. These are measured recursion depths, not measured stack-byte sizes.')
    h('Complete the Code')
    code(raw('Q5','complete_the_code')+raw('Q5','starter_extra_tests'),8)
    p('The exact starter output is Words: 7 and 1 0. The TODO uses isspace with unsigned-char conversion, so the added tab-separated four-word message returns 4. If only literal space were treated as a separator, that same tab-only message would be counted as one word. The starter’s broad “non-space” wording is implemented with all C whitespace characters, and the original main is unchanged. Empty and punctuation-only strings are palindromes under the rule that nonletters are ignored.')
    h('Joint Conclusion and Decision')
    p('Use custom loops when the definition is application specific, such as ignoring punctuation during a palindrome test or handling streaming tokens. Prefer standard library functions for conventional copying, length and comparison once capacities are established. Passing unsigned char values to ctype functions avoids undefined behaviour for negative plain-char values; locale and Unicode requirements must be addressed separately from these ASCII tests.')
    h('Alternative Concept and Complexity Analysis')
    p('The manual word scan, uppercase conversion, iterative reverse and two-pointer palindrome test take O(n) time. Repeated length scanning is O(n²) in the unhoisted model; cached length is O(n). An in-place iterative reversal uses O(1) auxiliary space, while this recursive reversal uses O(n) stack depth and O(n) time. The library palindrome version normalizes and reverses into two allocated buffers, adding O(n) space; the manual two-pointer version avoids them. strtok also needs a writable copy and modifies it, whereas the custom word counter can scan a read-only string.')
    shots('Q5');sources('Q5')
    chapter('Q6 Sorting and Searching a Hostel Name Directory')
    h('Shared Group Work')
    p('The directory stores up to 500 names in names[500][30], reads with fgets, strips newlines, sorts, searches and reports adjacent duplicates. It also sorts a case-insensitive pointer view. The focused eight-name input includes Apple/apple, duplicate Chris and lines of exactly 29 and 30 characters. Benchmarks generate 100,500,5000 fixed-length names in deterministic shuffled order, using heap storage for the larger case.')
    h('Student A')
    measured('Q6',['n','method','comparisons','copied_chars','index_writes','view_bytes','seconds'],['Names','Method','strcmp calls','Copied chars','Index writes','View bytes','CPU s'])
    searches=[re.findall(r'\d+',line) for line in raw('Q6','hostel_directory_lab').splitlines() if line.startswith('BENCH_SEARCH')]
    table(['Names','First present comparisons','Missing comparisons'],searches)
    p('The direct and index implementations use the same insertion-sort decisions, so their strcmp counts are equal. At 5000 names they make 5671880 comparisons, but the direct method copies 79476320 characters including terminators; the index method copies none of the name characters and writes 5671881 indices. The pointer-qsort callback makes 71150 strcmp calls in the captured run; both movement representation and sorting algorithm differ from insertion, so its timing cannot isolate pointer savings alone.')
    p('Length 29 fits as 29 characters plus NUL. Because fgets may leave the newline unread for an exactly full buffer, the code checks the next character: a newline is consumed without marking truncation. Length 30 stores only 29 characters, drains the rest and flags truncation. The two test names then become equal in storage, which creates a duplicate caused by truncation. Production software should reject or expand such names rather than merge identities. On the eight-name sorted directory, Chris is found in one strcmp call and ZZZ_missing takes three.')
    chart('Q6')
    h('Student B')
    p('strcmp compares byte values until a difference or NUL and returns a negative, zero or positive result, not necessarily -1 or 1. In the C locale on this ASCII-compatible target, uppercase A sorts before lowercase a, so Apple precedes apple. Case-insensitive comparison applies tolower to unsigned-char values and compares the folded bytes; sorting and searching must use the same rule. This program’s binary search is deliberately on the case-sensitive base directory, while the separate pointer view demonstrates case-insensitive order.')
    p('A swap implemented by three strcpy calls can copy about 3(L+1) characters for equal-length names. The direct insertion implementation instead copies a key twice plus each displaced name; its reported character count includes every terminator. After a correct sort, equal names are contiguous, so comparing each adjacent pair finds duplicates in O(n*L). Case-insensitive duplicates include Apple/apple. qsort is not stable, so equal folded names have no guaranteed relative order.')
    h('Joint Conclusion and Decision')
    p('An index view replaces whole-string movement by small integers and retains the original data. A pointer view makes comparisons convenient but must remain valid as long as the strings stay in place. Both add O(n) storage and indirection, and neither creates an independent string copy. The measured index size is 4 bytes and pointer size 8 bytes: 20000 versus 40000 view bytes for 5000 names, excluding the shared 150000-byte name storage. For a fixed 500-name directory, an index view gives compact ordering and stable source references.')
    h('Alternative Concept and Complexity Analysis')
    p('Direct and index insertion sorts have O(n²*L) worst-case comparison work, O(n*L) best case, and differ in move cost: O(L) per string move versus O(1) per index move. Pointer qsort uses a callback that dereferences two char pointers and calls strcmp. Under the usual O(n log n) comparison-sort model, its time is O(n log n*L), with O(n) pointer storage plus implementation-dependent sorting workspace; the C standard does not prescribe qsort’s algorithm. Binary search needs O(log n) strcmp calls, or O(L log n) character work. Fixed 30-byte names bound L here; truncation remains a correctness concern, not a sorting optimization.')
    shots('Q6');sources('Q6')
    chapter('Q7 Student Council Election from First Principles')
    h('Shared Group Work')
    h('Stage 1 Interpret the Problem Joint')
    p('Inputs are candidate count c in 1..12, vote count v in 0..5000 and v integer candidate IDs. Valid IDs satisfy 1<=id<=c; all others are invalid. Outputs must account for every input vote, list every candidate in descending vote order, and identify all candidates sharing the highest positive total. With no valid votes, report no winner. A deterministic ID order resolves display order within a tie without breaking the tie. Arrays hold up to 5000 input IDs, 12 unsigned-long-long counts and 12 candidate/count result records; a streamed deployment could discard input votes after counting.')
    p('Measurable requirements are valid+invalid=v, one visit per vote in the count-array method, sum(candidate counts)=valid, a nonincreasing result list, correct tie membership, and rejection of unsupported input dimensions. Benchmark mode intentionally extends the vote count to 500000 and candidate count to 500 to investigate scaling.')
    h('Stage 2 Design Student A')
    code('counts[0..c-1]=0; invalid=0\nfor each vote id:\n  if id<=0 or id>c: invalid++\n  else: counts[id-1]++\nresults = (candidate ID, count) for all candidates\nsort results by count descending then ID ascending\nif sum(counts)==0: report no winner\nelse: report every candidate with count == results[0].count\nassert sum(counts)+invalid == number of input votes',8)
    p('Counting does not sort raw votes or search names. Sorting only c result records is small for 12 candidates. Ranking uses descending count and ascending ID to make printed ties deterministic; the winner set still includes every tied candidate. Count types are wide enough for the 500000-vote experiment.')
    h('Stage 3 Implement Verify and Measure Student B')
    code(raw('Q7','election_lab').split('BENCH votes')[0],8)
    p('The hand set 1,2,2,3,1,0,-1,4 for c=3 gives counts 2,2,1, valid 5, invalid 3 and a tie between 1 and 2, exactly as predicted. The all-invalid test reports no winner. The generated 5000-vote run also reports a unique winner, Candidate 3 with 362 votes, among 4021 valid and 979 invalid votes. Independent Python generation checks all dataset invalid totals and the exact name-search comparison counts.')
    measured('Q7',['votes','candidates','method','visits','comparisons','invalid','seconds'],['Votes','Candidates','Method','Vote visits','Name or sort comparisons','Invalid','CPU s'])
    chart('Q7')
    p('Each benchmark method must produce identical counts and invalid totals before its row is accepted. Count-array timing includes clearing c counters and one pass over votes; name-search timing also includes candidate-name construction and per-vote formatting; sort-and-count includes copying, allocation, qsort and run counting. The result-ranking sort and report printing are outside these timers. Thus these are end-to-end implementations of the three counting strategies, not isolated instruction timings. Zero count-array ticks in some rows remain zero in the tables and chart.')
    h('Stage 4 Defend the Design Joint Conclusion and Decision')
    p('A count array indexes a valid ID directly and makes exactly v vote visits. With 500000 votes, linear name lookup needs 3798549 strcmp calls at 12 candidates and 126225709 at 500, while direct indexing still needs one pass. For 500 candidates allocate counters and results dynamically, validate IDs against the configured count, and rank results with an O(c log c) comparison sort. Counter memory grows with c; the name-based interface can map names to IDs once with a hash table rather than rescan names for every vote. A remaining limitation is that ID validation does not authenticate voters or detect repeated voting; the program is a tallying component, not a complete election system.')
    h('Alternative Concept and Complexity Analysis')
    p('One-pass counting is O(v+c) including counter initialization and O(c) auxiliary count space; including result ranking adds the usual O(c log c) comparison-sort cost. Storing all input votes as in the experiment adds O(v), but streaming can remove it. Name search is O(v*c*L) character work, or O(v*c) treating bounded names as constant length, plus O(c*L) candidate-name storage. Sorting votes then counting equal runs costs the usual O(v log v) comparisons and O(v) copying storage plus O(c) counts and implementation-dependent qsort workspace. Run counting is O(v). The prototype’s qsort callback count is empirical, and standard C does not guarantee a particular sorting implementation.')
    shots('Q7');sources('Q7')
    chapter('Reproduction and verification')
    p('Run python run_all.py from Assignment3-CO3 to compile every C file with the required flags and execute it using its input.txt. Run python verify.py to check exact starter output, source preservation, manifest hashes and independent numerical/count checks. Run build_report.py with python-docx, Pillow and matplotlib to regenerate charts, transcript images and this report from the saved evidence. Re-running experiments may produce different CPU ticks; never replace measured timings with previous values.')
    code((R/'qa/verification.txt').read_text(),8)
    h('Common C support header')
    code((R/'lab.h').read_text(),8)
    h('Submission reference')
    p('CO3_Assignment_3.docx.pdf, supplied assignment: questions Q1–Q7, role allocation, contribution record and 50-mark distribution. The source PDF and extracted text are retained under reference. The repository also includes Assignment2-CO2 with its earlier task history and the updated report cover URL.')
    for root in [d.styles.element,d.element]:
        for border in list(root.iter(qn('w:pBdr'))):border.getparent().remove(border)
    footer=sec.footer.paragraphs[0];footer.alignment=2;r=footer.add_run('Page ');r.font.size=Pt(8)
    f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');footer._p.append(f)
    d.core_properties.author='Chris Abraham George';d.core_properties.title='CSA02 Assignment 3 CO3 C Programming'
    d.save(R/FILE)

def readmes():
    commands=[]
    for manifest in sorted(R.glob('Q*/outputs/manifest.json')):
        for row in json.loads(manifest.read_text()):
            commands.append(' '.join(row['compile']));commands.append(f"build/{manifest.parent.parent.name}_{Path(row['source']).stem}.exe < "+row['input'].replace('\\','/'))
    gcc=(R/'environment/gcc.txt').read_text().strip()
    (R/'README.md').write_text(f'''# CSA02 Assignment 3 CO3

Student A: Chris Abraham George | Register No: 1911260256  
SIMATS Engineering | B.E / B.Tech CSE | Pair Work | 50 marks  
Repository: {URL}

Student B name/register/repository, Section and Submission Date are blank in the report.
The role-labelled sections and contribution table cover the prescribed Student A, Student B and joint responsibilities.

## Detected compiler

```text
{gcc}
```

## Compile, execute and verify

```powershell
python run_all.py
python verify.py
```

Every final C source compiles with `-std=c11 -O2 -Wall -Wextra`, with zero warnings.
The runner creates `build/`, preserves byte-exact stdout/stderr, records actual commands and SHA-256 hashes,
rejects failed runs/diagnostics, and compares starter outputs including trailing spaces and CRLF.
For manual `<` input redirection use cmd.exe or another supporting shell; the runner works directly in PowerShell.

### Exact commands recorded from execution

```text
{chr(10).join(commands)}
```

## Results and evidence

- Q1: exact binary-search starter PASS. 48 measured search rows cover 1000/10000/100000 entries, first/middle/last/missing keys, linear, binary, hash and interpolation. Binary worst observed 17; successful mean 15.689460 at 100000. Hash collisions are tested explicitly.
- Q2: 6-element traces plus 52 benchmark rows cover 4 sorts, 4 orders, 3 sizes and 20 late entries. Late-entry insertion takes 11499 comparisons vs bubble 519500 and selection 519690. Counting sort uses the known small integer range.
- Q3: exact starter and separate empty-list driver PASS. Campus A wins equal-score ties. At 10000 per campus, merge uses 19999 comparisons/20000 writes; simple in-place merge makes 50004999 record writes. qsort internal moves are NA, not invented.
- Q4: hand 3x4 and full 38x12 data verified. Separate functions implement all 4 computations. Actual CPU timings compare 2000x2000 traversal and 2D/flat/separate-row storage; pointer overhead is 304 bytes on this target.
- Q5: exact starter PASS, tab-separated extra test PASS; manual/library outputs agree. Safe truncation is executed; overflowing strcpy is explained but never executed. Real strlen calls through a volatile function pointer demonstrate repeated vs cached length. Recursive depths are recorded.
- Q6: direct/index insertion use equal comparison counts; index and pointer views copy no name characters. At 5000 names direct sorting copies 79476320 characters including NUL. Length29 fits, length30 is flagged and drained. Present/missing search counts and case-insensitive duplicates are recorded.
- Q7: the hand tally gives 2,2,1; valid5/invalid3; tie1/2. All three methods agree for 5000/500000 votes and 12/500 candidates. Count-array visits are exactly v; generated dataset totals and linear-name comparison counts are independently checked.

All raw outputs are in Q*/outputs. All source files, including the exact starter completions, are listed in the Word report.
Each task has input.txt and paginated 300-DPI dark-terminal transcript renderings, derived directly from captured commands and output.
Tabs use eight-column terminal stops; raw bytes remain authoritative. Screenshots are renderings of execution records, not OS-window photographs.
The six charts in charts/ read qa/data.json parsed from real output; CSV tables accompany them.

## Timing and count definitions

clock() measures process CPU seconds with CLOCKS_PER_SEC=1000 here. Values of 0.000000000 are real zero-tick observations,
not proof of zero work or a portable speedup. Q1 rows report batch CPU time and their own repetition count; other timings are single captured algorithm runs or explicitly labelled traversals.
Counts measure instrumented source-level operations. qsort comparator counts are observable; internal swaps and storage are not.
Binary-search steps count midpoint visits, as required by the supplied expected output, rather than every primitive == and <.
The standard C library does not prescribe qsort's algorithm; its O(n log n) discussion is the intended comparison-sort model.

## Files

- `{FILE}`: final role-labelled report with complete code, tables, charts and execution images.
- `PREDICTIONS.md`: committed before experiments.
- `qa/verification.txt`, `qa/data.json`: independent checks and parsed raw measurements.
- `qa/screenshots.json`: dimensions, DPI and exact transcript-line coverage.
- `complete_starters.py`: optional helper rebuilding TODO completions from the retained PDF text.
- `build_report.py`: artifact builder requiring python-docx, Pillow and matplotlib.
- `reference/`: supplied PDF and extracted text.

To regenerate artifacts after execution: `python verify.py`, then `python build_report.py` with those packages installed.
The workspace's bundled Python includes these dependencies. Rendering for visual QA used Microsoft Word read-only PDF export because bundled LibreOffice is unavailable on this Windows runtime.

The Student B sections describe the prescribed role's design and evidence; no unnamed partner's identity or independent execution is attested.
''',encoding='utf-8')
    (R.parent/'README.md').write_text(f'''# C Programming assignments

Chris Abraham George | Register Number 1911260256  
Saveetha Institute of Medical and Technical Sciences (SIMATS Engineering)  
B.E / B.Tech CSE | CSA02 C Programming

Repository: {URL}

| Assignment | Folder and reproduction guide | Word report |
| --- | --- | --- |
| Assignment 2 CO2 | [Assignment2-CO2](Assignment2-CO2/README.md) | [Report](Assignment2-CO2/CSA02_1911260256_Assignment2_Report.docx) |
| Assignment 3 CO3 | [Assignment3-CO3](Assignment3-CO3/README.md) | [Report](Assignment3-CO3/{FILE}) |

## Exact detected gcc version

```text
{gcc}
```

Assignment 2 retains its original executed evidence and progressive Git history. Its report cover now links to this repository.
Assignment 3 has separate progressive task commits and compiles all its C programs with `-std=c11 -O2 -Wall -Wextra`.
See each assignment README for exact compile commands, inputs, output definitions and reproduction steps.
The existing DBMS work and original Assignment 2 folder in the parent workspace are preserved.

```powershell
cd Assignment3-CO3
python run_all.py
python verify.py
```

The Assignment 3 cover leaves Student B details, Section and Submission Date blank.
''',encoding='utf-8')

if __name__=='__main__':images();charts();report();readmes();print('Generated report, six 300-DPI charts, transcript images and both README files.')
