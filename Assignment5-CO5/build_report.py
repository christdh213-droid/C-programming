from pathlib import Path
import sys,re,json,hashlib,struct,datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engineering_support'))
from artifacts import Report,screenshots,ROOT,URL
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle
R=Path(__file__).resolve().parent
for folder in ['charts','qa']:(R/folder).mkdir(exist_ok=True)
def raw(task,name):return (R/task/'outputs'/f'{name}.stdout.txt').read_text()
checks=[]
for task in ['TaskB1','TaskB3','TaskB4']:
    a=(R/task/'starter.txt').read_text();b=(R/task/'complete_the_code.c').read_text()
    assert a[a.index('int main(void)'):]==b[b.index('int main(void)'):]
    parts=re.split(r'(\s*// TODO[^\n]*(?:\n\s*//[^\n]*)*\n)',a);pos=0
    for i,part in enumerate(parts):
        if i and i%2==0:part=part.lstrip('\n')
        at=b.find(part,pos);assert at>=pos;pos=at+len(part)
    assert (R/task/'expected/complete_the_code.txt').read_bytes()==(R/task/'outputs/complete_the_code.stdout.txt').read_bytes()
    checks.append(task+' Complete-the-Code PASS: immutable main/skeleton and exact stdout bytes')
for manifest in R.glob('Task*/outputs/manifest.json'):
    for row in json.loads(manifest.read_text()):
        name=Path(row['source']).stem;assert (manifest.parent/(name+'.compiler.txt')).read_bytes()==b''
        assert row['compile_exit']==row['exit_code']==0
        assert hashlib.sha256((manifest.parent/(name+'.stdout.txt')).read_bytes()).hexdigest()==row['stdout_sha256']
checks.append('Every final ordinary build: zero diagnostics, exit0, captured stdout SHA256 PASS')
counts=[tuple(map(int,m)) for m in re.findall(r'CALLS n=(\d+) linear=(\d+) fast=(\d+)',raw('TaskB1','recursion_lab'))]
for n,l,f in counts:assert l==n+1 and f==n.bit_length()+1
stress=json.loads((R/'TaskB1/outputs/stack_stress.json').read_text());assert stress[-1]['exit']&0xffffffff==0xC00000FD
checks.append(f"Stack overflow OBSERVED at first failing sweep n={stress[-1]['n']}; previous tested n={stress[-2]['n']} passed; this is not the exact minimum threshold")
cases=json.loads((R/'TaskB2/outputs/adversarial_cases.json').read_text());assert all(x['actual']==x['expected'] for x in cases)
checks.append(f'Adversarial CLI {len(cases)} cases: expected statuses PASS')
files=[(int(n),fmt,int(size),float(w),float(r)) for n,fmt,size,w,r in re.findall(r'FILE n=(\d+) format=(\w+) bytes=(\d+) write_cpu=([\d.]+) read_verify_cpu=([\d.]+)',raw('TaskB3','file_benchmark'))]
for n,fmt,size,w,r in files:assert (R/f'TaskB3/data/donors_{n}.{ "bin" if fmt=="binary" else "txt"}').stat().st_size==size
# Independent Python decoding and eligibility calculation, without executing C again.
data=(R/'TaskB3/data/donors_100000.bin').read_bytes();fmt=struct.Struct('<i48s4si12s4i');assert fmt.size==88 and len(data)==100000*88
eligible=[];h=[0]*25;today=datetime.date(2026,11,26);end=today+datetime.timedelta(days=7)
for i,v in enumerate(fmt.iter_unpack(data)):
    id,name,group,age,phone,day,month,year,hospital=v
    assert id==7001+i and 1<=hospital<=25
    if 18<=age<=65 and datetime.date(year,month,day)<=today and datetime.date(year,month,day)+datetime.timedelta(days=90)<=end:eligible.append((age,id));h[hospital-1]+=1
memory=raw('TaskB4','nightly_report');stream=raw('TaskB4','stream')
assert f'eligible={len(eligible)} youngest_id={min(eligible)[1]}' in memory
for s in [memory,stream]:assert [int(x) for x in re.findall(r'HOSPITAL \d+ eligible=(\d+)',s)]==h
checks.append('Independent Python decode of 100000 records: eligibility count, youngest ID and 25 hospital totals PASS for both strategies')
for t in ['TaskB2','TaskB4']:
    assert 'cannot find -lasan' in (R/t/'outputs/sanitizer_probe.transcript.txt').read_text()
checks.append('Sanitizer verification UNAVAILABLE: real GCC link probes fail, missing libasan; zero-leak certification NOT obtained')
(R/'qa/verification.txt').write_text('\n'.join(checks)+'\n');print('\n'.join(checks))
screenshots(R)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):fig.savefig(R/'charts'/name,dpi=300,bbox_inches='tight',facecolor='white');plt.close(fig)
def box(ax,x,y,w,h,text):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02',facecolor='#e0edf4',edgecolor='#4d687a'));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
fig,ax=plt.subplots(figsize=(8,3));ax.set(xlim=(0,10),ylim=(0,5));ax.axis('off');box(ax,4,4,2,.65,'Application / CLI')
nodes=[(.1,'Register donor'),(2.6,'Find / eligible'),(5.1,'Stock update'),(7.6,'Nightly report')]
for x,t in nodes:box(ax,x,2.5,2.2,.65,t);ax.annotate('',(x+1.1,3.15),(5,4),arrowprops={'arrowstyle':'->','color':'#4d687a'})
for x,t in [(1.3,'Validate + append'),(4,'Load / save files'),(6.7,'Summary + export')]:box(ax,x,.7,2.1,.7,t)
for start,end in [((1.2,2.5),(2.35,1.4)),((3.7,2.5),(5.05,1.4)),((6.2,2.5),(5.05,1.4)),((8.7,2.5),(7.75,1.4))]:ax.annotate('',end,start,arrowprops={'arrowstyle':'->','color':'#4d687a'})
ax.set_title('A1 Functional decomposition and explicit ownership');save(fig,'a1_structure_chart.png')
fig,ax=plt.subplots(figsize=(7,4.3));ax.set(xlim=(0,10),ylim=(0,7));ax.axis('off')
for i,n in enumerate([30,15,7,3,1,0]):box(ax,.4,5.6-i*.84,4,.65,f'power(2, {n})'+('  BASE: return1' if n==0 else '  waiting for half'))
ax.text(5.1,4.2,'Deepest instant: six live power frames\nCaller/main lies below this schematic.\n\nDescent: 30 -> 15 -> 7 -> 3 -> 1 -> 0\nUnwind: 1 -> 2 -> 8 -> 128\n                  -> 32768 -> 1073741824',va='center',fontsize=10);ax.set_title('A2 Deepest halving-power call stack (logical frames)');save(fig,'a2_call_stack.png')
fig,ax=plt.subplots(figsize=(8,2.7));ax.set(xlim=(-.3,8.2),ylim=(-1.5,2));ax.axis('off');values=[40,25,12,8,30,9,4,15]
for i,v in enumerate(values):ax.add_patch(Rectangle((i,0),1,.75,facecolor='#dce8f0',edgecolor='#536777'));ax.text(i+.5,.38,str(v),ha='center');ax.text(i+.5,-.24,f'[{i}]',ha='center',fontsize=9);ax.text(i,1,str(i*4),ha='center',fontsize=8)
ax.text(0,1.45,'Relative byte offsets (measured sizeof(int)=4); values are the executed pointer test',fontsize=9)
ax.annotate('p = stock',(.1,0),(.1,-1),arrowprops={'arrowstyle':'->'});ax.annotate('p+3: address of8\n*(p+3) = p[3] =8',(3.5,0),(3,-1.15),arrowprops={'arrowstyle':'->'},ha='center',fontsize=9);ax.text(6,-1,'*p++ reads40\nthen p becomes stock+1',ha='center',fontsize=9);save(fig,'a3_pointer_memory.png')
fig,ax=plt.subplots(figsize=(7,3.6));ax.loglog([v[0] for v in counts],[v[1] for v in counts],'o-',label='Linear: measured n+1');ax.loglog([v[0] for v in counts],[v[2] for v in counts],'s-',label='Halving: measured bit_length(n)+1');ax.set(xlabel='Exponent n (base1 to avoid arithmetic overflow)',ylabel='Function calls',title='B1 Actual call counts');ax.grid(alpha=.2);ax.legend();fig.tight_layout();save(fig,'b1_recursion_calls.png')
fig,axes=plt.subplots(1,2,figsize=(9,3.6))
for mode,color in [('text','#b66b34'),('binary','#397c9b')]:
    rows=[x for x in files if x[1]==mode and x[0]>=1000];x=[r[0] for r in rows];axes[0].loglog(x,[r[2] for r in rows],'o-',label=mode,color=color);axes[1].plot(x,[r[3]+r[4] for r in rows],'o-',label=mode,color=color)
axes[0].set(xlabel='Donors',ylabel='Actual file bytes',title='Measured storage');axes[1].set(xlabel='Donors',ylabel='clock-derived seconds',title='Write + verified read (single run)');axes[1].ticklabel_format(axis='x',style='sci',scilimits=(0,0))
for ax in axes:ax.legend();ax.grid(alpha=.2)
fig.tight_layout();save(fig,'b3_text_vs_binary.png')
d=Report(R,5,'Modular Memory-aware and Persistent Program Engineering')
d.chapter('Assessment and execution method')
d.table(['Component','Task','Marks'],[['Part A','A1 Functional decomposition',7],['Part A','A2 Recursive design',5],['Part A','A3 Pointer design',5],['Part A','A4 Dynamic memory',4],['Part A','A5 File design',4],['Part B','B1 Instrumented recursion',7],['Part B','B2 Adversarial input',5],['Part B','B3 Text versus binary',8],['Part B','B4 Production decision',5],['Total','',50]])
d.p('All final ordinary C files were compiled and executed using -std=c11 -Wall -Wextra, with zero compiler diagnostics. Starters and exact byte fixtures are retained. Intentional unsafe/crash children and failed sanitizer probes are clearly separated. Source PDFs provide assignment context; the requested combined GitHub repository and folder names take precedence over PDF repository-name examples.')
d.code((ROOT/'engineering_support/environment/gcc.txt').read_text(),8)
d.p('Measurement discipline: output fields named cpu in B3 are raw clock()-derived seconds. They are implementation-dependent runtime measurements on Windows, not an assertion of hardware CPU cycles. Opening, closing and verification costs are included where shown. These are single local runs with cache, scheduler and clock-resolution effects; zero ticks are retained, and no repeated-run statistical speedup is claimed. Peak RAM is Windows PeakWorkingSetSize in separate processes; it includes runtime overhead beyond donor storage.')
d.p('Memory-check limitation: the installed MinGW GCC cannot link -fsanitize=address or address,leak because libasan is absent; valgrind is unavailable. Actual linker errors are retained. Safe executions, independent checks and source cleanup evidence passed, but the requested sanitizer/Valgrind clean-memory certification is NOT fulfilled. The report does not substitute native crash status or manual reasoning for it.')
part=(R/'PART_A.md').read_text(encoding='utf-8');sections=re.split(r'^## ',part,flags=re.M)[1:]
for section in sections:
    title,body=section.split('\n',1);d.chapter('Part A '+title)
    chart={'A1':'a1_structure_chart.png','A2':'a2_call_stack.png','A3':'a3_pointer_memory.png'}.get(title[:2])
    if chart:d.picture('charts/'+chart,'Design diagram; logical relationships and byte offsets, not fabricated physical addresses.')
    in_c=False;buf=[];algorithm=[]
    for line in body.strip().splitlines()+['']:
        if line.startswith('```'):
            if in_c:d.code('\n'.join(buf));buf=[]
            in_c=not in_c;continue
        if in_c:buf.append(line);continue
        if line.startswith('ALGORITHM '):
            if algorithm:d.code('\n'.join(algorithm),8);algorithm=[]
            algorithm.append(line)
        elif algorithm:
            if line.strip():algorithm.append(line)
            else:d.code('\n'.join(algorithm),8);algorithm=[]
        elif line.strip():d.p(line)
d.chapter('TaskB1 Instrumented Recursion')
d.h('Validation and comparison with design')
d.p('The implementation follows Part A: sum digits then recurse on the smaller sum, and compute one cached half-power before squaring. All three power methods agree for zero, one, ordinary and custom representable values. 0^0 is defined as1 for this exercise. Nonnegative exponents and representable arithmetic are preconditions; large call-count tests use base1, preventing signed overflow from confounding the stack experiment.')
d.code(raw('TaskB1','complete_the_code'));d.code(raw('TaskB1','recursion_lab'))
d.table(['n','Linear measured / predicted','Halving measured / predicted'],[[n,f'{l} / {n+1}',f'{f} / {n.bit_length()+1}'] for n,l,f in counts]);d.picture('charts/b1_recursion_calls.png','Call counts from the executed recursion_lab program.')
d.h('Observed stack limit and duplicate recursion')
d.p(f"The bounded doubling sweep passed at n={stress[-2]['n']} and first failed at tested n={stress[-1]['n']} with Windows exit0xC00000FD (STATUS_STACK_OVERFLOW). This is an observed failing exponent, not the smallest possible threshold and not a portable C limit. The same separate binary's iterative mode succeeded at that exponent and twice it. Compilation used no optimization flag, and a volatile call counter retained real work. Frame size, linker stack reservation and optimization change the threshold.")
d.p('Cached halving at30 uses6 calls. Replacing the cached halves with two independent half calls at every positive exponent gives D(n)=1+2D(floor(n/2)), D(0)=1: the measured total is63. The requested61 instead occurs with an odd-decrement/even-duplicate algorithm; that second algorithm was also executed and measured61. The immutable starter prints fast  : with two spaces before the colon, so its fixture preserves that spelling rather than the conflicting fast: request.')
d.h('Alternative Concept and Complexity Analysis');d.p('Iterative square-and-multiply maintains result, base and remaining exponent. Multiply result by base for an odd exponent, halve the exponent, and square base only when further work remains. It uses O(log n) multiplications and O(1) stack, versus O(log n) stack for cached halving and O(n) time/stack for linear recursion. Duplicate-halves expands O(n) calls and retains O(log n) depth.')
d.evidence('TaskB1');d.sources('TaskB1')
d.chapter('TaskB2 Adversarial Inputs and Memory Safety')
d.h('CLI design and executed cases')
d.p('bloodbank_cli supports initialization, group-stock lookup, validated issuing, bounded donor-name registration and a pointer demonstration. find reports group stock; eligibility search and its interfaces are designed in Part A, while the nightly implementation performs the eligibility scan. Stock is read and validated before mutation; insufficient units and invalid input leave the file unchanged. Files are closed on all handled paths. The registration extension records a name/group pair for this input experiment; the full case-study donor fields are implemented in donor_model.h and the B3/B4 data pipeline.')
d.table(['Case','Arguments / input','Expected and actual exit'],[[x['case'],' '.join(x['args']) or '(none)',f"{x['expected']} / {x['actual']}"] for x in cases])
d.p('The 256-character name is drained and rejected by the CLI before appending. The small safe fgets demonstration stores at most15 characters plus NUL and reports truncation. Missing and read-only files produce perror diagnostics and exit1; malformed files are rejected. Normal issue of two A- units is followed by a verified remaining-stock output. Pointer output uses real captured addresses; the Part A diagram uses relative offsets to avoid inventing physical locations.')
d.code(raw('TaskB2','adversarial_scanf_demo'));d.code(raw('TaskB2','pointers'))
d.h('Intentional unsafe child and unavailable sanitizer')
d.p('The unbounded scanf("%s") variant was isolated in a child with the overlong input. Its native run returned0xC0000005 (access violation); this is an observed UB outcome, not an AddressSanitizer diagnosis. The corrected path bounds input, drains the remainder and maintains NUL termination. Actual attempts to build both the demonstration with address instrumentation and the CLI with address,leak failed to link due to missing libasan. No clean sanitizer output exists, and no claim of zero detected leaks is made. Reproduce these probes on an ASan-capable GCC platform to close this environment gap.')
d.h('Alternative Concept and Complexity Analysis');d.p('POSIX getline(&buffer, &capacity, stdin) grows a heap buffer to hold the entire line. Reading L characters takes O(L) time and O(L) heap space; the caller must free buffer even after a failed call if it was allocated. fgets uses O(k) fixed storage and O(L) total time when draining an oversized line. getline is not ISO C11 and is therefore an alternative design rather than an unguarded dependency in these programs.')
d.evidence('TaskB2');d.sources('TaskB2')
d.chapter('TaskB3 Text versus Binary Files')
d.h('Small-data correctness and fixed-record update')
d.code(raw('TaskB3','complete_the_code'))
d.p('Index3 is zero-based: the fourth record, group4, changes from8 to20. Record9 lies beyond five records; fread fails before any write, so the existing records and length remain unchanged. The fixture retains the starter printf trailing space before the final newline. Ten generated donors round-trip in both formats, checked by individual fields rather than memcmp, which would conflate structure padding with logical equality.')
d.h('Measured file sizes and runtime')
d.table(['Donors','Format','Bytes','Write clock s','Read + verify clock s'],files);d.picture('charts/b3_text_vs_binary.png','Single-run observations including file open/close and field verification. Timing noise and cache effects remain.')
d.code('\n'.join(raw('TaskB3','file_benchmark').splitlines()[-3:]))
d.p('The 50,000th donor is zero-based index49999. Binary performs one seek/read/seek/write and closes; text reads all100000 records into a new rewritten file one record at a time. The changed age and all untouched fields are verified against the expected array after both updates. The original text fixture remains available; rewrite.txt is the update result. Output reports exact observed times, not estimated complexity.')
d.h('Engineering trade-off and Alternative Concept')
d.p('Here binary records are88 bytes, including fixed arrays and date/hospital fields, aligned to4. Text is smaller for this dataset because variable-length fields omit unused name capacity, while binary supports direct record addressing. Text is preferable for interchange and audit, with validated schema/delimiters. Raw binary is appropriate for local stock and cache files tied to the current ABI; it is not portable across endianness, type-width, padding or schema changes. A production binary format should specify byte order, field widths, version and record length.')
d.p('One bulk fwrite writes n records in one library call, versus n per-record calls; both transfer O(n) data. Bulk needs O(n) preloaded array memory, while per-record writing can use O(1) extra record storage. The measured bulk run happened to be slower here despite fewer calls, illustrating why one noisy run does not prove a general speed ordering. Buffered stdio already batches per-record system writes; fewer library calls do not guarantee fewer disk operations.')
d.evidence('TaskB3');d.sources('TaskB3')
d.chapter('TaskB4 Nightly Report and Production Decision')
d.h('Growable implementation and declared policy')
d.code(raw('TaskB4','complete_the_code'))
d.p('The full program extends the starter Donor and DonorList pattern with all donor fields, hospital membership, size_t capacity and growth counters. It keeps the same0->2->4->8 doubling and temporary-pointer realloc ownership rule. Last-donation dates are validated and compared as Gregorian ordinals. The simulation reports donors age18..65 whose last donation is not in the future and whose90-day interval ends by3December2026, including donors already eligible on26November. This is a declared assignment policy rather than a medical recommendation.')
d.code('\n'.join(memory.splitlines()[:2]));d.code('\n'.join(stream.splitlines()[:2]))
def measure(s):
    m=re.search(r'clock_seconds=([\d.]+) peak_working_set_bytes=(\d+) record_bytes=(\d+) capacity=(\d+) logical_input_buffer_bytes=(\d+) realloc_calls=(\d+)',s);return m.groups()
m=measure(memory);s=measure(stream)
d.table(['Strategy','Runtime clock s','OS peak bytes','Input buffer bytes','Growth calls'],[['In memory',m[0],m[1],m[4],m[5]],['Batch256',s[0],s[1],s[4],s[5]]])
d.p(f'Independent Python decoding of the binary input confirms {len(eligible)} eligible donors, youngest eligible ID{min(eligible)[1]}, and identical totals for every hospital in both processes. Capacity131072 holds100000 records after17 successful growth calls. Logical array allocation is capacity times88 bytes; OS peak working set additionally includes runtime pages and other overhead. Realloc counts are actual calls, while relocation bytes are not claimed because realloc may extend an allocation in place.')
d.table(['Hospital','Eligible'],[[i+1,v] for i,v in enumerate(h)])
d.h('Memory safety evidence and remaining requirement')
d.p('The sole growable owner is freed and reset after use; allocation failure closes the file and frees the retained owner. A controlled injected failure fills capacity2, denies the next growth, checks pointer/size/capacity/content unchanged, then frees exactly once. This tests failure behavior, not physical out-of-memory conditions. The real ASan/LSan compile attempt fails to find libasan, so clean memory certification remains unavailable. The captured failure is included and must not be described as a successful leak check.')
d.h('Production decision and Alternative Concept')
d.p('Choose batched streaming for this nightly sequential aggregation: it matched every result, reduced measured process peak RAM and logical input buffer, and avoided reallocations. Keep the in-memory list for interactive workloads that benefit from reuse and mutation, subject to memory budgets and explicit ownership. A separate sorted ID-to-file-offset index serves occasional point lookups using fseek binary search: O(log n) index reads and O(1) working RAM, plus one donor read. It does not accelerate the full eligibility scan unless a relevant eligibility/date index is designed and maintained.')
d.p('An unsorted in-memory donor array still needs O(n) ID search. O(1) average lookup after loading requires a hash/direct index, with additional O(n) storage; sorted arrays offer O(log n). The separate on-disk index needs O(n) disk space and update/rebuild work. Both nightly strategies scan O(n); streaming uses O(batch size + hospitals) working storage, while the growable array uses O(n). These complexity differences and the actual measurements favor batch streaming for the stated report, without claiming a universal timing ranking.')
d.evidence('TaskB4');d.sources('TaskB4')
d.chapter('Reproduction and Verification')
d.code('\n'.join(checks),8)
d.p('From the repository root run the commands in README.md in task order, then build the report with the bundled Python dependencies. B4 consumes B3 generated binary data. Compiler/runtime transcripts, exact byte fixtures, case manifests and all screenshot pages remain authoritative. A source header and scripts support reproducibility; earlier CO2/CO3 assignment files were preserved.')
d.h('Shared donor model');d.code((R/'donor_model.h').read_text())
d.chapter('Common support header');d.code((ROOT/'engineering_support/lab.h').read_text())
d.p('Reference: supplied CO5_Assignment_5.docx.pdf, Part A A1 through A5 and Part B B1 through B4, retained in reference with extracted text. Part A uses algorithmic INPUT/OUTPUT/BEGIN/numbered steps/END pseudocode; C prototypes separately describe interfaces. Figures are generated with matplotlib at300DPI; terminal images render actual recorded text. GCC static analyzer checks for the CLI and nightly program completed without diagnostics, as retained in qa/static_analyzer.txt; static analysis does not replace the unavailable sanitizer verification.')
path=d.save();print(path)
compiler=(ROOT/'engineering_support/environment/gcc.txt').read_text().strip()
commands=[]
for p in sorted(R.glob('Task*/outputs/manifest.json')):
    for row in json.loads(p.read_text()):commands.append(' '.join(row['compile']))
readme=f'''# CSA02 Assignment5 CO5

Chris Abraham George | 1911260256 | SIMATS Engineering | B.E / B.Tech CSE  
CSA02 C Programming | 50 marks | [Repository]({URL})

## Exact detected compiler

```text
{compiler}
```

## Reproduce from the repository root

```text
python engineering_support/execute.py 5 TaskB1
python Assignment5-CO5/probe_b1.py
python engineering_support/execute.py 5 TaskB2
python Assignment5-CO5/probe_b2.py
python engineering_support/execute.py 5 TaskB3
python engineering_support/execute.py 5 TaskB4
python Assignment5-CO5/probe_b4.py
```

The runner sets the installed GCC PATH, compiles with zero diagnostics, captures exact stdout/stderr, and checks byte fixtures. Run B3 before B4. B3 data directory is retained; B2 init resets stock; valid-name registration appends to its demonstration log. Stress and unsafe cases run in separate children with bounded waits and recorded exit codes. Do not run the unsafe child in a production process.

Exact successful C compilation commands (working directory Assignment5-CO5):

```text
{chr(10).join(commands)}
```

Representative manual runs (same assignment working directory; use cmd.exe for `<`):

```text
build/TaskB1_complete_the_code.exe
build/TaskB1_recursion_lab.exe
build/TaskB1_stack_limit.exe iterative 64000
build/TaskB2_adversarial_scanf_demo.exe < TaskB2/inputs/overlong.txt
build/TaskB2_bloodbank_cli.exe find O+
build/TaskB2_bloodbank_cli.exe issue A- 2
build/TaskB2_bloodbank_cli.exe register O+ < TaskB2/inputs/name.txt
build/TaskB3_complete_the_code.exe
build/TaskB3_file_benchmark.exe
build/TaskB4_complete_the_code.exe
build/TaskB4_nightly_report.exe
build/TaskB4_nightly_report.exe stream
```

## Results and limits

- B1: all value tests pass; linear/halving counts match recurrences. First failing sweep exponent64000 returned0xC00000FD, iterative64000 and128000 succeeded. This is not the smallest crash threshold. Literal duplicate-halves gives63 calls; odd-decrement variant gives the requested61.
- B2: all16 adversarial CLI cases match expected statuses. Safe fgets truncates/drains, CLI rejects oversized names. Native unbounded scanf child returned0xC0000005; this is not sanitizer evidence.
- B3:10-record round trips and1000/10000/100000 datasets pass field checks. Sizes and clock-derived write/read/update/bulk measurements are in raw outputs. The text fixture is smaller than88-byte fixed records; bulk single-call writing was slower in this one run, so no universal speed ranking is claimed.
- B4:100000 donors/25 hospitals give{len(eligible)} eligible, youngest ID{min(eligible)[1]}, identical25 hospital totals. In-memory runtime{m[0]}s and peak{m[1]} bytes; batch256 runtime{s[0]}s and peak{s[1]} bytes. These are separate-process local measurements. Doubling uses17 growth calls, capacity131072. Injected allocation failure preserves the old owner and contents.
- **Sanitizer/Valgrind requirement remains unverified.** Actual GCC `-fsanitize=address` and `-fsanitize=address,leak` link attempts fail: `cannot find -lasan`. Valgrind is absent. No zero-leak claim is made. B2/B4 retain verbatim failure transcripts; repeat on a supported toolchain to close this gap.
- All three starter outputs pass exact bytes. Preserve B1 `fast  :` and B3 trailing space from immutable main despite conflicting shortened examples in the request.
- Runtime fields labelled cpu in B3 are raw C clock()-derived seconds, implementation-dependent on Windows. Timings are single-run and include documented I/O/verification costs; cache effects and resolution remain.
- Eligibility is an assignment model: age18..65,90-day interval ending by end of next7 days, simulated26Nov2026; not clinical guidance.

## Report and evidence

`CSA02_1911260256_Assignment5_Report.docx` includes PartA algorithms/prototypes,300DPI diagrams/charts, complete C sources, measurements and real-output terminal renderings. `PART_A.md` is the design source. Section and Submission Date cover fields are blank.

`qa/verification.txt` checks immutable starter structure, exact output bytes, compiler logs, SHA256 records, file sizes, all CLI statuses, observed stack status and an independent Python eligibility calculation. `qa/screenshots.json` records300DPI image dimensions/nonblank checks and complete transcript-line coverage. Images are terminal-style renderings from real transcripts, not OS-window captures.

Generate the Word report using a Python environment with python-docx, Pillow and matplotlib: `python Assignment5-CO5/build_report.py`. In PowerShell 7 render with `& ./engineering_support/render_report.ps1 -Number 5`, then audit with `python engineering_support/audit_report.py 5`. The rendering script requires PowerShell 7 because legacy Windows PowerShell stalled in Word COM export here. The Word rendering step uses installed Microsoft Word; the rendered PDF/pages are local QA artifacts.
'''
(R/'README.md').write_text(readme,encoding='utf-8')
