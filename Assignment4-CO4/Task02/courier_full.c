#include "../../engineering_support/lab.h"
typedef struct { char name[32],city[24];int pincode; } Address;
typedef enum { NORMAL,EXPRESS } Service;
typedef struct { int id;double weight;Date booked;Address from,to;Service service;long long charge_paise; } Parcel;
typedef struct { int id;double weight;int day,month,year;char sender_name[32],sender_city[24];int sender_pin;char receiver_name[32],receiver_city[24];int receiver_pin;Service service;long long charge_paise; } FlatParcel;
static void sort_weight(Parcel *list,size_t n) {
    for(size_t i=0;i<n;i++) { size_t min=i;for(size_t j=i+1;j<n;j++) if(list[j].weight<list[min].weight) min=j;if(min!=i) { Parcel t=list[i];list[i]=list[min];list[min]=t; } }
}
static void print_parcel(const Parcel *p) {
    printf("PARCEL %d %.1f kg %s->%s-%d %02d/%02d/%04d %s charge=%lld.%02lld\n",p->id,p->weight,p->from.city,p->to.city,p->to.pincode,p->booked.day,p->booked.month,p->booked.year,p->service==NORMAL?"normal":"express",p->charge_paise/100,p->charge_paise%100);
}
int main(void) {
    Parcel list[100];int n;require(scanf("%d",&n)==1 && n>=3 && n<=100,"booking count");
    for(int i=0;i<n;i++) {
        Parcel *p=&list[i];int type;
        require(scanf("%d%lf%31s%23s%d%31s%23s%d%d%lld%d%d%d",&p->id,&p->weight,p->from.name,p->from.city,&p->from.pincode,p->to.name,p->to.city,&p->to.pincode,&type,&p->charge_paise,&p->booked.day,&p->booked.month,&p->booked.year)==13,"booking fields");
        require(p->weight>0 && type>=0 && type<=1 && valid_date(p->booked),"booking validation");p->service=(Service)type;
    }
    Parcel *ptr=list;printf("THIRD_PIN array=%d pointer=%d\n",list[2].to.pincode,(ptr+2)->to.pincode);
    sort_weight(list,(size_t)n);for(int i=0;i<n;i++) print_parcel(&list[i]);
    char city[24];require(scanf("%23s",city)==1,"city filter");printf("FILTER %s\n",city);
    for(int i=0;i<n;i++) if(strcmp(list[i].to.city,city)==0) print_parcel(&list[i]);
    printf("SIZE nested=%zu flat=%zu Address=%zu Date=%zu\n",sizeof(Parcel),sizeof(FlatParcel),sizeof(Address),sizeof(Date));return 0;
}
