#include "../../engineering_support/lab.h"
int main(int argc,char **argv) {
#ifdef _WIN32
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
#endif
    char name[16];
    if(argc==2 && !strcmp(argv[1],"unsafe")) {
        puts("INTENTIONAL unsafe scanf demonstration");fflush(stdout);
        if(scanf("%s",name)!=1) return 2;
        printf("unsafe length=%zu\n",strlen(name));return 0;
    }
    if(!fgets(name,sizeof name,stdin)) return 2;
    int truncated=strchr(name,'\n')==NULL;if(truncated) { int c;while((c=getchar())!='\n' && c!=EOF) {} }
    name[strcspn(name,"\r\n")]=0;printf("SAFE name=%s length=%zu truncated=%d\n",name,strlen(name),truncated);return 0;
}
