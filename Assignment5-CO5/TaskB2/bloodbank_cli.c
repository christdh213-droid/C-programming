#include "../../engineering_support/lab.h"
typedef struct { char group[4];int units; } Stock;
static const char *groups[]={"O+","O-","A+","A-","B+","B-","AB+","AB-"};
static int group_index(const char *s) { for(int i=0;i<8;i++) if(!strcmp(s,groups[i])) return i;return -1; }
static int usage(void) { fputs("Usage: bloodbank init | find GROUP | issue GROUP UNITS | register GROUP | pointers\n",stderr);return 2; }
static int *lowest_stock(int *stock,size_t n) { if(!n) return NULL;int *best=stock;for(size_t i=1;i<n;i++) if(stock[i]<*best) best=stock+i;return best; }
int main(int argc,char **argv) {
    const char *path=getenv("BLOODBANK_STOCK");if(!path) path="TaskB2/stock.bin";
    if(argc==2 && !strcmp(argv[1],"pointers")) {
        int stock[]={40,25,12,8,30,9,4,15};int *p=stock;
        printf("POINTER base=%p p+3=%p displacement=%zu value=%d indexed=%d\n",(void *)p,(void *)(p+3),3*sizeof *p,*(p+3),p[3]);
        int old=*p++;printf("POSTINCREMENT value=%d now_offset=%td\n",old,p-stock);int *best=lowest_stock(stock,8);printf("LOWEST index=%td before=%d",best-stock,*best);*best+=2;printf(" after=%d\n",*best);return 0;
    }
    if(argc==2 && !strcmp(argv[1],"init")) {
        FILE *fp=fopen(path,"wb");if(!fp) { perror(path);return 1; }
        Stock stock[8]={0};for(int i=0;i<8;i++) { strcpy(stock[i].group,groups[i]);stock[i].units=10+i; }
        int ok=fwrite(stock,sizeof *stock,8,fp)==8;int closed=fclose(fp)==0;if(!ok||!closed) { perror("stock init");return 1; }puts("Initialized eight stock records");return 0;
    }
    if(argc<3) return usage();
    int k=group_index(argv[2]);if(k<0) { fputs("Invalid blood group\n",stderr);return 2; }
    if(!strcmp(argv[1],"register") && argc==3) {
        char name[48];puts("Donor name:");if(!fgets(name,sizeof name,stdin)) { fputs("Missing name\n",stderr);return 2; }
        char *newline=strchr(name,'\n');if(!newline) { int c;while((c=getchar())!='\n' && c!=EOF) {}fputs("Name too long: rejected and drained\n",stderr);return 2; }
        *newline=0;size_t n=strlen(name);if(n && name[n-1]=='\r') name[--n]=0;
        if(!n||strchr(name,'|')) { fputs("Invalid name\n",stderr);return 2; }
        FILE *fp=fopen("TaskB2/registered.txt","a");if(!fp) { perror("donor file");return 1; }
        int ok=fprintf(fp,"%s|%s\n",name,groups[k])>=0;int closed=fclose(fp)==0;if(!ok||!closed) { perror("register");return 1; }printf("Registered %s (%s)\n",name,groups[k]);return 0;
    }
    int issue=!strcmp(argv[1],"issue");if((issue && argc!=4)||(!issue && (strcmp(argv[1],"find")||argc!=3))) return usage();
    long units=0;if(issue) { char *end;errno=0;units=strtol(argv[3],&end,10);if(errno||end==argv[3]||*end||units<=0||units>INT_MAX) { fputs("Invalid positive units\n",stderr);return 2; } }
    FILE *fp=fopen(path,issue?"rb+":"rb");if(!fp) { perror(path);return 1; }
    Stock stock[8];int ok=fread(stock,sizeof *stock,8,fp)==8;int extra=fgetc(fp);
    for(int i=0;i<8 && ok;i++) if(memcmp(stock[i].group,groups[i],strlen(groups[i])+1)||stock[i].units<0) ok=0;
    if(!ok||extra!=EOF||ferror(fp)) { fputs("Invalid stock file\n",stderr);fclose(fp);return 1; }
    if(issue) {
        if(stock[k].units<units) { fputs("Insufficient stock\n",stderr);fclose(fp);return 2; }
        stock[k].units-=(int)units;
        if(fseek(fp,(long)k*(long)sizeof(Stock),SEEK_SET)||fwrite(stock+k,sizeof(Stock),1,fp)!=1||fflush(fp)) { perror("stock update");fclose(fp);return 1; }
    }
    if(fclose(fp)) { perror("stock close");return 1; }printf("%s units=%d%s\n",groups[k],stock[k].units,issue?" after issue":"");return 0;
}
