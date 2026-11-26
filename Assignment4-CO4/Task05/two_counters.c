#include <stdio.h>
static int globals[2]={1000,1000};
static int auto_next(int which) { auto int tokens[2]={1000,1000};return ++tokens[which]; }
static int static_next(int which) { static int tokens[2]={1000,1000};return ++tokens[which]; }
static int global_next(int which) { return ++globals[which]; }
static int next_token(int *counter) { return ++*counter; }
int main(void) {
    int owned[2]={1000,1000};
    for(int mode=0;mode<4;mode++) {
        printf("TWO %s",mode==0?"auto":mode==1?"static":mode==2?"global":"pointer");
        for(int i=0;i<4;i++) { int which=i%2;int token=mode==0?auto_next(which):mode==1?static_next(which):mode==2?global_next(which):next_token(&owned[which]);printf(" %s=%d",which?"nonveg":"veg",token); }
        putchar('\n');
    }
    puts("MODIFICATION_COUNTS: auto/static/global add one second state cell and one selector parameter; pointer adds one caller-owned cell and zero function-body changes.");
    puts("register applies to the printing loop, not persistent token storage; its address cannot be taken in C11.");return 0;
}
