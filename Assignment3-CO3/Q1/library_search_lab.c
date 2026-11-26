#include "../lab.h"
static volatile Count sink;
static int linear(const int *a,int n,int key,Count *p) {
    *p=0; for(int i=0;i<n;i++) { ++*p; if(a[i]==key) return i; } return -1;
}
static int binary(const int *a,int n,int key,Count *p) {
    *p=0; int lo=0,hi=n-1;
    while(lo<=hi) { int mid=lo+(hi-lo)/2; ++*p; if(a[mid]==key) return mid; if(a[mid]<key) lo=mid+1; else hi=mid-1; }
    return -1;
}
static int interpolation(const int *a,int n,int key,Count *p) {
    *p=0; int lo=0,hi=n-1;
    while(lo<=hi && key>=a[lo] && key<=a[hi]) {
        ++*p;
        if(a[lo]==a[hi]) return a[lo]==key ? lo:-1;
        int pos=lo+(int)((long long)(key-a[lo])*(hi-lo)/(a[hi]-a[lo]));
        if(a[pos]==key) return pos;
        if(a[pos]<key) lo=pos+1; else hi=pos-1;
    }
    return -1;
}
static int hash_search(const int *table,int n,int key,Count *p) {
    *p=0; unsigned pos=(unsigned)key%(unsigned)n;
    for(int i=0;i<n;i++) { ++*p; if(table[pos]==0) return -1; if(table[pos]==key) return (int)pos; pos=(pos+1)%(unsigned)n; }
    return -1;
}
typedef int (*Search)(const int *,int,int,Count *);
int main(void) {
    puts("TRIAL key linear_unsorted binary_sorted");
    const int unsorted[]={1305,1021,1533,1048,1460,1103,1402,1190,1377,1222};
    const int sorted[]={1021,1048,1103,1190,1222,1305,1377,1402,1460,1533};
    const int keys[]={1305,1103,1222,1400};
    for(int k=0;k<4;k++) { Count a,b; linear(unsorted,10,keys[k],&a); binary(sorted,10,keys[k],&b); printf("%d %llu %llu\n",keys[k],a,b); }
    puts("BENCH n query method found probes reps cpu_seconds");
    Search funcs[]={linear,binary,hash_search,interpolation};
    const char *names[]={"linear","binary","hash","interpolation"};
    for(int n=1000;n<=100000;n*=10) {
        int *a=allocate((size_t)n,sizeof *a), cap=2*n+1;
        int *table=allocate((size_t)cap,sizeof *table);
        for(int i=0;i<n;i++) { a[i]=1000+2*i; unsigned pos=(unsigned)a[i]%(unsigned)cap; while(table[pos]) pos=(pos+1)%(unsigned)cap; table[pos]=a[i]; }
        int queries[]={a[0],a[n/2],a[n-1],a[n/2]+1};
        const char *labels[]={"first","middle","last","missing"};
        for(int k=0;k<4;k++) for(int method=0;method<4;method++) {
            Count probes; int found=funcs[method](method==2?table:a,method==2?cap:n,queries[k],&probes);
            require((found>=0)==(k!=3),"search truth");
            unsigned reps=method==0?100u:100000u; volatile int key=queries[k];
            clock_t begin=clock();
            for(unsigned j=0;j<reps;j++) { Count c; int pos=funcs[method](method==2?table:a,method==2?cap:n,key,&c); sink+=(Count)(pos+1)+c; }
            double elapsed=seconds(begin);
            printf("%d %s %s %d %llu %u %.9f\n",n,labels[k],names[method],found>=0,probes,reps,elapsed);
        }
        /* Exact average over all successful keys, not one middle-key proxy. */
        Count sum=0; for(int i=0;i<n;i++) { Count c; binary(a,n,a[i],&c); sum+=c; }
        printf("AVERAGE n=%d linear=%.6f binary=%.6f binary_total=%llu\n",n,(n+1)/2.0,(double)sum/n,sum);
        free(a); free(table);
    }
    /* Deliberately colliding positive keys demonstrate linear probing worst cases. */
    int table[11]={0}; for(int i=1;i<=5;i++) { unsigned pos=(unsigned)(11*i)%11u; while(table[pos]) pos=(pos+1)%11u; table[pos]=11*i; }
    Count collision; hash_search(table,11,55,&collision); printf("COLLISION fifth key probes=%llu\n",collision);
    hash_search(table,11,66,&collision); printf("COLLISION missing key probes=%llu\n",collision);
    printf("clock_ticks_per_second=%ld sink=%llu\n",(long)CLOCKS_PER_SEC,sink);
    return 0;
}
