#define main supplied_main
#include "complete_the_code.c"
#undef main
#include "../../engineering_support/lab.h"
static unsigned root(unsigned n) {
    if(n<10) return n;
    unsigned sum=0;while(n) { sum+=n%10;n/=10; }return root(sum);
}
static long long iterative(long long b,int n) {
    long long r=1;while(n) { if(n%2) r*=b;n/=2;if(n) b*=b; }return r;
}
static long long duplicate(long long b,int n) {
    calls++;if(!n) return 1;
    long long a=duplicate(b,n/2),c=duplicate(b,n/2);return a*c*(n%2?b:1);
}
static long long odd_decrement(long long b,int n) {
    calls++;if(!n) return 1;if(n%2) return b*odd_decrement(b,n-1);
    long long a=odd_decrement(b,n/2),c=odd_decrement(b,n/2);return a*c;
}
int main(void) {
    unsigned ns[]={0,1,9875,999999,123456789};unsigned want[]={0,1,2,9,9};
    for(size_t i=0;i<5;i++) { unsigned v=root(ns[i]);require(v==want[i],"digital root");printf("ROOT %u -> %u PASS\n",ns[i],v); }
    struct { long long b;int n;long long want; } tests[]={{0,0,1},{0,1,0},{1,1,1},{2,10,1024},{3,7,2187},{5,4,625}};
    for(size_t i=0;i<6;i++) { long long a=power_linear(tests[i].b,tests[i].n),b=power_fast(tests[i].b,tests[i].n),c=iterative(tests[i].b,tests[i].n);require(a==tests[i].want && a==b && b==c,"power");printf("POWER %lld ^ %d = %lld three variants PASS\n",tests[i].b,tests[i].n,a); }
    int sizes[]={10,100,1000,10000};
    for(int i=0;i<4;i++) { calls=0;require(power_linear(1,sizes[i])==1,"linear");long long linear=calls;calls=0;require(power_fast(1,sizes[i])==1,"fast");printf("CALLS n=%d linear=%lld fast=%lld\n",sizes[i],linear,calls); }
    calls=0;long long value=duplicate(2,30);printf("DUPLICATE_HALF exp=30 value=%lld calls=%lld\n",value,calls);require(calls==63,"duplicate half count");
    calls=0;value=odd_decrement(2,30);printf("ODD_DECREMENT exp=30 value=%lld calls=%lld\n",value,calls);require(calls==61,"odd decrement count");return 0;
}
