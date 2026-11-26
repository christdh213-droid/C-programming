#include "../../engineering_support/lab.h"
struct account { int number;float balance; };
static void addInterest(struct account *a,float rate) { a->balance+=a->balance*rate/100; }
static struct account returned_interest(struct account a,float rate) { a.balance+=a.balance*rate/100;return a; }
static volatile double checksum;
int main(void) {
    struct account list[3]={{101,5000},{102,12000},{103,800}};
    for(int i=0;i<3;i++) { addInterest(&list[i],4);printf("UPDATED %d %.2f\n",list[i].number,list[i].balance); }
    printf("SIZE account=%zu pointer=%zu conceptual_value_copy_bytes_per_call=%zu\n",sizeof(struct account),sizeof(struct account *),2*sizeof(struct account));
    const int repetitions=1000000;
    for(int mode=0;mode<2;mode++) {
        clock_t start=clock();double sum=0;
        for(int i=0;i<repetitions;i++) { struct account a={101,5000};if(mode==0) addInterest(&a,4);else a=returned_interest(a,4);sum+=a.balance; }
        checksum=sum;printf("BENCH %s repetitions=%d cpu_seconds=%.9f checksum=%.2f\n",mode==0?"pointer":"return_value",repetitions,elapsed(start),sum);
    }
    return checksum>0?0:1;
}
