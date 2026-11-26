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
}
