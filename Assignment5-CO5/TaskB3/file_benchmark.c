#include "../donor_model.h"
static long file_size(const char *path) { FILE *f=fopen(path,"rb");require(f!=NULL,"size open");require(fseek(f,0,SEEK_END)==0,"size seek");long n=ftell(f);require(fclose(f)==0 && n>=0,"size close");return n; }
static void write_file(const char *path,const DonorRecord *data,size_t n,int binary,int bulk) {
    FILE *f=fopen(path,binary?"wb":"w");require(f!=NULL,"write open");
    if(binary && bulk) require(fwrite(data,sizeof *data,n,f)==n,"bulk write");
    else for(size_t i=0;i<n;i++) require(binary?fwrite(data+i,sizeof *data,1,f)==1:write_text(f,data+i),"record write");
    require(fclose(f)==0,"write close");
}
static void verify_file(const char *path,const DonorRecord *data,size_t n,int binary) {
    FILE *f=fopen(path,binary?"rb":"r");require(f!=NULL,"read open");DonorRecord d;
    for(size_t i=0;i<n;i++) { require(binary?fread(&d,sizeof d,1,f)==1:read_text(f,&d),"read record");require(donor_equal(data+i,&d),"field round trip"); }
    require(fgetc(f)==EOF && !ferror(f),"exact file length");require(fclose(f)==0,"read close");
}
int main(void) {
    size_t sizes[]={10,1000,10000,100000};printf("RECORD sizeof=%zu alignment=%zu\n",sizeof(DonorRecord),_Alignof(DonorRecord));
    for(size_t k=0;k<4;k++) {
        size_t n=sizes[k];DonorRecord *data=allocate(n,sizeof *data);for(size_t i=0;i<n;i++) data[i]=generated_donor(i);
        char text[80],binary[80];snprintf(text,sizeof text,"TaskB3/data/donors_%zu.txt",n);snprintf(binary,sizeof binary,"TaskB3/data/donors_%zu.bin",n);
        for(int mode=0;mode<2;mode++) { const char *path=mode?binary:text;clock_t start=clock();write_file(path,data,n,mode,1);double w=elapsed(start);start=clock();verify_file(path,data,n,mode);double r=elapsed(start);printf("FILE n=%zu format=%s bytes=%ld write_cpu=%.9f read_verify_cpu=%.9f PASS\n",n,mode?"binary":"text",file_size(path),w,r); }
        if(n==100000) {
            const size_t index=49999;DonorRecord d;clock_t start=clock();FILE *f=fopen(binary,"rb+");require(f!=NULL,"update open");require(fseek(f,(long)(index*sizeof d),SEEK_SET)==0 && fread(&d,sizeof d,1,f)==1,"update read");d.age=42;require(fseek(f,-(long)sizeof d,SEEK_CUR)==0 && fwrite(&d,sizeof d,1,f)==1 && fclose(f)==0,"update write");double bt=elapsed(start);
            start=clock();FILE *in=fopen(text,"r"),*out=fopen("TaskB3/data/rewrite.txt","w");require(in && out,"text update open");
            for(size_t i=0;i<n;i++) { require(read_text(in,&d),"text update read");if(i==index) d.age=42;require(write_text(out,&d),"text update write"); }
            require(fclose(in)==0 && fclose(out)==0,"text update close");double tt=elapsed(start);data[index].age=42;verify_file(binary,data,n,1);verify_file("TaskB3/data/rewrite.txt",data,n,0);
            printf("UPDATE ordinal=50000 index=49999 binary_cpu=%.9f text_rewrite_cpu=%.9f untouched_fields_PASS\n",bt,tt);
            for(int bulk=0;bulk<2;bulk++) { start=clock();write_file("TaskB3/data/bulk.bin",data,n,1,bulk);double t=elapsed(start);verify_file("TaskB3/data/bulk.bin",data,n,1);printf("BULK n=%zu fwrite_calls=%zu write_cpu=%.9f PASS\n",n,bulk?(size_t)1:n,t); }
        }
        free(data);
    }
    return 0;
}
