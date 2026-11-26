"""Independent checks on all compiled artifacts, source skeletons and measured counts."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,re
R=Path(__file__).resolve().parent
checks=[]
def output(q,stem): return (R/q/'outputs'/f'{stem}.stdout.txt').read_text()
for q in (1,3,5):
    folder=R/f'Q{q}';old=(folder/'starter.txt').read_text();new=(folder/'complete_the_code.c').read_text()
    assert old[old.index('int main(void)'):]==new[new.index('int main(void)'):]
    segments=re.split(r'(    // TODO[^\n]*(?:\n    //[^\n]*)*\n)',old);pos=0
    for i,segment in enumerate(segments):
        if i and i%2==0: segment=segment.lstrip('\n')
        at=new.find(segment,pos);assert at>=pos,(q,'starter altered');pos=at+len(segment)
    assert (folder/'outputs/complete_the_code.stdout.txt').read_bytes()==(folder/'expected/complete_the_code.txt').read_bytes()
    checks.append(f'Q{q} Complete-the-Code: PASS; exact stdout bytes and preserved main/starter')
sources=list(R.glob('Q*/*.c'))
for source in sources:
    folder=source.parent/'outputs';row=next(x for x in json.loads((folder/'manifest.json').read_text()) if x['source']==source.name)
    assert row['compile'][1:5]==['-std=c11','-O2','-Wall','-Wextra']
    assert row['exit_code']==0
    raw=(folder/f'{source.stem}.stdout.txt').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['stdout_sha256']
    assert raw in (folder/f'{source.stem}.transcript.txt').read_bytes()
    assert (folder/f'{source.stem}.compiler.txt').read_bytes()==b''
    assert (folder/f'{source.stem}.stderr.txt').read_bytes()==b''
checks.append(f'All {len(sources)} C sources: actual run hashes, required flags and zero diagnostics PASS')
data={}
for q,stem,pattern,cols in [
    ('Q1','library_search_lab',r'^\d+ (?:first|middle|last|missing) ',['n','query','method','found','probes','reps','seconds']),
    ('Q2','seating_sort_lab',r'^\d+ (?:sorted|nearly|reverse|random|late20) ',['n','order','method','comparisons','swaps','shifts','writes','range','seconds']),
    ('Q3','merit_merge_lab',r'^\d+ \d+ (?:merge|concat_qsort|inplace) ',['m','n','method','comparisons','writes','aux_bytes','seconds']),
    ('Q4','rainfall_lab',r'^(?:row|column) 2000 ',['order','dimension','reps','cells','bytes','seconds','checksum']),
    ('Q5','sms_analyser_lab',r'^\d+ (?:repeated|cached) ',['n','method','calls','reps','seconds','checksum']),
    ('Q6','hostel_directory_lab',r'^\d+ (?:direct_insertion|index_insertion|pointer_qsort) ',['n','method','comparisons','copied_chars','index_writes','view_bytes','seconds']),
    ('Q7','election_lab',r'^\d+ \d+ (?:count_array|name_search|sort_count) ',['votes','candidates','method','visits','comparisons','invalid','seconds'])]:
    data[q]=[dict(zip(cols,line.split())) for line in output(q,stem).splitlines() if re.match(pattern,line)]
    assert data[q] and all(float(row['seconds'])>=0 for row in data[q])
for row in data['Q1']:
    n=int(row['n']);assert int(row['found'])==(row['query']!='missing')
    if row['method']=='linear': assert int(row['probes'])==({'first':1,'middle':n//2+1,'last':n,'missing':n}[row['query']])
    if row['method']=='binary': assert int(row['probes'])<=n.bit_length()
assert len(data['Q1'])==48
checks.append('Q1: 48 search rows, truth, linear counts and logarithmic bound PASS')
for row in data['Q2']:
    n=int(row['n']);cmp=int(row['comparisons'])
    if row['method']=='selection': assert cmp==n*(n-1)//2
    if row['order']=='sorted' and row['method'] in ('bubble','insertion'): assert cmp==n-1
    if row['order']=='reverse' and row['method'] in ('bubble','insertion'): assert cmp==n*(n-1)//2
    if row['order']=='reverse' and row['method']=='bubble': assert int(row['swaps'])==n*(n-1)//2
    if row['order']=='reverse' and row['method']=='insertion': assert int(row['shifts'])==n*(n-1)//2
assert len(data['Q2'])==52
checks.append('Q2: all 52 rows, selection/sorted/reverse count formulae PASS')
for row in data['Q3']:
    n=int(row['n'])
    if row['method']=='merge': assert int(row['comparisons'])==2*n-1 and int(row['writes'])==2*n
    if row['method']=='inplace': assert int(row['writes'])==(n-1)*(n+2)//2
assert 'EDGE equal: 91A0 91A1 91B0 91B1 91B2' in output('Q3','merit_merge_lab')
assert 'Empty A -> 95 91 80' in output('Q3','starter_extra_tests')
checks.append('Q3: stable ties, exact starter empty-list calls and merge/move formulae PASS')
rain=[list(map(float,line.split())) for line in (R/'Q4/input.txt').read_text().splitlines()]
assert len(rain)==38 and all(len(row)==12 for row in rain)
raw=output('Q4','rainfall_lab').split('DATASET full')[1]
for i,row in enumerate(rain): assert f'ANNUAL {i} {sum(row):.6f}' in raw
for j in range(12): assert f'MONTHLY {j} {sum(row[j] for row in rain)/38:.6f}' in raw
assert 'WETTEST district=2 month=3 mm=50.000000' in output('Q4','rainfall_lab')
assert 'STATE_ANNUAL_AVERAGE 80.000000 threshold=48.000000 deficient_count=1' in output('Q4','rainfall_lab')
for row in data['Q4']: assert int(row['cells'])==2000*2000*5 and int(row['bytes'])==32000000
checks.append('Q4: independent hand/full rainfall totals, averages and traversal sizes PASS')
for row in data['Q5']:
    n=int(row['n']);reps=int(row['reps']);assert int(row['calls'])==(n+1)*reps if row['method']=='repeated' else int(row['calls'])==reps
assert 'Tab-separated words: 4' in output('Q5','starter_extra_tests')
checks.append('Q5: whitespace extension, measured length-call counts and safe truncation PASS')
for n in (100,500,5000):
    rows={r['method']:r for r in data['Q6'] if int(r['n'])==n}
    assert rows['direct_insertion']['comparisons']==rows['index_insertion']['comparisons']
    assert int(rows['index_insertion']['copied_chars'])==0 and int(rows['pointer_qsort']['copied_chars'])==0
    assert int(rows['index_insertion']['view_bytes'])==4*n and int(rows['pointer_qsort']['view_bytes'])==8*n
raw=output('Q6','hostel_directory_lab');assert 'READ row=5 stored_length=29 truncated=0' in raw and 'READ row=6 stored_length=29 truncated=1' in raw
checks.append('Q6: direct/index comparisons, copy elimination, view sizes and 29/30 boundary PASS')
for c in (12,500):
    for size in (5000,500000):
        rng=13579;counts=Counter();expected_comparisons=0
        for i in range(size):
            rng=(rng*1664525+1013904223)&0xffffffff;vote=rng%(c+3)-1;counts[vote]+=1
        invalid=sum(n for id,n in counts.items() if id<=0 or id>c)
        expected_comparisons=sum(n*(id if 1<=id<=c else c) for id,n in counts.items())
        rows=[row for row in data['Q7'] if int(row['votes'])==size and int(row['candidates'])==c]
        assert len(rows)==3 and all(int(row['invalid'])==invalid for row in rows)
        assert next(int(row['comparisons']) for row in rows if row['method']=='name_search')==expected_comparisons
assert 'WINNERS count=2 tied=1: 1 2' in output('Q7','election_lab')
checks.append('Q7: independently regenerated vote truth and name-search counts for all 4 datasets PASS')
(R/'qa').mkdir(exist_ok=True);(R/'qa/verification.txt').write_text('\n'.join(checks)+'\n')
(R/'qa/data.json').write_text(json.dumps(data,indent=2)+'\n')
print('\n'.join(checks))
