#define main supplied_main
#include "complete_the_code.c"
#undef main
int main(void) {
    printf("sizeof(struct parcel)=%zu alignment=%zu bytes_per_swap=%zu\n",sizeof(struct parcel),_Alignof(struct parcel),3*sizeof(struct parcel));return 0;
}
