#ifndef LAB_H
#define LAB_H
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef unsigned long long Count;
static inline void *allocate(size_t n, size_t size) {
    void *p=calloc(n?n:1,size); if(!p) { fputs("allocation failed\n",stderr); exit(1); } return p;
}
static inline double seconds(clock_t start) { return (double)(clock()-start)/CLOCKS_PER_SEC; }
static inline uint32_t random32(uint32_t *s) { *s=*s*1664525u+1013904223u; return *s; }
static inline void require(int ok,const char *message) { if(!ok) { fprintf(stderr,"FAIL: %s\n",message); exit(1); } }
/* clock() measures process CPU time, in seconds. No timing is fabricated or rounded up. */
#endif
