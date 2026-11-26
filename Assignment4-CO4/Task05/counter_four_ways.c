#include <stdio.h>
extern int shared_token;
extern int external_next(void);
static int automatic_next(void) { auto int token=1000;return ++token; }
static int static_next(void) { static int token=1000;return ++token; }
int main(void) {
    printf("auto:");for(int i=0;i<3;i++) printf(" %d",automatic_next());putchar('\n');
    printf("static:");for(int i=0;i<3;i++) printf(" %d",static_next());putchar('\n');
    printf("extern:");for(int i=0;i<3;i++) printf(" %d",external_next());putchar('\n');
    printf("register loop:");for(register int i=0;i<3;i++) printf(" %d",i);putchar('\n');
    printf("extern final state=%d\n",shared_token);return 0;
}
