#include "../../engineering_support/lab.h"
#define main supplied_main
#include "complete_the_code.c"
#undef main
typedef struct { float celsius;int percent;char status[8]; } AllValues;
typedef struct { enum kind type;AllValues value; } AllTagged;
typedef struct { enum kind type;void *value; } Dynamic;
static volatile double checksum;
int main(void) {
    struct reading r={TEMPERATURE,{.celsius=31.5f}};uint32_t bits=0;
    require(sizeof(float)==sizeof bits,"binary32-sized float");memcpy(&bits,&r.value.celsius,sizeof bits);
    printf("LAYOUT full_payload=%zu full_with_tag=%zu union=%zu tagged=%zu align_union=%zu align_tagged=%zu value_offset=%zu\n",sizeof(AllValues),sizeof(AllTagged),sizeof r.value,sizeof r,_Alignof(r.value),_Alignof(struct reading),offsetof(struct reading,value));
    printf("MISUSE celsius=%.1f inactive_percent=%d memcpy_bits=0x%08lx\n",r.value.celsius,r.value.percent,(unsigned long)bits);
    puts("Inactive-member interpretation is target-specific; production dispatch must use the tag.");
    const size_t n=30000,k=n/3;struct reading *tagged=allocate(n,sizeof *tagged);
    float *temperatures=allocate(k,sizeof *temperatures);int *humidities=allocate(k,sizeof *humidities);char (*statuses)[8]=allocate(k,sizeof *statuses);
    Dynamic *dynamic=allocate(n,sizeof *dynamic);clock_t start=clock();
    for(size_t i=0;i<n;i++) { tagged[i].type=(enum kind)(i%3);switch(tagged[i].type) { case TEMPERATURE:tagged[i].value.celsius=31.5f;break;case HUMIDITY:tagged[i].value.percent=68;break;case STATUS:strcpy(tagged[i].value.status,"OK");break; } }
    double build_tagged=elapsed(start);start=clock();double sum=0;
    for(size_t i=0;i<n;i++) switch(tagged[i].type) { case TEMPERATURE:sum+=tagged[i].value.celsius;break;case HUMIDITY:sum+=tagged[i].value.percent;break;case STATUS:sum+=(unsigned char)tagged[i].value.status[0];break; }
    double read_tagged=elapsed(start);checksum=sum;
    printf("BENCH tagged n=%zu known_bytes=%zu build_cpu=%.9f read_cpu=%.9f checksum=%.1f\n",n,n*sizeof *tagged,build_tagged,read_tagged,sum);
    start=clock();for(size_t i=0;i<k;i++) { temperatures[i]=31.5f;humidities[i]=68;strcpy(statuses[i],"OK"); }double build_arrays=elapsed(start);
    start=clock();sum=0;for(size_t i=0;i<k;i++) sum+=temperatures[i]+humidities[i]+(unsigned char)statuses[i][0];double read_arrays=elapsed(start);
    printf("BENCH separate_type_arrays n=%zu known_bytes=%zu build_cpu=%.9f read_cpu=%.9f checksum=%.1f\n",n,k*(sizeof(float)+sizeof(int)+8),build_arrays,read_arrays,sum);require(sum==checksum,"array checksum");
    start=clock();size_t payload_bytes=0;
    for(size_t i=0;i<n;i++) {
        dynamic[i].type=(enum kind)(i%3);size_t bytes=i%3==2?8:4;dynamic[i].value=allocate(1,bytes);payload_bytes+=bytes;
        switch(dynamic[i].type) { case TEMPERATURE:*(float *)dynamic[i].value=31.5f;break;case HUMIDITY:*(int *)dynamic[i].value=68;break;case STATUS:strcpy(dynamic[i].value,"OK");break; }
    }
    double build_dynamic=elapsed(start);start=clock();sum=0;
    for(size_t i=0;i<n;i++) switch(dynamic[i].type) { case TEMPERATURE:sum+=*(float *)dynamic[i].value;break;case HUMIDITY:sum+=*(int *)dynamic[i].value;break;case STATUS:sum+=(unsigned char)*(char *)dynamic[i].value;break; }
    double read_dynamic=elapsed(start);
    printf("BENCH malloc_void_pointer n=%zu known_bytes=%zu build_cpu=%.9f read_cpu=%.9f checksum=%.1f\n",n,n*sizeof *dynamic+payload_bytes,build_dynamic,read_dynamic,sum);require(sum==checksum,"dynamic checksum");
    printf("DYNAMIC descriptor=%zu payload_bytes=%zu allocations=%zu allocator_overhead=not_measured\n",sizeof(Dynamic),payload_bytes,n);
    puts("Separate compact arrays group packets by type; preserving arbitrary arrival order requires additional tags/indices.");
    for(size_t i=0;i<n;i++) free(dynamic[i].value);
    free(dynamic);free(temperatures);free(humidities);free(statuses);free(tagged);return 0;
}
