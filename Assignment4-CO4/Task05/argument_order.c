#define main supplied_main
#include "complete_the_code.c"
#undef main
int main(void) {
    printf("%d %d %d\n",next_token(),next_token(),next_token());
    puts("Observed argument order is not a portable token-printing order.");return 0;
}
