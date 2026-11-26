#include <stdio.h>
#include <limits.h>
static void show(unsigned char reg) {
    for(int b=7;b>=0;b--) putchar((reg>>b)&1u ? '1':'0');
}
int main(void) {
    unsigned char reg=0, state[8]={0};
    const int devs[]={7,0,7,0};
    for(int k=0;k<4;k++) {
        unsigned mask=1u<<devs[k];
        if(k<2) { reg=(unsigned char)(reg|mask); state[devs[k]]=1; }
        else if(k==2) { reg=(unsigned char)(reg^mask); state[devs[k]]^=1; }
        else { reg=(unsigned char)(reg&~mask); state[devs[k]]=0; }
        unsigned count=0, array_count=0;
        for(int j=0;j<8;j++) { count+=(reg>>j)&1u; array_count+=state[j]; }
        printf("step=%d value=%u binary=",k+1,(unsigned)reg); show(reg);
        printf(" bit_count=%u array_count=%u\n",count,array_count);
        if(count!=array_count) return 1;
    }
    reg=2; int dev=1;
    printf("reg=2 dev=1: reg & 1 << dev = %u; (reg & 1) << dev = %u\n",reg & 1u << dev,(reg & 1u) << dev);
    signed char s=(signed char)128u;
    printf("CHAR_BIT=%d sizeof register=%zu array=%zu; signed conversion=%d right_shift=%d\n",CHAR_BIT,sizeof reg,sizeof state,(int)s,s>>1);
    puts("1000000 homes: register=1000000 bytes; array=8000000 bytes; count visits=8 per home in both.");
    return 0;
}
