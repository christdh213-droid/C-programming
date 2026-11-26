#include "../lab.h"
static volatile double checksum;
static Count visits;
static void annual_totals(int rows,int cols,const double a[rows][cols],double totals[rows]) {
    visits=0;for(int i=0;i<rows;i++) { totals[i]=0;for(int j=0;j<cols;j++) { totals[i]+=a[i][j];++visits; } }
}
static void monthly_averages(int rows,int cols,const double a[rows][cols],double averages[cols]) {
    visits=0;for(int j=0;j<cols;j++) { averages[j]=0;for(int i=0;i<rows;i++) { averages[j]+=a[i][j];++visits; } averages[j]/=rows; }
}
static void wettest(int rows,int cols,const double a[rows][cols],int *district,int *month,double *maximum) {
    *district=0;*month=0;*maximum=a[0][0];visits=0;
    for(int i=0;i<rows;i++) for(int j=0;j<cols;j++) { ++visits;if(a[i][j]>*maximum) { *maximum=a[i][j];*district=i;*month=j; } }
}
static int deficient(int rows,const double totals[rows],int indices[rows],double *average) {
    *average=0;for(int i=0;i<rows;i++) *average+=totals[i];*average/=rows;
    int count=0;for(int i=0;i<rows;i++) if(totals[i]<.6*(*average)) indices[count++]=i;
    return count;
}
static void analyse(const char *name,int rows,int cols,const double a[rows][cols]) {
    double *totals=allocate((size_t)rows,sizeof *totals),*averages=allocate((size_t)cols,sizeof *averages);
    int *indices=allocate((size_t)rows,sizeof *indices);double average,maximum;int district,month;
    printf("DATASET %s rows=%d cols=%d\n",name,rows,cols);
    annual_totals(rows,cols,a,totals);printf("annual_visits=%llu\n",visits);
    for(int i=0;i<rows;i++) printf("ANNUAL %d %.6f\n",i,totals[i]);
    monthly_averages(rows,cols,a,averages);printf("monthly_visits=%llu\n",visits);
    for(int j=0;j<cols;j++) printf("MONTHLY %d %.6f\n",j,averages[j]);
    wettest(rows,cols,a,&district,&month,&maximum);printf("WETTEST district=%d month=%d mm=%.6f visits=%llu\n",district,month,maximum,visits);
    int count=deficient(rows,totals,indices,&average);
    printf("STATE_ANNUAL_AVERAGE %.6f threshold=%.6f deficient_count=%d\n",average,.6*average,count);
    for(int i=0;i<count;i++) printf("DEFICIENT %d\n",indices[i]);
    free(totals);free(averages);free(indices);
}
int main(void) {
    const double trial[3][4]={{10,20,30,40},{0,0,0,0},{20,30,40,50}};
    analyse("hand",3,4,trial);
    double rain[38][12];
    for(int i=0;i<38;i++) for(int j=0;j<12;j++) require(scanf("%lf",&rain[i][j])==1 && rain[i][j]>=0,"38x12 nonnegative rainfall input");
    analyse("full",38,12,rain);
    double flat[38*12],*rows[38];
    for(int i=0;i<38;i++) { rows[i]=allocate(12,sizeof **rows);for(int j=0;j<12;j++) { flat[i*12+j]=rain[i][j];rows[i][j]=rain[i][j]; } }
    puts("LAYOUT method repetitions cells_visited pointer_bytes cpu_seconds checksum");
    for(int mode=0;mode<3;mode++) {
        double sum=0;clock_t start=clock();
        for(int r=0;r<20000;r++) {
            for(int i=0;i<38;i++) for(int j=0;j<12;j++) sum+=mode==0?rain[i][j]:(mode==1?flat[i*12+j]:rows[i][j]);
            checksum=sum;
        }
        double elapsed=seconds(start);
        printf("%s 20000 9120000 %zu %.9f %.3f\n",mode==0?"2D":mode==1?"flat":"row_pointers",mode==2?sizeof rows:0,elapsed,sum);
    }
    for(int i=0;i<38;i++) free(rows[i]);
    const int n=2000,reps=5;
    double *storage=allocate((size_t)n*n,sizeof *storage);
    for(int i=0;i<n;i++) for(int j=0;j<n;j++) storage[(size_t)i*n+j]=(i%101)+(j%97)/10.0;
    volatile double *big=storage;
    puts("TRAVERSAL order dimension repetitions cells_visited data_bytes cpu_seconds checksum");
    for(int mode=0;mode<2;mode++) {
        double sum=0;clock_t start=clock();
        for(int r=0;r<reps;r++) {
            if(mode==0) for(int i=0;i<n;i++) for(int j=0;j<n;j++) sum+=big[(size_t)i*n+j];
            else for(int j=0;j<n;j++) for(int i=0;i<n;i++) sum+=big[(size_t)i*n+j];
        }
        double elapsed=seconds(start);checksum=sum;
        printf("%s 2000 %d %d %zu %.9f %.3f\n",mode==0?"row":"column",reps,n*n*reps,(size_t)n*n*sizeof(double),elapsed,sum);
    }
    printf("clock_ticks_per_second=%ld final_checksum=%.3f\n",(long)CLOCKS_PER_SEC,checksum);
    free(storage);return 0;
}
