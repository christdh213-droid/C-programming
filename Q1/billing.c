#include <stdio.h>
int main(void) {
    int price, qty, senior;
    puts("price qty senior | original_total original_net | corrected_net");
    while (scanf("%d%d%d", &price, &qty, &senior)==3) {
        int total, net;
        total = price * qty - price * qty * 15 / 100 * senior + price * qty * 5 / 100;
        net = total > 1000 ? total - 50 : total;
        double gross=(double)price*qty;
        double discount=senior ? gross*0.15 : 0.0;
        double taxable=gross-discount;
        double tax=taxable*0.05;
        double corrected=taxable+tax;
        if (corrected>1000.0) corrected-=50.0;
        printf("%d %d %d | %d %d | %.6f\n",price,qty,senior,total,net,corrected);
    }
    puts("Static arithmetic operations: original 11; corrected 5 (senior case); comparisons/branches excluded.");
    return 0;
}
