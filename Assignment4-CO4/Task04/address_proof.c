#include <stdio.h>
struct account { int number;float balance; };
static void addInterest(struct account a,float rate) {
    printf("VALUE address=%p number=%d before=%.2f",(void *)&a,a.number,a.balance);
    a.balance+=a.balance*rate/100;printf(" local_after=%.2f\n",a.balance);
}
int main(void) {
    struct account list[3]={{101,5000},{102,12000},{103,800}};
    for(int i=0;i<3;i++) { printf("CALLER address=%p number=%d\n",(void *)&list[i],list[i].number);addInterest(list[i],4);printf("CALLER unchanged=%.2f\n",list[i].balance); }
    return 0;
}
