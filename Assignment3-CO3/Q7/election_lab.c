#include "../lab.h"
typedef struct { int candidate;Count votes; } Result;
static Count sort_calls;
static volatile Count sink;
static int descending(const void *a,const void *b) {
    const Result *x=a,*y=b;
    if(x->votes!=y->votes) return x->votes<y->votes?1:-1;
    return (x->candidate>y->candidate)-(x->candidate<y->candidate);
}
static Count count_once(const int *votes,size_t v,int c,Count *counts) {
    memset(counts,0,(size_t)c*sizeof *counts);Count invalid=0;
    for(size_t i=0;i<v;i++) { int id=votes[i];if(id<=0||id>c) ++invalid;else ++counts[id-1]; }return invalid;
}
static Count name_search(const int *votes,size_t v,int c,Count *counts,Count *comparisons) {
    char (*names)[20]=allocate((size_t)c,sizeof *names);for(int i=0;i<c;i++) snprintf(names[i],20,"Candidate%04d",i+1);
    memset(counts,0,(size_t)c*sizeof *counts);Count invalid=0;*comparisons=0;
    for(size_t i=0;i<v;i++) {
        char key[20];snprintf(key,sizeof key,"Candidate%04d",votes[i]);int found=-1;
        for(int j=0;j<c;j++) { ++*comparisons;if(strcmp(key,names[j])==0) { found=j;break; } }
        if(found<0) ++invalid;else ++counts[found];
    }
    free(names);return invalid;
}
static int int_compare(const void *a,const void *b) { ++sort_calls;int x=*(const int *)a,y=*(const int *)b;return (x>y)-(x<y); }
static Count sort_count(const int *votes,size_t v,int c,Count *counts) {
    int *copy=allocate(v,sizeof *copy);memcpy(copy,votes,v*sizeof *copy);sort_calls=0;qsort(copy,v,sizeof *copy,int_compare);
    memset(counts,0,(size_t)c*sizeof *counts);Count invalid=0;
    for(size_t i=0;i<v;) { size_t end=i+1;while(end<v && copy[end]==copy[i]) ++end;Count run=(Count)(end-i);if(copy[i]<=0||copy[i]>c) invalid+=run;else counts[copy[i]-1]+=run;i=end; }
    free(copy);return invalid;
}
static void results(const char *label,int c,const Count *counts,Count invalid,size_t total) {
    Result *r=allocate((size_t)c,sizeof *r);Count valid=0;
    for(int i=0;i<c;i++) { r[i]=(Result){i+1,counts[i]};valid+=counts[i]; }
    require(valid+invalid==total,"all votes accounted for");qsort(r,(size_t)c,sizeof *r,descending);
    printf("RESULT %s candidates=%d valid=%llu invalid=%llu\n",label,c,valid,invalid);
    for(int i=0;i<c;i++) printf("RANK %d candidate=%d votes=%llu\n",i+1,r[i].candidate,r[i].votes);
    if(valid==0) puts("NO WINNER: no valid votes");
    else { int tied=0;for(int i=0;i<c;i++) if(r[i].votes==r[0].votes) ++tied;printf("WINNERS count=%d tied=%d:",tied,tied>1);for(int i=0;i<tied;i++) printf(" %d",r[i].candidate);putchar('\n'); }
    free(r);
}
int main(void) {
    int c;size_t v;require(scanf("%d%zu",&c,&v)==2 && c>0&&c<=12&&v<=5000,"c<=12, votes<=5000");
    int *votes=allocate(v,sizeof *votes);for(size_t i=0;i<v;i++) require(scanf("%d",&votes[i])==1,"vote input");
    Count counts[12];Count invalid=count_once(votes,v,c,counts);results("hand",c,counts,invalid,v);free(votes);
    int none[]={0,-1,4};invalid=count_once(none,3,3,counts);results("all_invalid",3,counts,invalid,3);
    const size_t sizes[]={5000,500000};
    puts("BENCH votes candidates method vote_visits string_or_sort_comparisons invalid cpu_seconds");
    for(int dimension=0;dimension<2;dimension++) for(int s=0;s<2;s++) {
        int candidates=dimension==0?12:500;size_t size=sizes[s];
        int *sample=allocate(size,sizeof *sample);Count *expected=allocate((size_t)candidates,sizeof *expected),*work=allocate((size_t)candidates,sizeof *work);
        uint32_t rng=13579u;for(size_t i=0;i<size;i++) sample[i]=(int)(random32(&rng)%(unsigned)(candidates+3))-1;
        clock_t start=clock();Count bad=count_once(sample,size,candidates,expected);double elapsed=seconds(start);
        printf("%zu %d count_array %zu 0 %llu %.9f\n",size,candidates,size,bad,elapsed);
        Count comparisons;start=clock();Count bad2=name_search(sample,size,candidates,work,&comparisons);elapsed=seconds(start);
        require(bad==bad2 && memcmp(expected,work,(size_t)candidates*sizeof *work)==0,"name search agreement");
        printf("%zu %d name_search %zu %llu %llu %.9f\n",size,candidates,size,comparisons,bad2,elapsed);
        start=clock();bad2=sort_count(sample,size,candidates,work);elapsed=seconds(start);
        require(bad==bad2 && memcmp(expected,work,(size_t)candidates*sizeof *work)==0,"sort count agreement");
        printf("%zu %d sort_count %zu %llu %llu %.9f\n",size,candidates,size,sort_calls,bad2,elapsed);
        if(candidates==12 && size==5000) results("5000_sample",candidates,expected,bad,size);
        sink+=bad+expected[0];free(sample);free(expected);free(work);
    }
    printf("clock_ticks_per_second=%ld sink=%llu\n",(long)CLOCKS_PER_SEC,sink);return 0;
}
