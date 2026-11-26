"""Independent evidence checks, including immutable starter text and Decimal loan recurrence."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,re
R=Path(__file__).resolve().parent
checks=[]
for q in ('Q3','Q4','Q5'):
    starter=(R/q/'starter.txt').read_text()
    completed=(R/q/'complete.c').read_text()
    # The preserved source segments must occur in order; only TODO blank lines gain code.
    parts=re.split(r'(    // TODO[^\n]*(?:\n    //[^\n]*)?\n)',starter)
    pos=0
    for i,part in enumerate(parts):
        if i>0 and i%2==0: part=part.lstrip('\n')
        found=completed.find(part,pos)
        assert found>=pos, (q,'starter text altered')
        pos=found+len(part)
    assert completed[completed.index('int main(void)'):]==starter[starter.index('int main(void)'):]
    assert (R/q/'expected/complete.txt').read_bytes()==(R/q/'outputs/complete.stdout.txt').read_bytes()
    checks.append(q+': starter and main preserved; exact expected bytes PASS')
for source in sorted(R.glob('Q*/*.c')):
    output=source.parent/'outputs'
    warning=(output/(source.stem+'.compiler.txt')).read_bytes()
    assert bool(warning)==(source.stem=='ub_demo')
    rows=json.loads((output/'manifest.json').read_text())
    row=next(r for r in rows if r['source']==source.name)
    assert row['exit_code']==0
    assert row['stdout_sha256']==hashlib.sha256((output/(source.stem+'.stdout.txt')).read_bytes()).hexdigest()
    assert (output/(source.stem+'.stdout.txt')).read_bytes() in (output/(source.stem+'.transcript.txt')).read_bytes()
checks.append('All C programs: real execution manifest hashes and warning policy PASS')
b=Decimal(10000); interest=Decimal(0); schedule=[]
while b>0:
    i=b*Decimal('.02'); due=b+i; paid=min(Decimal(2000),due)
    schedule.append([b,i,paid,due-paid]); interest+=i; b=due-paid
assert len(schedule)==6 and interest==Decimal('645.38226624')
raw=(R/'Q6/outputs/loan.stdout.txt').read_text()
for k,row in enumerate(schedule,1):
    assert f'{k} '+ ' '.join(f'{v:.8f}' for v in row) in raw
checks.append('Q6: exact Decimal recurrence agrees with all 6 C schedule rows PASS')
q2=(R/'Q2/outputs/concession.stdout.txt').read_text()
audits=re.findall(r'^audit passenger=(\d+) card=(\d+)$',q2,re.M)
assert [int(a[0]) for a in audits]==list(range(1000))
assert all(int(card)==(int(i)%10==0) for i,card in audits)
assert '0 1000 333 750' in q2 and '3 1000 333 750' in q2
checks.append('Q2: 1000 unique audit entries, truth and call-count checks PASS')
q7=(R/'Q7/outputs/redesign.stdout.txt').read_text()
for line in q7.splitlines()[1:]:
    if line.startswith('Validation:'): break
    n,p,om,nm,oq,nq,ot,nt,pc=line.split()
    assert int(ot)==int(om)+int(oq) and int(nt)==int(nm)+int(nq)
    if int(n) in (7919,1000003): assert int(nt)*2<=int(ot)
checks.append('Q7: counts recomputed and objective >=50% reduction on both large primes PASS')
reference=(R/'reference/assignment.txt').read_text(encoding='utf-8')
printed=reference.split('Expected output:',3)[3].split('Change the condition')[0].strip('\n')
observed=(R/'Q5/outputs/complete.stdout.txt').read_text().strip('\n')
differences=[dict(line=i,printed=repr(a),actual=repr(b)) for i,(a,b) in enumerate(zip(printed.splitlines(),observed.splitlines()),1) if a!=b]
assert [r['line'] for r in differences]==[1,4]
checks.append('Q5: PDF printed whitespace discrepancy independently confirmed on rows 1 and 4')
(R/'qa').mkdir(exist_ok=True)
(R/'qa/Q5_printed_expected_comparison.json').write_text(json.dumps(differences,indent=2)+'\n')
(R/'qa/verification.txt').write_text('\n'.join(checks)+'\n')
print('\n'.join(checks))
