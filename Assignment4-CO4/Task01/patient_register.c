#include "../../engineering_support/lab.h"
#include <ctype.h>
typedef struct { int systolic,diastolic; } BloodPressure;
typedef struct { char name[40];int age;char phone[11];BloodPressure bp;Date visit; } Patient;
typedef struct { char name[100][40];int age[100];char phone[100][11];BloodPressure bp[100];Date visit[100]; } Parallel;
static int addPatient(Patient *list,size_t *count,size_t capacity,const Patient *patient) {
    if(*count>=capacity || patient->age<0 || patient->age>120 || strlen(patient->phone)!=10 || !valid_date(patient->visit) || patient->bp.diastolic<=0 || patient->bp.systolic<=patient->bp.diastolic) return 0;
    for(int i=0;i<10;i++) if(!isdigit((unsigned char)patient->phone[i])) return 0;
    list[(*count)++]=*patient;return 1;
}
static Count sort_by_age(Patient *list,size_t n) {
    Count swaps=0;
    for(size_t i=0;i<n;i++) { size_t min=i;for(size_t j=i+1;j<n;j++) if(list[j].age<list[min].age) min=j;if(i!=min) { Patient t=list[i];list[i]=list[min];list[min]=t;++swaps; } }
    return swaps;
}
int main(void) {
    Patient list[100],small[2],value;size_t count=0,tiny=0;memset(&value,0,sizeof value);
    while(scanf("%39s%d%10s%d%d%d%d%d",value.name,&value.age,value.phone,&value.bp.systolic,&value.bp.diastolic,&value.visit.day,&value.visit.month,&value.visit.year)==8) {
        require(addPatient(list,&count,100,&value),"valid patient input");
        size_t before=tiny;int accepted=addPatient(small,&tiny,2,&value);printf("capacity2 add=%s before=%zu after=%zu\n",accepted?"accepted":"rejected",before,tiny);
        if(!accepted) require(tiny==before,"capacity rejection preserves count");
    }
    Count swaps=sort_by_age(list,count);
    for(size_t i=0;i<count;i++) printf("PATIENT %s age=%d phone=%s bp=%d/%d date=%02d/%02d/%04d\n",list[i].name,list[i].age,list[i].phone,list[i].bp.systolic,list[i].bp.diastolic,list[i].visit.day,list[i].visit.month,list[i].visit.year);
    size_t fields=40+sizeof(int)+11+sizeof(BloodPressure)+sizeof(Date);
    printf("LAYOUT Patient=%zu align=%zu fields=%zu padding=%zu Parallel100=%zu AoS100=%zu\n",sizeof(Patient),_Alignof(Patient),fields,sizeof(Patient)-fields,sizeof(Parallel),sizeof(Patient)*100);
    printf("OFFSETS name=%zu age=%zu phone=%zu bp=%zu visit=%zu\n",offsetof(Patient,name),offsetof(Patient,age),offsetof(Patient,phone),offsetof(Patient,bp),offsetof(Patient,visit));
    printf("SWAPS %llu AoS_source_bytes=%llu equivalent_SoA_source_bytes=%llu (three assignments per swapped field)\n",swaps,swaps*3*sizeof(Patient),swaps*3*fields);
    return 0;
}
