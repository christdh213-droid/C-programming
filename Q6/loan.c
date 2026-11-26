#include <stdio.h>
#include <math.h>
static void simulate(double principal,double rate,double payment,unsigned cap,int detail) {
    printf("loan P=%.2f r=%.6f E=%.2f cap=%u\n",principal,rate,payment,cap);
    if(!isfinite(principal)||!isfinite(rate)||!isfinite(payment)||principal<0||rate<0||payment<=0||cap==0) { puts("INVALID INPUT"); return; }
    if(principal==0) { puts("ALREADY REPAID months=0 interest=0"); return; }
    if(payment<=principal*rate) { puts("NON AMORTIZING: repayment does not exceed first-month interest"); return; }
    double b=principal,total_interest=0,total_paid=0;
    unsigned month=0;
    if(detail) puts("month opening interest payment closing");
    while(b>0.0) {
        if(month==cap) { puts("SAFETY LIMIT: unpaid balance remains; review repayment terms"); break; }
        double interest=b*rate, due=b+interest;
        if(!isfinite(due)) { puts("NUMERIC RANGE ERROR"); break; }
        double paid=due<payment ? due : payment;
        double next=due-paid;
        ++month; total_interest+=interest; total_paid+=paid;
        if(detail) printf("%u %.8f %.8f %.8f %.8f\n",month,b,interest,paid,next);
        b=next;
    }
    double exact=rate==0 ? principal/payment : -log1p(-rate*principal/payment)/log1p(rate);
    printf("RESULT months=%u interest=%.8f paid=%.8f balance=%.8f formula=%.8f ceil=%.0f\n",month,total_interest,total_paid,b,exact,ceil(exact));
}
int main(void) {
    double p,r,e; unsigned cap; int detail;
    while(scanf("%lf%lf%lf%u%d",&p,&r,&e,&cap,&detail)==5) simulate(p,r,e,cap,detail);
    return 0;
}
