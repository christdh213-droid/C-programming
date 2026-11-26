#include "../../engineering_support/lab.h"
typedef struct { int hour,minute; } Time;
typedef enum { PACKAGED,COOKED,COMBO } Kind;
typedef struct { int id;char name[24];long long price_paise;int stock;Kind kind;union { Date expiry;Time prepared;struct { int count,ids[3]; } combo; } detail; } Item;
typedef struct { int id;long long quantity,revenue_paise; } Bill;
typedef struct { Item items[10];size_t count;Bill bills[10];Date today; } Canteen;
static int find(const Canteen *c,int id) { for(size_t i=0;i<c->count;i++) if(c->items[i].id==id) return (int)i;return -1; }
static void expiry_warning(const Canteen *c) {
    for(size_t i=0;i<c->count;i++) if(c->items[i].kind==PACKAGED) { int days=date_serial(c->items[i].detail.expiry)-date_serial(c->today);if(days<=2) printf("EXPIRY %s days=%d %s\n",c->items[i].name,days,days<0?"EXPIRED":"within two days"); }
}
static int sale(Canteen *c,int id,int quantity) {
    int index=find(c,id);if(index<0 || quantity<=0) { puts("REJECT invalid item or quantity");return 0; }
    Item *item=&c->items[index];long long need[10]={0};
    if(item->kind!=COMBO) need[index]=quantity;
    else {
        if(item->detail.combo.count<1 || item->detail.combo.count>3) { puts("REJECT invalid combo");return 0; }
        for(int j=0;j<item->detail.combo.count;j++) { int k=find(c,item->detail.combo.ids[j]);if(k<0 || c->items[k].kind==COMBO) { puts("REJECT nested or missing combo component");return 0; }need[k]+=quantity; }
    }
    for(size_t i=0;i<c->count;i++) if(need[i]>0) {
        if(need[i]>c->items[i].stock) { printf("REJECT stock %s available=%d required=%lld\n",c->items[i].name,c->items[i].stock,need[i]);return 0; }
        if(c->items[i].kind==PACKAGED && date_serial(c->items[i].detail.expiry)<date_serial(c->today)) { printf("REJECT expired %s\n",c->items[i].name);return 0; }
    }
    require(item->price_paise>=0 && quantity<=INT_MAX,"bounded amount");
    long long revenue=item->price_paise*quantity;
    for(size_t i=0;i<c->count;i++) c->items[i].stock-=(int)need[i];
    c->bills[index].id=id;c->bills[index].quantity+=quantity;c->bills[index].revenue_paise+=revenue;
    printf("SALE id=%d quantity=%d revenue=%lld.%02lld\n",id,quantity,revenue/100,revenue%100);return 1;
}
static int revenue_compare(const void *x,const void *y) { const Bill *a=x,*b=y;if(a->revenue_paise!=b->revenue_paise) return a->revenue_paise<b->revenue_paise?1:-1;return (a->id>b->id)-(a->id<b->id); }
int main(void) {
    Canteen c={0};c.count=5;
    require(scanf("%d%d%d",&c.today.day,&c.today.month,&c.today.year)==3 && valid_date(c.today),"simulation date");
    c.items[0]=(Item){.id=1,.name="Juice",.price_paise=3000,.stock=10,.kind=PACKAGED,.detail.expiry={28,11,2026}};
    c.items[1]=(Item){.id=2,.name="Rice",.price_paise=6000,.stock=8,.kind=COOKED,.detail.prepared={10,30}};
    c.items[2]=(Item){.id=3,.name="MealCombo",.price_paise=8000,.kind=COMBO,.detail.combo={2,{1,2,0}}};
    c.items[3]=(Item){.id=4,.name="OldMilk",.price_paise=2000,.stock=5,.kind=PACKAGED,.detail.expiry={25,11,2026}};
    c.items[4]=(Item){.id=5,.name="TripleJuice",.price_paise=7500,.kind=COMBO,.detail.combo={3,{1,1,1}}};
    expiry_warning(&c);int id,quantity;
    while(scanf("%d%d",&id,&quantity)==2) {
        int before[10];Bill old[10];for(size_t i=0;i<c.count;i++) before[i]=c.items[i].stock;memcpy(old,c.bills,sizeof old);
        if(!sale(&c,id,quantity)) { for(size_t i=0;i<c.count;i++) require(before[i]==c.items[i].stock,"atomic stock rejection");require(memcmp(old,c.bills,sizeof old)==0,"atomic bill rejection");puts("UNCHANGED stock and revenue"); }
    }
    for(size_t i=0;i<c.count;i++) printf("STOCK id=%d %s=%d\n",c.items[i].id,c.items[i].name,c.items[i].stock);
    qsort(c.bills,c.count,sizeof c.bills[0],revenue_compare);long long total=0;
    for(size_t i=0;i<c.count;i++) if(c.bills[i].quantity) { printf("SUMMARY id=%d quantity=%lld revenue=%lld.%02lld\n",c.bills[i].id,c.bills[i].quantity,c.bills[i].revenue_paise/100,c.bills[i].revenue_paise%100);total+=c.bills[i].revenue_paise; }
    printf("TOTAL revenue=%lld.%02lld sizeof_Item=%zu pointer_overhead_per_list_node=%zu\n",total/100,total%100,sizeof(Item),sizeof(Item *));
    printf("DATE_CHECK year_boundary_days=%d leap_boundary_days=%d\n",date_serial((Date){1,1,2027})-date_serial((Date){31,12,2026}),date_serial((Date){1,3,2028})-date_serial((Date){28,2,2028}));return 0;
}
