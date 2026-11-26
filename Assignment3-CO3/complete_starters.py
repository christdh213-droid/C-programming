from pathlib import Path
import re
R=Path(__file__).resolve().parent
text=(R/'reference/assignment.txt').read_text(encoding='utf-8')
blocks=re.findall(r'#include <stdio.h>.*?\n}\s*\nExpected output:',text,re.S)
bodies={1:[r'''    int low = 0, high = n - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        steps++;
        if (a[mid] == key) return mid;
        if (a[mid] < key) low = mid + 1;
        else high = mid - 1;
    }'''],3:[r'''    while (i < na && j < nb) {
        if (a[i] >= b[j]) out[k++] = a[i++];
        else out[k++] = b[j++];
    }
    while (i < na) out[k++] = a[i++];
    while (j < nb) out[k++] = b[j++];'''],5:[r'''    for (int i = 0; s[i] != '\0'; i++) {
        if (isspace((unsigned char)s[i])) inside = 0;
        else if (!inside) { count++; inside = 1; }
    }''',r'''    while (left < right) {
        while (left < right && !isalpha((unsigned char)s[left])) left++;
        while (left < right && !isalpha((unsigned char)s[right])) right--;
        if (tolower((unsigned char)s[left]) != tolower((unsigned char)s[right])) return 0;
        left++; right--;
    }''']}
expected={1:'Book 1021 -> index 0, comparisons = 3\nBook 1305 -> index 5, comparisons = 3\nBook 1533 -> index 9, comparisons = 4\nBook 1400 -> index -1, comparisons = 4\n',3:'98 95 91 91 85 80 72 \n',5:'Words: 7\n1 0\n'}
for index,q in enumerate((1,3,5)):
    starter=blocks[index].rsplit('Expected output:',1)[0].rstrip()+'\n'
    (R/f'Q{q}/starter.txt').write_text(starter,encoding='utf-8')
    parts=re.split(r'(    // TODO[^\n]*(?:\n    //[^\n]*)*\n)',starter)
    for k in range(1,len(parts),2): parts[k+1]=bodies[q].pop(0)+'\n'+parts[k+1]
    (R/f'Q{q}/complete_the_code.c').write_text(''.join(parts),encoding='utf-8')
    e=R/f'Q{q}/expected';e.mkdir(exist_ok=True)
    (e/'complete_the_code.txt').write_bytes(expected[q].encode().replace(b'\n',b'\r\n'))
