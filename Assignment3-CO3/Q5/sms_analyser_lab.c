#include "../lab.h"
#include <ctype.h>
static volatile Count sink;
static size_t manual_length(const char *s) { size_t n=0;while(s[n]) ++n;return n; }
static unsigned words(const char *s) {
    unsigned result=0;int inside=0;
    for(size_t i=0;s[i];i++) { if(isspace((unsigned char)s[i])) inside=0;else if(!inside) { ++result;inside=1; } }
    return result;
}
static void upper_manual(char *out,const char *in) {
    size_t i=0;for(;in[i];i++) out[i]=in[i]>='a'&&in[i]<='z'?(char)(in[i]-'a'+'A'):in[i];out[i]='\0';
}
static void reverse_manual(char *out,const char *in) {
    size_t n=manual_length(in);for(size_t i=0;i<n;i++) out[i]=in[n-1-i];out[n]='\0';
}
static int palindrome_manual(const char *s) {
    size_t left=0,right=manual_length(s);
    while(left<right) {
        while(left<right && !isalpha((unsigned char)s[left])) ++left;
        while(left<right && !isalpha((unsigned char)s[right-1])) --right;
        if(left<right && tolower((unsigned char)s[left])!=tolower((unsigned char)s[right-1])) return 0;
        if(left<right) { ++left;--right; }
    }
    return 1;
}
static int palindrome_library(const char *s) {
    size_t n=strlen(s),k=0;char *clean=allocate(n+1,1),*rev=allocate(n+1,1);
    for(size_t i=0;i<n;i++) if(isalpha((unsigned char)s[i])) clean[k++]=(char)tolower((unsigned char)s[i]);
    for(size_t i=0;i<k;i++) rev[i]=clean[k-1-i];
    int yes=strcmp(clean,rev)==0;free(clean);free(rev);return yes;
}
static unsigned words_library(const char *s) {
    size_t n=strlen(s);char *copy=allocate(n+1,1);strcpy(copy,s);unsigned result=0;
    for(char *token=strtok(copy," \t\r\n\v\f");token;token=strtok(NULL," \t\r\n\v\f")) ++result;
    free(copy);return result;
}
static void compare(const char *s) {
    char a[512],b[512],rev[512],librev[512];size_t n=strlen(s);require(n<sizeof a,"test string fits");
    upper_manual(a,s);strcpy(b,s);for(size_t i=0;i<n;i++) b[i]=(char)toupper((unsigned char)b[i]);
    reverse_manual(rev,s);strcpy(librev,s);for(size_t i=0;i<n/2;i++) { char t=librev[i];librev[i]=librev[n-1-i];librev[n-1-i]=t; }
    unsigned wa=words(s),wb=words_library(s);int pa=palindrome_manual(s),pb=palindrome_library(s);
    require(strcmp(a,b)==0 && strcmp(rev,librev)==0 && wa==wb && pa==pb,"manual/library agreement");
    printf("TEXT [%s]\nWORDS manual=%u library=%u PAL manual=%d library=%d\nUPPER [%s]\nREVERSE [%s]\n",s,wa,wb,pa,pb,a,rev);
}
static void recursive_reverse(char *s,size_t left,size_t right,size_t depth,size_t *maxdepth) {
    volatile unsigned char marker=(unsigned char)depth;
    if(depth>*maxdepth) *maxdepth=depth;
    if(left<right) { char t=s[left];s[left]=s[right];s[right]=t;recursive_reverse(s,left+1,right-1,depth+1,maxdepth); }
    sink+=marker; /* Work after the call prevents a source-level tail call. */
}
int main(void) {
    compare("  Meet at  the library at 5 PM ");compare("Madam, I'm Adam");compare("Hello, world!");compare("");compare("one\ttwo");compare("!!!");
    char long_message[128],small[8];
    require(fgets(long_message,sizeof long_message,stdin)!=NULL,"runtime long message input");
    char *newline=strchr(long_message,'\n');if(newline) *newline='\0';
    printf("SAFETY unsafe strcpy would need %zu bytes in capacity=%zu; NOT executed\n",strlen(long_message)+1,sizeof small);
    strncpy(small,long_message,sizeof small-1);small[sizeof small-1]='\0';printf("strncpy bounded [%s] length=%zu\n",small,strlen(small));
    int needed=snprintf(small,sizeof small,"%s",long_message);printf("snprintf [%s] required=%d truncated=%d\n",small,needed,needed>=(int)sizeof small);
    require(fgets(small,sizeof small,stdin)!=NULL,"fgets safety input");printf("fgets first chunk [%s] length=%zu\n",small,strlen(small));
    int ch,drained=0;while((ch=getchar())!='\n' && ch!=EOF) ++drained;printf("fgets drained_remaining=%d\n",drained);
    puts("STRLEN n method length_calls reps cpu_seconds checksum");
    size_t (*volatile length_call)(const char *)=strlen;
    for(size_t n=1000;n<=10000;n*=10) {
        char *s=allocate(n+1,1);memset(s,'x',n);
        for(int mode=0;mode<2;mode++) {
            Count calls=0,sum=0;const int reps=100;clock_t begin=clock();
            for(int rep=0;rep<reps;rep++) {
                if(mode==0) { size_t i=0;for(;;) { size_t length=length_call(s);++calls;if(i>=length) break;sum+=(unsigned char)s[i++]; } }
                else { size_t length=length_call(s);++calls;for(size_t i=0;i<length;i++) sum+=(unsigned char)s[i]; }
            }
            double elapsed=seconds(begin);sink+=sum;
            printf("%zu %s %llu %d %.9f %llu\n",n,mode==0?"repeated":"cached",calls,reps,elapsed,sum);
        }
        size_t maxdepth=0;recursive_reverse(s,0,n-1,1,&maxdepth);printf("RECURSION n=%zu max_active_calls=%zu\n",n,maxdepth);free(s);
    }
    printf("clock_ticks_per_second=%ld sink=%llu\n",(long)CLOCKS_PER_SEC,sink);return 0;
}
