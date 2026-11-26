"""Materialize experiment sources and preserved PDF starter completions."""
from pathlib import Path
import re, sys
R=Path(__file__).resolve().parent
def put(q,name,code,data=''):
    d=R/q; (d/'inputs').mkdir(parents=True,exist_ok=True)
    (d/name).write_text(code.strip()+'\n',encoding='utf-8')
    (d/'inputs'/f'{Path(name).stem}.txt').write_text(data,encoding='ascii')

def starter(q,body,expected):
    import pypdf
    text='\n'.join(p.extract_text() for p in pypdf.PdfReader(R/'reference'/'CO2_Assignment_2_.docx.pdf').pages)
    blocks=re.findall(r'#include <stdio.h>.*?\n}\s*\nExpected output:',text,re.S)
    block=blocks[int(q[1])-3].rsplit('Expected output:',1)[0].rstrip()
    d=R/q; d.mkdir(exist_ok=True)
    (d/'starter.txt').write_text(block+'\n',encoding='utf-8')
    # Insert statements into the blank after TODO comment(s), preserving all starter text.
    parts=re.split(r'(    // TODO[^\n]*(?:\n    //[^\n]*)?\n)',block)
    for i in range(1,len(parts),2):
        parts[i+1]=body.pop(0)+'\n'+parts[i+1]
    put(q,'complete.c',''.join(parts))
    (d/'expected').mkdir(exist_ok=True)
    (d/'expected'/'complete.txt').write_bytes(expected.encode().replace(b'\n',b'\r\n'))

def q1():
    put('Q1','billing.c',r'''
#include <stdio.h>
int main(void) {
    int price, qty, senior;
    puts("price qty senior | original_total original_net | corrected_net");
    while (scanf("%d%d%d", &price, &qty, &senior)==3) {
        int total, net;
        total = price * qty - price * qty * 15 / 100 * senior + price * qty * 5 / 100;
        net = total > 1000 ? total - 50 : total;
        double gross=(double)price*qty;
        double discount=senior ? gross*0.15 : 0.0;
        double taxable=gross-discount;
        double tax=taxable*0.05;
        double corrected=taxable+tax;
        if (corrected>1000.0) corrected-=50.0;
        printf("%d %d %d | %d %d | %.6f\n",price,qty,senior,total,net,corrected);
    }
    puts("Static arithmetic operations when senior and coupon apply: original 11; corrected 6; comparisons/branches excluded.");
    return 0;
}''','99 3 1\n500 2 0\n1200 1 1\n')
    put('Q1','ub_demo.c',r'''
#include <stdio.h>
int main(void) {
    int count=0;
    count = count++ + 1;
    printf("Observed count = %d (undefined behaviour; not a portable result)\n",count);
    count=0;
    count += 1;
    printf("Correct increment = %d\n",count);
    return 0;
}''')

def q2():
    put('Q2','concession.c',r'''
#include <stdio.h>
static unsigned calls;
static int verify(int i) {
    ++calls;
    volatile unsigned work=0;
    for (unsigned j=0;j<100;j++) work+=j;
    (void)work;
    return i%10==0;
}
int main(void) {
    puts("mode passengers concessions verifier_calls");
    for(int mode=0;mode<5;mode++) {
        calls=0; unsigned granted=0;
        for(int i=0;i<1000;i++) {
            int senior=i%3==0, eligible=i%4!=0, ok=0;
            switch(mode) {
                case 0: ok=(senior && eligible) || verify(i); break;
                case 1: ok=verify(i) || (senior && eligible); break;
                case 2: ok=(senior & eligible) | verify(i); break;
                case 3: if(senior && eligible) ok=1; else ok=verify(i); break;
                default: { int audited=verify(i); ok=(senior && eligible)||audited; break; }
            }
            granted+=(unsigned)ok;
        }
        printf("%d 1000 %u %u\n",mode,granted,calls);
    }
    calls=0; int a=0 && verify(0); printf("0 && verify: result=%d calls=%u\n",a,calls);
    calls=0; a=1 || verify(0); printf("1 || verify: result=%d calls=%u\n",a,calls);
    calls=0; a=0 & verify(0); printf("0 & verify: result=%d calls=%u\n",a,calls);
    puts("Audit log for every passenger follows (server result computed before eligibility):");
    for(int i=0;i<1000;i++) { int card=verify(i); printf("audit passenger=%d card=%d\n",i,card); }
    return 0;
}''')

def q3():
    starter('Q3',[
'    return (unsigned char)(reg | (1u << dev));',
'    return (unsigned char)(reg & ~(1u << dev));',
'    return (unsigned char)(reg ^ (1u << dev));',
'    return (reg >> dev) & 1u;'], '00000101\n00000110\nAC is ON, PUMP is OFF\n')
    put('Q3','register_compare.c',r'''
#include <stdio.h>
#include <limits.h>
static void show(unsigned char reg) {
    for(int b=7;b>=0;b--) putchar((reg>>b)&1u ? '1':'0');
}
int main(void) {
    unsigned char reg=0, state[8]={0};
    const int devs[]={7,0,7,0};
    for(int k=0;k<4;k++) {
        unsigned mask=1u<<devs[k];
        if(k<2) { reg=(unsigned char)(reg|mask); state[devs[k]]=1; }
        else if(k==2) { reg=(unsigned char)(reg^mask); state[devs[k]]^=1; }
        else { reg=(unsigned char)(reg&~mask); state[devs[k]]=0; }
        unsigned count=0, array_count=0;
        for(int j=0;j<8;j++) { count+=(reg>>j)&1u; array_count+=state[j]; }
        printf("step=%d value=%u binary=",k+1,(unsigned)reg); show(reg);
        printf(" bit_count=%u array_count=%u\n",count,array_count);
        if(count!=array_count) return 1;
    }
    reg=2; int dev=1;
    printf("reg=2 dev=1: reg & 1 << dev = %u; (reg & 1) << dev = %u\n",reg & 1u << dev,(reg & 1u) << dev);
    signed char s=(signed char)128u;
    printf("CHAR_BIT=%d sizeof register=%zu array=%zu; signed conversion=%d right_shift=%d\n",CHAR_BIT,sizeof reg,sizeof state,(int)s,s>>1);
    puts("1000000 homes: register=1000000 bytes; array=8000000 bytes; count visits=8 per home in both.");
    return 0;
}''')

def q4():
    starter('Q4',[r'''    switch (marks / 10) {
        case 10: case 9: return 'S';
        case 8: return 'A';
        case 7: return 'B';
        case 6: return 'C';
        case 5: return 'D';
        default: return 'F';
    }'''],'100:S 95:S 83:A 50:D 49:F -5:? \n')
    # A missing-return variant preserves the starter main and produces a real changed run.
    code=(R/'Q4'/'complete.c').read_text().replace("case 10: case 9: return 'S';","case 10: case 9: /* deliberately removed return; falls through to A */")
    put('Q4','fallthrough.c',code)
    put('Q4','classifiers.c',r'''
#include <stdio.h>
static char ladder(int m) {
    if(m<0||m>100) return '?';
    if(m>=90) return 'S';
    else if(m>=80) return 'A';
    else if(m>=70) return 'B';
    else if(m>=60) return 'C';
    else if(m>=50) return 'D';
    return 'F';
}
static char sw(int m) {
    if(m<0||m>100) return '?';
    switch(m/10) {
        case 10: case 9: return 'S'; case 8: return 'A'; case 7: return 'B';
        case 6: return 'C'; case 5: return 'D'; default: return 'F';
    }
}
static char lookup(int m) {
    static const char grades[11]={'F','F','F','F','F','D','C','B','A','S','S'};
    return m<0||m>100 ? '?' : grades[m/10];
}
static const char *scholarship(char g,int income) {
    /* Explicit experiment policy: S/A and income <=200000 full, <=500000 partial. */
    if(income<0 || g=='?') return "invalid";
    if(g=='S'||g=='A') { if(income<=200000) return "full"; if(income<=500000) return "partial"; }
    return "none";
}
int main(void) {
    int m; puts("marks ladder switch lookup");
    while(scanf("%d",&m)==1) {
        char a=ladder(m),b=sw(m),c=lookup(m);
        printf("%d %c %c %c\n",m,a,b,c);
        if(a!=b||b!=c) return 1;
    }
    unsigned checked=0;
    for(int n=-100;n<=200;n++) { if(ladder(n)!=sw(n)||sw(n)!=lookup(n)) return 1; ++checked; }
    printf("Exhaustive integer range -100..200: %u agreements\n",checked);
    const int incomes[]={-1,0,200000,200001,500000,500001};
    const char gs[]={'S','A','B','?'};
    for(unsigned i=0;i<sizeof gs;i++) for(unsigned j=0;j<sizeof incomes/sizeof incomes[0];j++)
        printf("scholarship %c %d %s\n",gs[i],incomes[j],scholarship(gs[i],incomes[j]));
    return 0;
}''','-1\n0\n1\n48\n49\n50\n51\n59\n60\n61\n69\n70\n71\n79\n80\n81\n89\n90\n91\n99\n100\n101\n')

def q5():
    starter('Q5',[r'''    for (unsigned long i = 2; i <= n / i; i++) {
        checks++;
        if (n % i == 0) return 0;
    }
    return 1;'''],'      97  prime      divisions = 8\n     100  not prime  divisions = 1\n    7919  prime      divisions = 87\n 1000003  prime      divisions = 999\n')
    put('Q5','naive_complete.c',(R/'Q5'/'complete.c').read_text().replace('i <= n / i','i < n'))
    put('Q5','loops_sieve.c',r'''
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static int test(unsigned long n,int mode,unsigned long *mods,unsigned long *quotients) {
    *mods=0; *quotients=0;
    if(n<2) return 0;
    unsigned long i=2;
    if(mode==0) {
        for(;i<n;i++) { ++*mods; if(n%i==0) return 0; }
    } else if(mode==1) {
        for(;;i++) { ++*quotients; if(i>n/i) break; ++*mods; if(n%i==0) return 0; }
    } else if(mode==2) {
        while(1) { ++*quotients; if(i>n/i) break; ++*mods; if(n%i==0) return 0; ++i; }
    } else {
        ++*quotients;
        if(i>n/i) return 1;
        do { ++*mods; if(n%i==0) return 0; ++i; ++*quotients; } while(i<=n/i);
    }
    return 1;
}
int main(void) {
    const unsigned long limit=1000003;
    unsigned char *flags=calloc(limit+1,1); if(!flags) return 1;
    unsigned long marks=0, primes=0;
    for(unsigned long p=2;p<=limit/p;p++) if(!flags[p])
        for(unsigned long j=p*p;j<=limit;j+=p) { flags[j]=1; ++marks; }
    for(unsigned long n=2;n<=limit;n++) if(!flags[n]) ++primes;
    printf("sieve bytes=%lu marking_visits=%lu primes=%lu\n",limit+1,marks,primes);
    unsigned long n;
    puts("n mode prime modulo_attempts condition_quotients total_divisions");
    while(scanf("%lu",&n)==1) for(int mode=0;mode<4;mode++) {
        unsigned long m,q; int p=test(n,mode,&m,&q);
        printf("%lu %d %d %lu %lu %lu\n",n,mode,p,m,q,m+q);
        if(n<=limit && p!=(n>=2&&!flags[n])) { free(flags); return 1; }
    }
    for(n=0;n<=10000;n++) for(int mode=0;mode<4;mode++) {
        unsigned long m,q; if(test(n,mode,&m,&q)!=(n>=2&&!flags[n])) { free(flags); return 1; }
    }
    puts("All 4 variants agree with sieve for every n=0..10000.");
    uint32_t i=65536;
    printf("Defined uint32_t wrap: i=%" PRIu32 " i*i=%" PRIu32 " UINT32_MAX=%" PRIu32 "\n",i,(uint32_t)(i*i),UINT32_MAX);
    puts("Signed overflow is undefined and is not executed. Use i<=n/i for safe trial bounds.");
    free(flags); return 0;
}''','0\n1\n2\n3\n4\n25\n97\n100\n7919\n1000003\n')

def q6():
    put('Q6','loan.c',r'''
#include <stdio.h>
#include <math.h>
static void simulate(double principal,double rate,double payment,unsigned cap,int detail) {
    printf("loan P=%.2f r=%.6f E=%.2f cap=%u\n",principal,rate,payment,cap);
    if(!isfinite(principal)||!isfinite(rate)||!isfinite(payment)||principal<0||rate<0||payment<=0||cap==0) { puts("INVALID INPUT"); return; }
    if(principal==0) { puts("ALREADY REPAID months=0 interest=0"); return; }
    if(payment<=principal*rate) { puts("NON AMORTIZING: repayment does not exceed first-month interest"); return; }
    double b=principal,total_interest=0,total_paid=0;
    unsigned month=0;
    if(detail) puts("month opening interest payment closing");
    while(b>0.0) {
        if(month==cap) { puts("SAFETY LIMIT: unpaid balance remains; review repayment terms"); break; }
        double interest=b*rate, due=b+interest;
        if(!isfinite(due)) { puts("NUMERIC RANGE ERROR"); break; }
        double paid=due<payment ? due : payment;
        double next=due-paid;
        ++month; total_interest+=interest; total_paid+=paid;
        if(detail) printf("%u %.8f %.8f %.8f %.8f\n",month,b,interest,paid,next);
        b=next;
    }
    double exact=rate==0 ? principal/payment : -log1p(-rate*principal/payment)/log1p(rate);
    printf("RESULT months=%u interest=%.8f paid=%.8f balance=%.8f formula=%.8f ceil=%.0f\n",month,total_interest,total_paid,b,exact,ceil(exact));
}
int main(void) {
    double p,r,e; unsigned cap; int detail;
    while(scanf("%lf%lf%lf%u%d",&p,&r,&e,&cap,&detail)==5) simulate(p,r,e,cap,detail);
    return 0;
}''','10000 .02 2000 360 1\n10000 .02 1000 360 0\n10000 .02 500 360 0\n10000 .02 250 360 0\n10000 .02 210 360 0\n10000 .02 201 360 0\n10000 .02 200.01 360 0\n10000 .02 200 360 0\n10000 .02 199 360 0\n10000 0 2000 360 0\n0 .02 2000 360 0\n-1 .02 2000 360 0\n')

def q7():
    put('Q7','redesign.c',r'''
#include <stdio.h>
#include <stdlib.h>
typedef struct { unsigned long mods,quotients; } Work;
static int original(unsigned long n,Work *w) {
    *w=(Work){0,0}; if(n<2) return 0;
    for(unsigned long i=2;;i++) {
        ++w->quotients; if(i>n/i) break;
        ++w->mods; if(n%i==0) return 0;
    }
    return 1;
}
static int revised(unsigned long n,Work *w) {
    *w=(Work){0,0}; if(n<2) return 0;
    if(n==2||n==3) return 1;
    ++w->mods; if(n%2==0) return 0;
    ++w->mods; if(n%3==0) return 0;
    for(unsigned long i=5;;i+=6) {
        ++w->quotients; if(i>n/i) break;
        ++w->mods; if(n%i==0) return 0;
        ++w->mods; if(n%(i+2)==0) return 0;
    }
    return 1;
}
int main(void) {
    puts("n prime old_mod new_mod old_quot new_quot old_total new_total reduction_percent");
    unsigned long n;
    while(scanf("%lu",&n)==1) {
        Work a,b; int x=original(n,&a),y=revised(n,&b);
        if(x!=y) return 1;
        unsigned long old=a.mods+a.quotients,new=b.mods+b.quotients;
        printf("%lu %d %lu %lu %lu %lu %lu %lu %.3f\n",n,x,a.mods,b.mods,a.quotients,b.quotients,old,new,old?100.0*(old-new)/(double)old:0.0);
    }
    const unsigned long limit=1000003;
    unsigned char *sieve=calloc(limit+1,1); if(!sieve) return 1;
    for(unsigned long p=2;p<=limit/p;p++) if(!sieve[p])
        for(unsigned long j=p*p;j<=limit;j+=p) sieve[j]=1;
    for(n=0;n<=limit;n++) { Work w; if(revised(n,&w)!=(n>=2&&!sieve[n])) { free(sieve); return 1; } }
    for(n=0;n<=10000;n++) { Work a,b; if(original(n,&a)!=revised(n,&b)) { free(sieve); return 1; } }
    puts("Validation: revised vs sieve 0..1000003 PASS; original vs revised 0..10000 PASS.");
    free(sieve); return 0;
}''','0\n1\n2\n3\n4\n9\n25\n49\n97\n100\n7919\n1000003\n')

if __name__=='__main__': globals()['q'+sys.argv[1]]()
