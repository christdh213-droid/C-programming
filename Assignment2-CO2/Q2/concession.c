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
}
