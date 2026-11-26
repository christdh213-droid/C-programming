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
}
