"""Build charts and a Word report entirely from captured experiment evidence."""
from pathlib import Path
import json, math, re, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageChops
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parent
NAME='CSA02_1911260256_Assignment2_Report.docx'
LINK='https://github.com/<your-username>/CSA02-1911260256-Assignment2'
origin=subprocess.run(['git','remote','get-url','origin'],cwd=R,capture_output=True,text=True)
if origin.returncode==0: LINK=origin.stdout.strip().removesuffix('.git')
def raw(q,name): return (R/q/'outputs'/f'{name}.stdout.txt').read_text()

def visuals():
    evidence=[]
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',27)
    label=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',23)
    for transcript in sorted(R.glob('Q*/outputs/*.transcript.txt')):
        # Split only at actual line boundaries. No replacement or fabricated output.
        lines=transcript.read_text(encoding='utf-8').splitlines()
        folder=transcript.parent.parent/'screenshots'; folder.mkdir(exist_ok=True)
        for old in folder.glob(transcript.name.split('.')[0]+'_*.png'): old.unlink()
        for start in range(0,len(lines),36):
            chunk=lines[start:start+36]
            width=max(1800,int(max(font.getlength(line) for line in chunk))+100)
            height=110+len(chunk)*38
            im=Image.new('RGB',(width,height),'#101720'); draw=ImageDraw.Draw(im)
            draw.text((40,22),f'{transcript.parent.parent.name} | {transcript.stem} | lines {start+1}-{start+len(chunk)}',font=label,fill='#91a4b5')
            for j,line in enumerate(chunk):
                color='#6fe3b3' if line.startswith('$ ') else '#edf3f8'
                draw.text((40,75+j*38),line,font=font,fill=color)
                assert font.getbbox(line)[2]+40<width-30
            path=folder/f'{transcript.name.split(".")[0]}_{start//36+1:02}.png'
            im.save(path,dpi=(300,300))
            reopened=Image.open(path)
            diff=ImageChops.difference(reopened,Image.new('RGB',reopened.size,'#101720'))
            assert reopened.width>=1800 and diff.getbbox()
            evidence.append(dict(file=str(path.relative_to(R)),width=width,height=height,nonblank=True,source=str(transcript.relative_to(R)),line_start=start+1,line_end=start+len(chunk)))
    (R/'qa/screenshots.json').write_text(json.dumps(evidence,indent=2))
    figdir=R/'charts'; figdir.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    rows=[line.split() for line in raw('Q2','concession').splitlines()[1:6]]
    fig,ax=plt.subplots(figsize=(7,3)); ax.bar(['Cheap first','Server first','Eager','Nested if','Audit all'],[int(r[3]) for r in rows],color='#275d86'); ax.set_ylabel('Verifier calls / 1000 passengers'); fig.tight_layout(); fig.savefig(figdir/'Q2_calls.png',dpi=300); plt.close(fig)
    lines=raw('Q7','redesign').splitlines()[1:-1]; rows=[r.split() for r in lines if r.split()[0] in ('97','7919','1000003')]
    fig,ax=plt.subplots(figsize=(7,3.2)); x=list(range(len(rows))); ax.bar([v-.18 for v in x],[int(r[6]) for r in rows],.36,label='Original'); ax.bar([v+.18 for v in x],[int(r[7]) for r in rows],.36,label='6k +/- 1'); ax.set_xticks(x,[r[0] for r in rows]); ax.set_xlabel('Ticket number'); ax.set_ylabel('All counted divisions'); ax.legend(); fig.tight_layout(); fig.savefig(figdir/'Q7_divisions.png',dpi=300); plt.close(fig)
    pairs=[]; payment=None; rate=None; principal=None
    for line in raw('Q6','loan').splitlines():
        if line.startswith('loan '):
            payment=float(re.search(r'E=([0-9.]+)',line)[1])
            rate=float(re.search(r'r=([0-9.]+)',line)[1])
            principal=float(re.search(r'P=(-?[0-9.]+)',line)[1])
        if line.startswith('RESULT ') and principal==10000 and rate==.02 and 200<payment<=2000:
            pairs.append((payment,int(re.search(r'months=(\d+)',line)[1])))
    pairs.sort(); assert len(pairs)==7
    (figdir/'loan_chart_data.json').write_text(json.dumps(pairs,indent=2)+'\n')
    fig,ax=plt.subplots(figsize=(7,3)); ax.plot([p[0] for p in pairs],[p[1] for p in pairs],'o-',color='#275d86'); ax.set_xlabel('Monthly repayment Rs'); ax.set_ylabel('Executed loop iterations'); ax.annotate('360 month safety cap',(200.01,360),xytext=(650,300),arrowprops={'arrowstyle':'->'}); fig.tight_layout(); fig.savefig(figdir/'Q6_growth.png',dpi=300); plt.close(fig)

d=Document(); sec=d.sections[0]; sec.page_width=Inches(8.27); sec.page_height=Inches(11.69)
sec.top_margin=sec.bottom_margin=Inches(.7); sec.left_margin=sec.right_margin=Inches(.75)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
    s=d.styles[name]; s.font.name='Calibri'; s.font.color.rgb=RGBColor(0,0,0)
d.styles['Normal'].font.size=Pt(10.5); d.styles['Normal'].paragraph_format.space_after=Pt(6)
d.styles['Normal'].paragraph_format.line_spacing=1.08
d.styles['Title'].font.size=Pt(26)
for name,size in [('Heading 1',18),('Heading 2',13),('Heading 3',11)]: d.styles[name].font.size=Pt(size)
def p(s,style=None): return d.add_paragraph(s,style)
def h(s): d.add_heading(s,2)
def page(title):
    heading=d.add_heading(title,1)
    heading.paragraph_format.page_break_before=not (re.match(r'Q[2-7] ',title) or title=='Source code listings')
    heading.paragraph_format.space_before=Pt(14)
def table(headers,rows):
    t=d.add_table(rows=1,cols=len(headers)); t.autofit=True
    for c,v in zip(t.rows[0].cells,headers): c.text=str(v)
    for row in rows:
        for c,v in zip(t.add_row().cells,row): c.text=str(v)
    for i,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr()
        no=OxmlElement('w:cantSplit'); trpr.append(no)
        if i==0:
            repeat=OxmlElement('w:tblHeader'); trpr.append(repeat)
        for c in row.cells:
            pr=c._tc.get_or_add_tcPr(); shade=OxmlElement('w:shd'); shade.set(qn('w:fill'),'DCE8F0' if i==0 else ('F5F7F9' if i%2 else 'FFFFFF')); pr.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:color'),'D9D9D9'); borders.append(e)
            pr.append(borders)
            for para in c.paragraphs:
                para.paragraph_format.space_after=Pt(4); para.paragraph_format.space_before=Pt(4)
                for run in para.runs: run.font.size=Pt(9); run.bold=(i==0)
    p('')
def code(s,size=8):
    para=p(''); para.paragraph_format.space_after=Pt(5); para.paragraph_format.line_spacing=1
    para.paragraph_format.keep_together=len(s.splitlines())<=12
    run=para.add_run(s.rstrip()); run.font.name='Consolas'; run.font.size=Pt(size)
def image(path,caption,width=6.65):
    para=p(''); para.paragraph_format.keep_with_next=True
    para.add_run().add_picture(str(R/path),width=Inches(width))
    cap=p(caption); cap.paragraph_format.space_after=Pt(8)
    for r in cap.runs: r.italic=True; r.font.size=Pt(9)
def shot(q,name):
    path=f'{q}/screenshots/{name}_01.png'
    image(path,f'{q} actual command and captured output. Complete transcript and subsequent image pages are in {q}/outputs and {q}/screenshots.')

def report():
    p('ASSIGNMENT 2 - CO2','Title'); p('CSA02 C Programming','Subtitle')
    p('Operators decision making and looping constructs','Subtitle')
    p('Max Marks: 50')
    p('Chris Abraham George'); p('Register Number: 1911260256')
    p('Saveetha Institute of Medical and Technical Sciences\nSIMATS Engineering')
    p('Programme: B.E / B.Tech\nComputer Science and Engineering (CSE)')
    p('Section: ____________________'); p('Submission Date: ____________________')
    p('GitHub Repository Link'); p(LINK)
    p('Repository: CSA02-1911260256-Assignment2')
    page('Execution environment and evidence map')
    p('This report analyses C operator behaviour, decisions and loops through seven executed experiments. The final redesign reduces counted integer divisions on a large prime by 74.937%. All final programs compile without warnings; the isolated undefined-behaviour demonstration intentionally records GCC diagnostics.')
    h('Detected environment')
    code((R/'environment/gcc.txt').read_text().strip(),9)
    p((R/'environment/git.txt').read_text().strip()+'; '+(R/'environment/python.txt').read_text().strip()+'. Platform: Windows. C compilation uses -std=c11 -Wall -Wextra; the UB demonstration uses -std=c11 -Wall. The loan program links -lm.')
    p('PREDICTIONS.md was committed before task execution. Each task stores sources, reproducible inputs, byte-exact stdout/stderr, compiler diagnostics, command transcripts and execution manifests. Transcript images are 300 DPI renderings of the actual commands and captured output, with line coverage checked by Pillow. Counts describe source-level work; no wall-clock timings or machine-instruction counts are claimed.')
    table(['Task','Marks','Evidence'],[
        ['Q1',6,'Predictions, integer bills, UB warning, readable correction'],['Q2',4,'1000 passengers, 5 orders, call counts, audit log'],['Q3',6,'Unmodified starter, register predictions, array comparison'],['Q4',6,'Starter, 22 boundaries, 301-case agreement, fall-through'],['Q5',7,'Starter, 4 loop variants, counts, sieve, overflow'],['Q6',8,'6 hand-verified rows, growth, safety cap, formula'],['Q7',13,'Diagnosis, objective, design, prediction, validation, defence']])
    p('Rubric coverage totals 50 marks; this maps supplied requirements to evidence and does not assign a faculty score. Source listings follow the analysis. Full raw files remain the authoritative output, including the long Q2 audit log.')
    page('Q1 Pharmacy billing precedence and correction')
    h('Prediction and operator analysis')
    p('For integer price, quantity and senior, * and / share precedence and associate left to right. Each multiplication/division chain is grouped before the left-associative subtraction and addition. Relational > binds before ?:, so the coupon is subtracted only when total exceeds 1000. Associativity determines grouping, not a general operand evaluation order.')
    code('total = (((price * qty) - ((((price * qty) * 15) / 100) * senior))\n         + (((price * qty) * 5) / 100));\nnet = (total > 1000) ? (total - 50) : total;',9)
    table(['Bill price qty senior','Predicted total / net','Observed total / net','Corrected net Rs'],[['99 3 1','267 / 267','267 / 267','265.072500'],['500 2 0','1050 / 1000','1050 / 1000','1000.000000'],['1200 1 1','1080 / 1030','1080 / 1030','1021.000000']])
    p('For the first bill, gross is 297. Integer discount is 4455/100 = 44 and original GST is 1485/100 = 14, giving 267. The intended senior discount is 44.55; tax on 252.45 is 12.6225, giving 265.0725. For the third bill, tax on the gross overcharges Rs 9 relative to tax after discount. The non-senior second bill agrees because its percentages are integral and no discount changes the tax base. The coupon test itself implements the stated strict > threshold correctly.')
    h('Corrected design and cost')
    p('Use gross, discount, taxable, tax and corrected as double intermediates. Apply the discount first, compute GST on the discounted value, then test the coupon threshold. This explicitly states the chosen interpretation of “less discount, plus GST”. These experiments retain fractional rupees; a production billing policy must specify rounding to paise. The corrected source separates sequencing from arithmetic grouping.')
    p('When senior discount and coupon both apply, the written original performs 11 arithmetic operations including the final coupon subtraction; the corrected sequence performs 6. This is a static source count, not runtime instrumentation or a prediction of optimized machine code. Both take O(1) time and O(1) space; intermediates add a fixed number of scalar objects while avoiding repeated price*qty and making the tax base visible.')
    h('Undefined behaviour inquiry')
    p('count = count++ + 1 modifies count twice without the required sequencing between those side effects. Its result is undefined under C11; a particular observed number cannot validate it. The dedicated run below records the compiler warning. count += 1 is a defined replacement when incrementing once is intended.')
    shot('Q1','ub_demo'); shot('Q1','billing')
    page('Q2 Railway concession and short circuit evaluation')
    p('The deterministic sample has 1000 passengers indexed 0..999: senior if i%3==0, eligible class if i%4!=0, and disability card if i%10==0. The verifier includes a volatile local workload so calls do real repeatable work; it models an expensive check without claiming a network benchmark. All orders grant 333 concessions.')
    table(['Order','Verifier calls','Concessions'],[['(senior && eligible) || verify',750,333],['verify || (senior && eligible)',1000,333],['(senior & eligible) | verify',1000,333],['Nested if then verify',750,333],['Verify first for audit completeness',1000,333]])
    p('The 250 senior passengers with eligible classes make the first OR operand true, so cheap-first avoids 250 calls. For 0 && verify, no call occurs; for 1 || verify, no call occurs. Replacing && with & executes the second operand, giving one call even for 0 & verify. Logical operators return 0 or 1 and sequence the left operand before the right; bitwise operators work on all value bits and do not guarantee an operand evaluation order. Their truth results agree here because operands are normalized to 0 and 1.')
    h('Ordering and the audit requirement')
    p('For &&, place a cheap or likely-false pure check first to reject early. For ||, place a cheap or likely-true pure check first to accept early. The relevant trade-off combines cost with probability, so cheapest alone is not a universal rule. Order has no call-count effect when the first operand never short-circuits, both checks are trivial, or every check must execute for a required side effect. Reordering impure predicates may change program behaviour.')
    p('When every passenger must be checked and logged, call verify once in a separate statement before deciding eligibility. The source emits passenger IDs 0..999 and results in a separate complete audit run; verify.py checks uniqueness and truth. If the contract only requires logging the passengers actually verified, the original 750-call order remains valid. Audit scope determines which interpretation is appropriate.')
    h('Alternatives and complexity')
    code('if (senior && eligible) granted = 1;\nelse granted = verify(i);\n/* Full-audit requirement */\nint verified = verify(i);\ngranted = (senior && eligible) || verified;',9)
    p('For n passengers and s early accepts, cheap-first and nested if make n-s calls; server-first and eager &/| make n. If verifier cost is V, time is O(n + (n-s)V) versus O(n+nV); all are O(n) for fixed V. Counters and decisions use O(1) auxiliary space. Persisting every audit record requires O(n) output/storage, although streaming the records uses constant working memory.')
    image('charts/Q2_calls.png','Measured verifier calls for the same 1000-passenger sample.')
    shot('Q2','concession')
    page('Q3 Smart home bit register')
    p('The four TODO bodies use reg | (1u<<dev), reg & ~(1u<<dev), reg ^ (1u<<dev), and (reg>>dev)&1u. Device indices are assumed valid in 0..7. Unsigned masks make the operation explicit; conversion back to unsigned char retains the byte.')
    table(['Statement in starter main','Predicted register','Observed evidence'],[['Initialization','0 / 00000000','Source initialization'],['LIGHT on','1 / 00000001','Intermediate calculation'],['AC on then show','5 / 00000101','00000101'],['FAN toggled','7 / 00000111','Intermediate calculation'],['LIGHT off then show','6 / 00000110','00000110'],['printf tests','6 unchanged','AC ON, PUMP OFF']])
    p('show and printf do not mutate the register. The additional experiment sets bit 7, sets bit 0, toggles bit 7 and clears bit 0, predicting 128,129,1,0. The real run records each register value and confirms identical array and bit counts.')
    h('Precedence and signedness')
    p('Shifts bind more tightly than bitwise &: reg & 1 << dev means reg & (1<<dev). It tests the chosen bit. (reg & 1)<<dev tests bit zero and then moves that result. With reg=2 and dev=1 these give 2 and 0 respectively. is_on normalizes the selected bit to 0 or 1 with a right shift and mask.')
    p('An unsigned char represents all eight bits without a negative sign on this CHAR_BIT=8 target. Converting 128 to signed char is implementation-defined when out of range in C11, and right-shifting a negative signed value is implementation-defined. The measured conversion/shift is target evidence only. Integer promotion can propagate the negative sign into later expressions, so use unsigned storage and masks. A signed left shift with an unrepresentable result would be undefined.')
    h('Array alternative and complexity')
    p('For char state[8], set with state[dev]=1, clear with =0, toggle with ^=1, and test the element. Each update or test is O(1) for either representation. Counting scans eight bits/elements, so O(8)=O(1) for this fixed problem; generalized to d devices it is O(d). The measured sizes are 1 and 8 bytes, so one million homes need 1,000,000 versus 8,000,000 bytes for states, excluding allocator or container overhead. The bit register saves 7 MB and may need extra masking; the array is easier to inspect and extend.')
    p('The completed starter stdout matches its expected byte sequence exactly, including the final newline. The retained starter and unchanged main are checked independently.')
    shot('Q3','complete'); shot('Q3','register_compare')
    page('Q4 Grades scholarship and boundary tests')
    p('Both the ladder and switch validate 0..100 before classification. The switch groups case 10 and case 9 as S; default handles decades below 5 as F. Validation is essential: in C, -1/10 truncates toward zero, and 101/10 is 10, so an unchecked switch could misclassify -1 and 101.')
    table(['Input','Ladder','Switch','Lookup'],[[m,*([g]*3)] for m,g in [(100,'S'),(90,'S'),(89,'A'),(0,'F'),(-1,'?'),(101,'?')]])
    p('The boundary set includes -1,0,1; 48,49,50,51; 59,60,61; 69,70,71; 79,80,81; 89,90,91; 99,100,101. This tests both sides of each valid grade transition, plus domain endpoints. All three implementations also agree across every integer from -100 to 200 (301 cases).')
    h('Observed fall through')
    p('The dedicated variant removes the S return from the grouped cases 10 and 9. Execution continues into case 8, returning A: the starter output changes from 100:S 95:S to 100:A 95:A. Remaining outputs are unchanged. A return terminates the function and therefore replaces a break; leaving out that exit causes fall-through. The variant still compiles without warnings with the required flags.')
    code(raw('Q4','fallthrough'),9)
    p('A C switch selects integer constant cases, so case 75..84 is not standard C11. marks/10 only groups decades and cannot describe an arbitrary shifted boundary. The ladder is easier to edit for boundaries such as 75 or 85; a switch would need another mapping or many explicit cases.')
    h('Scholarship design decision')
    p('No numerical income policy is specified in the question. The experiment explicitly defines S/A with income <=200000 as full scholarship, S/A with income <=500000 as partial, and other valid cases as none; negative income or invalid grade is rejected. Nested if is chosen for this small range-based rule because it keeps the policy readable. A switch within if is useful for many discrete grade categories; a lookup table is preferable when a larger approved grade-by-income matrix must be updated as data. The run tests -1,0,200000,200001,500000,500001 for S,A,B and invalid grade.')
    h('Lookup alternative and cost')
    code("static const char grades[11] =\n    {'F','F','F','F','F','D','C','B','A','S','S'};\nreturn marks < 0 || marks > 100 ? '?' : grades[marks / 10];",9)
    p('The lookup uses 11 char elements and one index operation after validation, O(1) time and O(k) table storage for k buckets. A ladder can perform up to k grade comparisons, O(k) time and O(1) auxiliary space; with these fixed six grades it is also O(1). The switch is constant-sized here, but C does not require a particular jump-table implementation. No speedup is claimed without timing or assembly evidence.')
    shot('Q4','complete'); shot('Q4','classifiers')
    page('Q5 Prime loops operation counts and sieve')
    h('Deriving the bound')
    p('If n=a*b and both factors exceeded sqrt(n), their product would exceed n. Therefore a composite has a factor at most sqrt(n). Test i starting at 2, continue while i<=n/i, and return immediately when n%i==0. For positive i, i<=n/i is equivalent to i*i<=n without multiplication overflow. n<2 is rejected before the loop.')
    table(['Ticket','Naive for modulo','Bounded for','Bounded while','Bounded do while'],[[97,95,8,8,8],[100,1,1,1,1],[7919,7917,87,87,87],[1000003,1000001,999,999,999]])
    p('The primary assignment counter counts remainder attempts n%i. Changing the starter bound to i<n produces the recorded naive counts above. The separate loop experiment additionally counts quotient evaluations n/i in the safe condition: for the large prime, 999 remainder attempts plus 1000 condition quotients gives 1999 integer divisions. These extra condition divisions must be included when comparing all source-level division operations.')
    h('Boundary behaviour and overflow')
    p('For 2 and 3, no trial divisor satisfies the bound. A do-while executes at least once, so the implementation first tests the bound outside the loop; otherwise testing 2%2 would incorrectly reject 2 and perform unnecessary work for 3. Tests include 0,1,2,3,4,25 and perfect-square composites. Each bounded form stops on the first divisor.')
    p('The defined uint32_t demonstration computes 65536*65536 as 0 by modular arithmetic. This shows how a squared loop bound can wrap for large unsigned inputs. Signed overflow would be undefined and is not executed. The division bound is safe for unsigned long as long as the divisor is nonzero.')
    h('Starter output comparison')
    p('The exact given main is preserved. Its %8lu field prints six leading spaces for 97, five for 100, four for 7919 and one for 1000003. The PDF expected block displays five, five, four and zero respectively in its extracted text. Thus a literal comparison against the printed block fails on whitespace for 97 and 1000003; the numbers, labels and counts match. The executable passes a byte-for-byte fixture derived from the unchanged printf contract, with Windows CRLF line endings. No main change was made to hide this source inconsistency.')
    code('\n'.join(repr(line) for line in (R/'Q5/outputs/complete.stdout.txt').read_bytes().splitlines(keepends=True)),8)
    h('Sieve alternative and complexity')
    p('Allocate N+1 zeroed flags for indices 0..N, mark multiples from p*p for each unmarked p<=N/p, then answer n>=2 && !flags[n]. The actual run for N=1000003 allocates 1,000,004 bytes, performs 2,122,051 marking visits and finds 78,499 primes. Marking visits count repeated attempts to set a flag; they are not division counts. All four loop variants agree with the sieve on every n=0..10000.')
    p('Naive trial division is O(n) worst-case time per ticket. The bounded forms are O(sqrt(n)) time and O(1) working space. A sieve costs O(N log log N) preprocessing, O(N) storage and O(1) query time, making it suitable for many queries over a known maximum. Trial division avoids the allocation for isolated or very large tickets.')
    shot('Q5','complete'); shot('Q5','naive_complete'); shot('Q5','loops_sieve')
    page('Q6 Loan repayment termination and growth')
    h('Loop design and hand calculation')
    p('A while loop matches an unknown number of payments and skips an already repaid loan. While balance>0, calculate interest, add it to balance, and pay min(fixed repayment, amount due). Assigning closing=due-paid gives exactly zero in the final branch. Comparing balance!=0 while repeatedly subtracting a fixed payment can leave a residual or overpay; this design chooses the final payment deliberately.')
    table(['Month','Opening Rs','Interest Rs','Payment Rs','Closing Rs'],[[1,'10000','200','2000','8200'],[2,'8200','164','2000','6364'],[3,'6364','127.28','2000','4491.28'],[4,'4491.28','89.8256','2000','2581.1056'],[5,'2581.1056','51.622112','2000','632.727712'],[6,'632.727712','12.65455424','645.38226624','0']])
    p('The recurrence Bnext=1.02B-payment predicts six months, total interest Rs 645.38226624 and total paid Rs 10645.38226624. Independent Decimal arithmetic verifies every eight-decimal output row. Values are intentionally unrounded internally; rounding monthly interest to paise defines a different model and may change totals or boundary behaviour.')
    h('Measured approach to non repayment')
    table(['Repayment Rs','Executed months','Formula ceiling','Status'],[['2000',6,6,'Repaid'],['1000',12,12,'Repaid'],['500',26,26,'Repaid'],['250',82,82,'Repaid'],['210',154,154,'Repaid'],['201',268,268,'Repaid'],['200.01',360,501,'Stopped at safety cap'],['200 or 199',0,'Undefined real formula','Rejected as non amortizing']])
    p('When E<=rP, the first payment cannot reduce principal: equality holds the balance constant and a smaller repayment grows it. Reject such terms before entering the loop. As E approaches rP from above, the required months grow sharply, confirming the prediction. The 360-month break gives a bounded execution guarantee and reports an unpaid balance of Rs 9376.71943611 for E=200.01; it never calls the capped loan repaid. The message asks for review of repayment terms, which is more actionable than silently truncating the schedule.')
    image('charts/Q6_growth.png','Observed iteration growth. The Rs 200.01 point is capped at 360, not its theoretical payoff month.')
    h('Closed form and deployment decision')
    p('For r>0 and E>rP, n=-log(1-rP/E)/log(1+r). Use ceil(n) for a whole number of months, log1p for numerical stability, and n=P/E when r=0. This model produces 5.32053217 months and a ceiling of 6 for the hand example. Computing the count is O(1) under the usual scalar-operation model; producing a monthly schedule remains O(n). Both formula and streamed simulation use O(1) auxiliary space.')
    p('Near E=rP, cancellation, a logarithm near its domain boundary and rounding around an integer can change ceil(n). Simulation accumulates floating-point rounding over months. Use the formula for planning, the bounded simulation for the required schedule, and verify integer-month boundary cases under the chosen money-rounding policy. The program also handles zero principal, zero interest, negative principal, nonpositive repayment, invalid caps and nonfinite scalar values.')
    shot('Q6','loan')
    page('Q7 Day 4 design challenge')
    h('A Diagnose the bottleneck 2 marks')
    p('Q5 shows the original bounded loop tries every integer divisor up to sqrt(n). For prime 1000003 it performs 999 remainders and 1000 condition quotients. Most candidates are redundant: after ruling out divisibility by 2 and 3, multiples of either cannot be the first factor. The count grows with sqrt(n); the loop does not reuse work across separate tickets.')
    h('B Define the objective 2 marks')
    p('Reduce all counted integer divisions by at least 50% for the same two primes 7919 and 1000003, preserve the prime/composite result and retain O(1) auxiliary space. Count both % tests and / loop-bound evaluations. This criterion was committed in PREDICTIONS.md before implementation.')
    h('C Design the revised solution 4 marks')
    p('Handle n<2, then 2 and 3. Reject other multiples of 2 or 3. Every remaining prime factor is congruent to 1 or 5 modulo 6, so test i=5,11,17,... and i+2. The property narrows possible factors; it does not claim that all 6k+/-1 candidates are prime. One n/i guard covers each pair, and a final i+2 test may lie just above sqrt(n), adding a harmless remainder attempt. For unsigned long these small trial indices leave i+2 and i+=6 far below the type limit.')
    code('if n < 2: return composite\nif n == 2 or n == 3: return prime\nif n % 2 == 0 or n % 3 == 0: return composite\ni = 5\nwhile i <= n / i:\n    if n % i == 0 or n % (i + 2) == 0: return composite\n    i += 6\nreturn prime',9)
    p('The revised function uses only a divisor and counters, O(1) space. The sieve used during validation is a separate test oracle and is not part of the deployed redesign. The asymptotic worst-case time stays O(sqrt(n)); the improvement is in the constant amount of repeated work.')
    h('D Prediction before implementation 1 mark')
    p('Remainder candidates should fall by roughly two thirds for large primes, with a further saving because one quotient guard serves two tests. Prediction: at least half the total divisions will be removed for both large primes. Small composites may show little benefit because the original already exits early.')
    h('E Implement and validate 2 marks')
    table(['Ticket','Old % / quotient','New % / quotient','Old total','New total','Reduction'],[['97','8 / 9','4 / 2',17,6,'64.706%'],['100','1 / 1','1 / 0',2,1,'50.000%'],['7919','87 / 88','30 / 15',175,45,'74.286%'],['1000003','999 / 1000','334 / 167',1999,501,'74.937%']])
    p('The same-input comparison includes 0,1,2,3,4,9,25,49 as boundary and square cases. The redesigned function agrees with an independently constructed sieve for every input 0..1000003 (1,000,004 values), and directly with the original for 0..10000 (10,001 values). Both large-prime objectives pass. This validates the tested domain; the factor argument supports correctness beyond it.')
    image('charts/Q7_divisions.png','Original and redesigned total integer divisions, including condition quotients.')
    h('F Defend the final design 2 marks')
    p('For 1000003, 1498 of 1999 divisions are removed, a 74.937% reduction and a division-count ratio of about 3.99. This does not claim a 3.99-fold wall-clock speedup: branches and other work still exist. The design adds special cases and paired tests but no input-sized storage. The original remains easier to teach and inspect; for small values such as 5 both versions perform three total divisions. For many bounded ticket queries, Q5’s sieve may be preferable because it shares preprocessing across queries. The 6k+/-1 design is the final choice for isolated tickets when memory is constrained.')
    shot('Q7','redesign')
    page('Source code listings')
    p('These are the final sources compiled by run_all.py. Long source lines wrap for display; compile the repository files. All external input is stored under each task inputs folder; empty files indicate self-contained experiments. Complete-the-Code files preserve every supplied starter line and main, inserting statements only at TODO blocks.')
    for file in sorted(R.glob('Q*/*.c')):
        h(str(file.relative_to(R)).replace('\\','/'))
        # Explicit physical wrapping keeps long C lines inside the printable width.
        lines=[]
        for line in file.read_text().splitlines():
            lines.extend(textwrap.wrap(line,width=100,replace_whitespace=False,drop_whitespace=False,subsequent_indent='    ') or [''])
        code('\n'.join(lines),7.5)
    page('Reproduction and verification')
    p('From the repository directory, run python run_all.py to compile and execute all C files. Run python verify.py to validate hashes, diagnostics, starter preservation, expected stdout, audit coverage, loan rows and the Q7 objective. The README lists each exact compile command and input redirection. The author_tasks.py file records source generation; it is not needed to reproduce runs.')
    code((R/'qa/verification.txt').read_text(),9)
    p('Raw stdout and stderr are preserved separately with SHA-256 hashes in each task manifest. The screenshot manifest records dimensions and exact source-line coverage for each image. Charts use measured raw values, not estimated timings. Git history contains the setup commit, seven task commits, a correction commit and final documentation commit.')
    h('Submission reference')
    p('Source: CO2_Assignment_2_.docx.pdf, supplied assignment, seven questions and mark distribution totalling 50. The assignment source is retained under reference. The provided document requests a working GitHub URL; the editable cover placeholder is ready to replace after the repository is published.')
    d.core_properties.author='Chris Abraham George'; d.core_properties.title='CSA02 Assignment 2 CO2 C Programming'; d.core_properties.subject='Executed experiments and design evaluation'
    footer=sec.footer.paragraphs[0]; footer.alignment=2
    r=footer.add_run('Page '); r.font.size=Pt(9)
    field=OxmlElement('w:fldSimple'); field.set(qn('w:instr'),'PAGE'); footer._p.append(field)
    for root in (d.styles.element,d.element):
        for border in list(root.iter(qn('w:pBdr'))): border.getparent().remove(border)
    d.save(R/NAME)

def readme():
    commands=[]
    for file in sorted(R.glob('Q*/outputs/manifest.json')):
        for row in json.loads(file.read_text()):
            task=file.parent.parent.name; name=Path(row['source']).stem
            commands += [' '.join(row['command']),f'build/{task}_{name}.exe < {task}/inputs/{name}.txt']
    text=f'''# CSA02 Assignment 2 CO2

Chris Abraham George | Register number 1911260256  
SIMATS Engineering | B.E / B.Tech CSE  
Course: CSA02 C Programming | Maximum marks: 50

Repository link: {LINK}

## Environment

Detected compiler (not a hardcoded requirement):

```text
{(R/'environment/gcc.txt').read_text().strip()}
```

{(R/'environment/git.txt').read_text().strip()}; {(R/'environment/python.txt').read_text().strip()}.

## Reproduce all programs

From this directory with gcc and Python on PATH:

```powershell
python run_all.py
python verify.py
```

All final C programs use `-std=c11 -Wall -Wextra`; Q6 additionally uses `-lm`.
Only Q1/ub_demo.c intentionally emits a real `-Wsequence-point` warning, compiled with `-std=c11 -Wall`.
The runner rejects any unexpected compiler diagnostic, failed run or expected-output mismatch.
It preserves stdout/stderr bytes without newline normalization and writes the actual commands and hashes.
No timings are claimed. Counts refer to source-level operations.

## Exact compile and run commands

The runner creates `build/` first. The following commands are recorded from actual runs.
For manual input redirection use a shell supporting `<`, such as `cmd.exe`; the Python runner works directly from PowerShell.

```text
{chr(10).join(commands)}
```

## Results

- Q1: original bill totals/nets agree with precommitted predictions; discounted-base GST corrects senior bills. Integer truncation and real undefined-behaviour diagnostics are analysed.
- Q2: 333 concessions for all five orders; 750 verifier calls for cheap-first/nested if versus 1000 for server-first/eager/full audit. The audit output covers all 1000 passenger IDs.
- Q3: starter output matches exactly; bit and byte-array operations agree; states use 1 versus 8 bytes per home on the detected target.
- Q4: 22 boundary inputs and all 301 integers -100..200 agree across ladder, switch and table. Missing return changes the S results to A. Scholarship thresholds are explicit experimental policy, since the assignment gives no numeric income bands.
- Q5: modulo counts for 1000003 fall from 1000001 to 999. All four loop variants agree with the sieve over 0..10000. Safe conditions additionally count quotient divisions. The sieve performs 2122051 marking visits in 1000004 bytes and finds 78499 primes.
- Q6: six-month hand schedule matches independent Decimal arithmetic; interest Rs 645.38226624. A Rs 200.01 repayment hits the 360-month cap; the formula predicts 501 months. Rs 200 or less is rejected as non amortizing.
- Q7: total divisions on 1000003 drop 1999 -> 501 (74.937%). Validation agrees with the sieve for all 1000004 values 0..1000003; original/revised also agree over 0..10000.

## Starter fidelity and the Q5 printed-output discrepancy

Q3, Q4 and Q5 retain the PDF starter in `starter.txt`. Only TODO blocks receive code; `main()` is identical.
Fixtures compare actual bytes, including Q4's trailing space and Windows CRLF line endings.
Q5 uses the overflow-safe equivalent `i <= n / i` to implement the mathematical `i*i <= n` condition.
The PDF's displayed expected block has inconsistent leading whitespace for 97 and 1000003 relative to its own `%8lu` format.
The exact main is preserved, and the fixture follows that format: six leading spaces for 97, five for 100, four for 7919 and one for 1000003.
The report documents the literal printed-block mismatch; no output has been modified to hide it.

## Files and evidence

- `Q1/` through `Q7/`: C sources, input files, expected fixtures where applicable, raw output files, compilation diagnostics, command transcripts, execution manifests and 300 DPI transcript images.
- `PREDICTIONS.md`: predictions committed before execution.
- `charts/`: charts generated from raw measured values.
- `qa/verification.txt`: independent checks; `qa/screenshots.json`: dimensions, nonblank checks and line coverage.
- `{NAME}`: complete report, analysis, measurements, screenshots and final source listings.
- `reference/`: supplied assignment and extracted text.
- `author_tasks.py`: source materialization helper (requires pypdf, only needed to regenerate sources from the reference PDF).
- `build_report.py`: creates screenshot renderings, charts, README and Word report (requires Pillow, matplotlib, python-docx).

Transcript images are rendered from captured execution records, not photographs of an OS terminal window. Long transcripts are paginated without omitting lines. Complete raw outputs remain authoritative.

## Git and submission

This directory is a separate Git repository on `main`; existing DBMS work in the parent workspace is preserved.
Use `git log --oneline --reverse` to inspect progressive setup, task and final-documentation commits.
No origin was configured during preparation, so the report contains the requested editable GitHub placeholder.
Before submission, create the matching GitHub repository, push this history, replace the placeholder with the actual URL and grant the faculty access.
The cover leaves Section and Submission Date blank.
'''
    (R/'README.md').write_text(text,encoding='utf-8')

if __name__=='__main__': visuals(); report(); readme(); print('Built report, README, transcript images and three measured-data charts.')
