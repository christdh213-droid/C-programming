#include "../../engineering_support/lab.h"
static volatile unsigned long long calls;
static unsigned long long linear(unsigned n) { calls++;if(!n) return 1;return linear(n-1); }
int main(int argc,char **argv) {
#ifdef _WIN32
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
#endif
    if(argc!=3) return 2;
    char *end;errno=0;unsigned long n=strtoul(argv[2],&end,10);if(errno||*end||n>10000000) return 2;
    unsigned long long result=1;
    if(strcmp(argv[1],"linear")==0) result=linear((unsigned)n);
    else if(strcmp(argv[1],"iterative")==0) { for(unsigned long i=0;i<=n;i++) calls++; }
    else return 2;
    printf("STACK mode=%s n=%lu result=%llu calls=%llu\n",argv[1],n,result,calls);return 0;
}
