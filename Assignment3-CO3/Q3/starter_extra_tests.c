#define main supplied_main
#include "complete_the_code.c"
#undef main
int main(void) {
    const int b[]={95,91,80};int out[3];
    int n=merge(NULL,0,b,3,out);
    printf("Empty A -> ");for(int i=0;i<n;i++) printf("%d ",out[i]);putchar('\n');
    if(n!=3 || out[0]!=95 || out[1]!=91 || out[2]!=80) return 1;
    printf("Both empty -> count %d\n",merge(NULL,0,NULL,0,out));
    return 0;
}
