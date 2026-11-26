#include "../lab.h"
#include <ctype.h>
enum { CAP=30 };
static Count compares,copies,pointer_compares;
static int cmp(const char *a,const char *b) { ++compares;return strcmp(a,b); }
static void copy_name(char *to,const char *from) { copies+=(Count)strlen(from)+1;strcpy(to,from); }
static void direct_sort(char a[][CAP],int n) {
    compares=0;copies=0;
    for(int i=1;i<n;i++) {
        char key[CAP];copy_name(key,a[i]);int j=i;
        while(j>0 && cmp(a[j-1],key)>0) { copy_name(a[j],a[j-1]);--j; }
        copy_name(a[j],key);
    }
}
static void index_sort(const char a[][CAP],int *index,int n,Count *moves) {
    compares=0;copies=0;*moves=0;
    for(int i=1;i<n;i++) { int key=index[i],j=i;while(j>0 && cmp(a[index[j-1]],a[key])>0) { index[j]=index[j-1];++*moves;--j; }index[j]=key;++*moves; }
}
static int pointer_compare(const void *x,const void *y) {
    ++pointer_compares;return strcmp(*(const char *const *)x,*(const char *const *)y);
}
static int insensitive(const char *a,const char *b) {
    while(*a && *b) { int x=tolower((unsigned char)*a++),y=tolower((unsigned char)*b++);if(x!=y) return (x>y)-(x<y); }
    return ((unsigned char)*a>(unsigned char)*b)-((unsigned char)*a<(unsigned char)*b);
}
static int ci_pointer_compare(const void *x,const void *y) { return insensitive(*(const char *const *)x,*(const char *const *)y); }
static int search(char a[][CAP],int n,const char *key,Count *steps) {
    int lo=0,hi=n-1;*steps=0;
    while(lo<=hi) { int mid=lo+(hi-lo)/2;++*steps;int c=strcmp(a[mid],key);if(!c) return mid;if(c<0) lo=mid+1;else hi=mid-1; }return -1;
}
int main(void) {
    char names[500][30];int n=0;
    while(n<500 && fgets(names[n],sizeof names[n],stdin)) {
        size_t len=strlen(names[n]);int truncated=0;
        if(len && names[n][len-1]=='\n') names[n][--len]='\0';
        else { int ch=getchar();if(ch!='\n' && ch!=EOF) { truncated=1;while((ch=getchar())!='\n' && ch!=EOF) {} } }
        printf("READ row=%d stored_length=%zu truncated=%d [%s]\n",n,len,truncated,names[n]);++n;
    }
    require(n>0,"directory input");direct_sort(names,n);
    printf("DIRECTORY count=%d strcmp_calls=%llu copied_characters_including_NUL=%llu\n",n,compares,copies);
    for(int i=0;i<n;i++) printf("SORTED %d [%s]\n",i,names[i]);
    for(int i=1;i<n;i++) if(strcmp(names[i-1],names[i])==0) printf("DUPLICATE [%s]\n",names[i]);
    Count steps;int pos=search(names,n,"Chris",&steps);printf("SEARCH present Chris index=%d strcmp_calls=%llu\n",pos,steps);require(pos>=0,"present search");
    pos=search(names,n,"ZZZ_missing",&steps);printf("SEARCH missing index=%d strcmp_calls=%llu\n",pos,steps);require(pos==-1,"missing search");
    char *view[500];for(int i=0;i<n;i++) view[i]=names[i];qsort(view,(size_t)n,sizeof *view,ci_pointer_compare);
    for(int i=0;i<n;i++) printf("CASE_INSENSITIVE %d [%s]\n",i,view[i]);
    for(int i=1;i<n;i++) if(insensitive(view[i-1],view[i])==0) printf("CI_DUPLICATE [%s] [%s]\n",view[i-1],view[i]);
    puts("BENCH n method strcmp_calls copied_chars index_writes view_bytes cpu_seconds");
    const int sizes[]={100,500,5000};
    for(int s=0;s<3;s++) {
        int count=sizes[s];char (*base)[CAP]=allocate((size_t)count,sizeof *base),(*data)[CAP]=allocate((size_t)count,sizeof *data);
        int *index=allocate((size_t)count,sizeof *index);char **list=allocate((size_t)count,sizeof *list);
        for(int i=0;i<count;i++) snprintf(base[i],CAP,"Resident%05d",i);
        uint32_t rng=987654321u;
        for(int i=count-1;i>0;i--) { int j=(int)(random32(&rng)%(unsigned)(i+1));char tmp[CAP];strcpy(tmp,base[i]);strcpy(base[i],base[j]);strcpy(base[j],tmp); }
        memcpy(data,base,(size_t)count*sizeof *data);clock_t start=clock();direct_sort(data,count);double elapsed=seconds(start);
        printf("%d direct_insertion %llu %llu 0 0 %.9f\n",count,compares,copies,elapsed);
        for(int i=0;i<count;i++) index[i]=i;
        Count moves;start=clock();index_sort(base,index,count,&moves);elapsed=seconds(start);
        printf("%d index_insertion %llu %llu %llu %zu %.9f\n",count,compares,copies,moves,(size_t)count*sizeof *index,elapsed);
        for(int i=0;i<count;i++) list[i]=base[i];
        pointer_compares=0;start=clock();qsort(list,(size_t)count,sizeof *list,pointer_compare);elapsed=seconds(start);
        printf("%d pointer_qsort %llu 0 NA %zu %.9f\n",count,pointer_compares,(size_t)count*sizeof *list,elapsed);
        for(int i=0;i<count;i++) require(strcmp(data[i],base[index[i]])==0 && strcmp(data[i],list[i])==0,"same sorted view");
        Count present,missing;search(data,count,"Resident00000",&present);search(data,count,"ZZZ_missing",&missing);
        printf("BENCH_SEARCH n=%d first_present=%llu missing=%llu\n",count,present,missing);
        free(base);free(data);free(index);free(list);
    }
    printf("sizeof_pointer=%zu sizeof_index=%zu clock_ticks_per_second=%ld\n",sizeof(char *),sizeof(int),(long)CLOCKS_PER_SEC);return 0;
}
