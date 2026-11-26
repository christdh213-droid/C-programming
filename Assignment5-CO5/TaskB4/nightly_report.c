#include "../donor_model.h"
typedef struct { DonorRecord *data;size_t size,capacity,growths; } DonorList;
typedef struct { size_t count,hospitals[25];int youngest_id,youngest_age; } Summary;
static int append(DonorList *list,DonorRecord d,int fail) {
    if(list->size==list->capacity) {
        if(list->capacity>SIZE_MAX/2/sizeof d) return 0;
        size_t cap=list->capacity?2*list->capacity:2;DonorRecord *p=fail?NULL:realloc(list->data,cap*sizeof *p);
        if(!p) return 0;
        list->data=p;list->capacity=cap;list->growths++;
    }
    list->data[list->size++]=d;return 1;
}
static void summarize(Summary *s,const DonorRecord *d,Date today) {
    require(d->hospital>=1 && d->hospital<=25 && valid_date(d->last),"record validity");
    int last=date_serial(d->last),now=date_serial(today);
    if(d->age>=18 && d->age<=65 && last<=now && last+90<=now+7) {
        s->count++;s->hospitals[d->hospital-1]++;
        if(s->youngest_id<0||d->age<s->youngest_age||(d->age==s->youngest_age && d->id<s->youngest_id)) { s->youngest_id=d->id;s->youngest_age=d->age; }
    }
}
int main(int argc,char **argv) {
    int stream=argc==2 && !strcmp(argv[1],"stream");if(argc>2||(argc==2 && !stream)) return 2;
    DonorList list={0};Summary s={.youngest_id=-1};Date today={26,11,2026};clock_t start=clock();size_t count=0;
    FILE *fp=fopen("TaskB3/data/donors_100000.bin","rb");if(!fp) { perror("donor file");return 1; }
    if(stream) {
        DonorRecord batch[256];size_t n;
        while((n=fread(batch,sizeof *batch,256,fp))>0) { for(size_t i=0;i<n;i++) summarize(&s,batch+i,today);count+=n; }
    } else {
        DonorRecord d;while(fread(&d,sizeof d,1,fp)==1) {
            if(!append(&list,d,0)) { fputs("Allocation failure\n",stderr);fclose(fp);free(list.data);return 1; }
        }
        count=list.size;for(size_t i=0;i<list.size;i++) summarize(&s,list.data+i,today);
    }
    int ok=!ferror(fp);require(fclose(fp)==0 && ok,"input close/read");require(count==100000,"district donor count");
    printf("NIGHTLY mode=%s date=26/11/2026 records=%zu hospitals=25 eligible=%zu youngest_id=%d\n",stream?"stream":"memory",count,s.count,s.youngest_id);
    printf("MEASURE clock_seconds=%.9f peak_working_set_bytes=%zu record_bytes=%zu capacity=%zu logical_input_buffer_bytes=%zu realloc_calls=%zu\n",elapsed(start),peak_ram_bytes(),sizeof(DonorRecord),list.capacity,stream?256*sizeof(DonorRecord):list.capacity*sizeof(DonorRecord),list.growths);
    for(size_t i=0;i<25;i++) printf("HOSPITAL %zu eligible=%zu\n",i+1,s.hospitals[i]);
    free(list.data);list.data=NULL;list.size=list.capacity=0;puts("CLEANUP donor allocation freed; owner reset (source instrumentation, not sanitizer proof)");
    DonorList probe={0};require(append(&probe,generated_donor(0),0) && append(&probe,generated_donor(1),0),"failure setup");
    DonorRecord *old=probe.data;size_t cap=probe.capacity;require(!append(&probe,generated_donor(2),1) && probe.data==old && probe.capacity==cap && probe.size==2,"injected failure preserves owner");
    require(probe.data[0].id==7001 && probe.data[1].id==7002,"preserved content");free(probe.data);puts("INJECTED realloc failure: pointer, capacity, size and content unchanged; freed once");return 0;
}
