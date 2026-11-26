#include "../lab.h"
typedef struct { int score,campus,order; } Entry;
static Count comparisons;
static int descending(const void *x,const void *y) {
    ++comparisons; int a=((const Entry *)x)->score,b=((const Entry *)y)->score; return (b>a)-(b<a);
}
static Count merge(const Entry *a,int m,const Entry *b,int n,Entry *out,Count *moves) {
    int i=0,j=0,k=0;Count cmp=0; *moves=0;
    while(i<m && j<n) { ++cmp; out[k++]=a[i].score>=b[j].score?a[i++]:b[j++]; ++*moves; }
    while(i<m) { out[k++]=a[i++]; ++*moves; }
    while(j<n) { out[k++]=b[j++]; ++*moves; }
    return cmp;
}
static Count inplace(Entry *a,int m,int n,Count *moves) {
    int i=0,j=m,total=m+n;Count cmp=0;*moves=0;
    while(i<j && j<total) {
        ++cmp;
        if(a[i].score>=a[j].score) ++i;
        else { Entry t=a[j]; memmove(a+i+1,a+i,(size_t)(j-i)*sizeof *a); *moves+=(Count)(j-i); a[i]=t; ++*moves; ++i; ++j; }
    }
    return cmp;
}
static void print_entries(const char *name,const Entry *a,int n) {
    printf("EDGE %s:",name); for(int i=0;i<n;i++) printf(" %d%c%d",a[i].score,a[i].campus?'B':'A',a[i].order);putchar('\n');
}
static void edge(const char *name,const Entry *a,int m,const Entry *b,int n) {
    Entry out[20];Count moves;Count cmp=merge(a,m,b,n,out,&moves);print_entries(name,out,m+n);
    for(int i=1;i<m+n;i++) require(out[i-1].score>=out[i].score,"edge order");
    for(int i=1;i<m+n;i++) if(out[i-1].score==out[i].score) require(out[i-1].campus<=out[i].campus,"A before B on ties");
    printf("EDGE_WORK %s comparisons=%llu moves=%llu\n",name,cmp,moves);
}
int main(void) {
    const Entry a[]={{98,0,0},{91,0,1},{85,0,2},{72,0,3}},b[]={{95,1,0},{91,1,1},{80,1,2}};
    const Entry equalA[]={{91,0,0},{91,0,1}},equalB[]={{91,1,0},{91,1,1},{91,1,2}};
    edge("unequal",a,4,b,3);edge("empty_A",NULL,0,b,3);edge("empty_B",a,4,NULL,0);edge("both_empty",NULL,0,NULL,0);edge("equal",equalA,2,equalB,3);
    puts("BENCH m n method comparisons record_writes_known aux_record_bytes cpu_seconds");
    for(int n=1000;n<=10000;n*=10) {
        Entry *left=allocate((size_t)n,sizeof *left),*right=allocate((size_t)n,sizeof *right),*out=allocate((size_t)2*n,sizeof *out),*combined=allocate((size_t)2*n,sizeof *combined);
        for(int i=0;i<n;i++) { left[i]=(Entry){2*n-2*i,0,i};right[i]=(Entry){2*n-2*i-1,1,i}; }
        Count moves;clock_t start=clock();Count cmp=merge(left,n,right,n,out,&moves);double elapsed=seconds(start);
        printf("%d %d merge %llu %llu %zu %.9f\n",n,n,cmp,moves,(size_t)2*n*sizeof *out,elapsed);
        start=clock();memcpy(combined,left,(size_t)n*sizeof *left);memcpy(combined+n,right,(size_t)n*sizeof *right);comparisons=0;qsort(combined,(size_t)2*n,sizeof *combined,descending);elapsed=seconds(start);
        printf("%d %d concat_qsort %llu NA %zu %.9f\n",n,n,comparisons,(size_t)2*n*sizeof *combined,elapsed);
        for(int i=0;i<2*n;i++) require(combined[i].score==out[i].score,"qsort equals merge scores");
        memcpy(combined,left,(size_t)n*sizeof *left);memcpy(combined+n,right,(size_t)n*sizeof *right);
        start=clock();cmp=inplace(combined,n,n,&moves);elapsed=seconds(start);
        printf("%d %d inplace %llu %llu %zu %.9f\n",n,n,cmp,moves,sizeof(Entry),elapsed);
        for(int i=0;i<2*n;i++) require(combined[i].score==out[i].score,"in-place equals merge scores");
        free(left);free(right);free(out);free(combined);
    }
    printf("sizeof_entry=%zu clock_ticks_per_second=%ld; qsort internal moves/storage implementation-dependent\n",sizeof(Entry),(long)CLOCKS_PER_SEC);return 0;
}
