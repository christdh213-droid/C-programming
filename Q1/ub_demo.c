#include <stdio.h>
int main(void) {
    int count=0;
    count = count++ + 1;
    printf("Observed count = %d (undefined behaviour; not a portable result)\n",count);
    count=0;
    count += 1;
    printf("Correct increment = %d\n",count);
    return 0;
}
