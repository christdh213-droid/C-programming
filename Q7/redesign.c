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
}
