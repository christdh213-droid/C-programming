#ifndef ENGINEERING_LAB_H
#define ENGINEERING_LAB_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <limits.h>
#include <errno.h>
#include <time.h>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <psapi.h>
#endif
typedef unsigned long long Count;
typedef struct { int day,month,year; } Date;
static inline void require(int ok,const char *what) { if(!ok) { fprintf(stderr,"FAIL: %s\n",what);exit(1); } }
static inline void *allocate(size_t n,size_t bytes) { void *p=calloc(n?n:1,bytes);require(p!=NULL,"allocation");return p; }
static inline double elapsed(clock_t start) { return (double)(clock()-start)/CLOCKS_PER_SEC; }
static inline int leap(int y) { return y%4==0 && (y%100!=0 || y%400==0); }
static inline int valid_date(Date d) {
    static const int lengths[]={31,28,31,30,31,30,31,31,30,31,30,31};
    return d.year>=1 && d.year<=9999 && d.month>=1 && d.month<=12 && d.day>=1 && d.day<=lengths[d.month-1]+(d.month==2 && leap(d.year));
}
static inline int date_serial(Date d) {
    static const int lengths[]={31,28,31,30,31,30,31,31,30,31,30,31};
    require(valid_date(d),"valid Gregorian date");int y=d.year-1,days=365*y+y/4-y/100+y/400+d.day;
    for(int m=1;m<d.month;m++) days+=lengths[m-1]+(m==2 && leap(d.year));
    return days;
}
static inline size_t peak_ram_bytes(void) {
#ifdef _WIN32
    PROCESS_MEMORY_COUNTERS info;
    if(GetProcessMemoryInfo(GetCurrentProcess(),&info,sizeof info)) return (size_t)info.PeakWorkingSetSize;
#endif
    return 0;
}
#endif
