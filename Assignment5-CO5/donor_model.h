#ifndef DONOR_MODEL_H
#define DONOR_MODEL_H
#include "../engineering_support/lab.h"
typedef struct { int id;char name[48],group[4];int age;char phone[12];Date last;int hospital; } DonorRecord;
static inline DonorRecord generated_donor(size_t i) {
    static const char *groups[]={"O+","O-","A+","A-","B+","B-","AB+","AB-"};
    DonorRecord d={0};d.id=7001+(int)i;snprintf(d.name,sizeof d.name,"Donor %06zu",i);strcpy(d.group,groups[i%8]);d.age=18+(int)(i%53);snprintf(d.phone,sizeof d.phone,"9%09zu",i%1000000000);d.last=(Date){1+(int)(i%28),1+(int)(i%11),2026};d.hospital=1+(int)(i%25);return d;
}
static inline int donor_equal(const DonorRecord *a,const DonorRecord *b) {
    return a->id==b->id && !strcmp(a->name,b->name) && !strcmp(a->group,b->group) && a->age==b->age && !strcmp(a->phone,b->phone) && a->last.day==b->last.day && a->last.month==b->last.month && a->last.year==b->last.year && a->hospital==b->hospital;
}
static inline int write_text(FILE *f,const DonorRecord *d) {
    return fprintf(f,"%d|%s|%s|%d|%s|%02d/%02d/%04d|%d\n",d->id,d->name,d->group,d->age,d->phone,d->last.day,d->last.month,d->last.year,d->hospital)>0;
}
static inline int read_text(FILE *f,DonorRecord *d) {
    char line[256],tail;int consumed=0;if(!fgets(line,sizeof line,f)) return 0;
    int fields=sscanf(line,"%d|%47[^|]|%3[^|]|%d|%11[^|]|%d/%d/%d|%d%n",&d->id,d->name,d->group,&d->age,d->phone,&d->last.day,&d->last.month,&d->last.year,&d->hospital,&consumed);
    return fields==9 && sscanf(line+consumed," %c",&tail)==EOF && valid_date(d->last) && d->hospital>=1 && d->hospital<=25;
}
#endif
