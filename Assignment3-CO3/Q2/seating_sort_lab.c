#include "../lab.h"
typedef struct { Count comparisons,swaps,shifts,writes; } Work;
static void show(const char *alg,int pass,const int *a,int n) {
    printf("TRACE %s pass=%d:",alg,pass); for(int i=0;i<n;i++) printf(" %d",a[i]); putchar('\n');
}
static Work bubble(int *a,int n,int trace) {
    Work w={0,0,0,0};
    for(int end=n-1,pass=1;end>0;end--,pass++) {
        int changed=0;
        for(int j=0;j<end;j++) { ++w.comparisons; if(a[j]>a[j+1]) { int t=a[j]; a[j]=a[j+1]; a[j+1]=t; ++w.swaps; w.writes+=2; changed=1; } }
        if(trace) show("bubble",pass,a,n);
        if(!changed) break;
    }
    return w;
}
static Work selection(int *a,int n,int trace) {
    Work w={0,0,0,0};
    for(int i=0;i<n-1;i++) {
        int min=i;
        for(int j=i+1;j<n;j++) { ++w.comparisons; if(a[j]<a[min]) min=j; }
        if(min!=i) { int t=a[i]; a[i]=a[min]; a[min]=t; ++w.swaps; w.writes+=2; }
        if(trace) show("selection",i+1,a,n);
    }
    return w;
}
static Work insertion(int *a,int n,int trace) {
    Work w={0,0,0,0};
    for(int i=1;i<n;i++) {
        int key=a[i],j=i;
        while(j>0) { ++w.comparisons; if(a[j-1]<=key) break; a[j]=a[j-1]; ++w.shifts; ++w.writes; --j; }
        a[j]=key; ++w.writes;
        if(trace) show("insertion",i,a,n);
    }
    return w;
}
static Work counting(int *a,int n,int trace) {
    (void)trace; Work w={0,0,0,0}; if(!n) return w;
    int max=a[0]; for(int i=1;i<n;i++) { ++w.comparisons; if(a[i]>max) max=a[i]; }
    unsigned *freq=allocate((size_t)max+1,sizeof *freq);
    for(int i=0;i<n;i++) { ++freq[a[i]]; ++w.writes; }
    int p=0; for(int value=0;value<=max;value++) while(freq[value]--) { a[p++]=value; ++w.writes; }
    free(freq); return w;
}
int main(void) {
    int trial[6]; for(int i=0;i<6;i++) require(scanf("%d",&trial[i])==1,"six trace inputs");
    Work (*sorts[])(int *,int,int)={bubble,selection,insertion,counting};
    const char *names[]={"bubble","selection","insertion","counting"};
    for(int alg=0;alg<3;alg++) { int a[6]; memcpy(a,trial,sizeof a); show(names[alg],0,a,6); Work w=sorts[alg](a,6,1); printf("TRACE_WORK %s comparisons=%llu swaps=%llu shifts=%llu\n",names[alg],w.comparisons,w.swaps,w.shifts); }
    puts("BENCH n order method comparisons swaps shifts writes range_k cpu_seconds");
    for(int n=100;n<=10000;n*=10) for(int order=0;order<4;order++) {
        int *base=allocate((size_t)n,sizeof *base),*a=allocate((size_t)n,sizeof *a);
        for(int i=0;i<n;i++) base[i]=order==2?n-1-i:i;
        uint32_t rng=123456789u;
        if(order==1) for(int i=0;i<10 && i<n-1;i++) { int j=(int)(random32(&rng)%(unsigned)(n-1)); int t=base[j];base[j]=base[j+1];base[j+1]=t; }
        if(order==3) for(int i=n-1;i>0;i--) { int j=(int)(random32(&rng)%(unsigned)(i+1)); int t=base[i];base[i]=base[j];base[j]=t; }
        const char *orders[]={"sorted","nearly","reverse","random"};
        for(int alg=0;alg<4;alg++) {
            memcpy(a,base,(size_t)n*sizeof *a); clock_t start=clock(); Work w=sorts[alg](a,n,0); double elapsed=seconds(start);
            for(int i=0;i<n;i++) require(a[i]==i,"permutation sorted");
            printf("%d %s %s %llu %llu %llu %llu %d %.9f\n",n,orders[order],names[alg],w.comparisons,w.swaps,w.shifts,w.writes,n,elapsed);
        }
        free(base);free(a);
    }
    int base[1020],a[1020];
    for(int i=0;i<1000;i++) base[i]=2*i;
    for(int i=0;i<20;i++) base[1000+i]=i*100+1;
    for(int alg=0;alg<4;alg++) {
        memcpy(a,base,sizeof a); clock_t start=clock(); Work w=sorts[alg](a,1020,0);double elapsed=seconds(start);
        for(int i=1;i<1020;i++) require(a[i-1]<=a[i],"late registrations sorted");
        printf("1020 late20 %s %llu %llu %llu %llu 1999 %.9f\n",names[alg],w.comparisons,w.swaps,w.shifts,w.writes,elapsed);
    }
    printf("clock_ticks_per_second=%ld\n",(long)CLOCKS_PER_SEC); return 0;
}
