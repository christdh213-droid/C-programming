from pathlib import Path
import re
R=Path(__file__).resolve().parent.parent
tasks={4:['Task02','Task03','Task05'],5:['TaskB1','TaskB3','TaskB4']}
bodies={
(4,'Task02'):[r'''    printf("%d %.1f kg %s-%d %02d/%02d/%04d\n",p->id,p->weight,
           p->to.city,p->to.pincode,p->booked.day,p->booked.month,p->booked.year);''',r'''    for (int i = 0; i < n - 1; i++) {
        int lightest = i;
        for (int j = i + 1; j < n; j++) if (p[j].weight < p[lightest].weight) lightest = j;
        if (lightest != i) { struct parcel temp = p[i]; p[i] = p[lightest]; p[lightest] = temp; }
    }'''],
(4,'Task03'):[r'''    switch (r->type) {
        case TEMPERATURE: printf("Temp %.1f C\n",r->value.celsius); break;
        case HUMIDITY: printf("Humidity %d%%\n",r->value.percent); break;
        case STATUS: printf("Status %s\n",r->value.status); break;
    }'''],
(4,'Task05'):[r'''    static int token = 1000;
    return ++token;'''],
(5,'TaskB1'):[r'''    if (exp == 0) return 1;
    long long half = power_fast(base, exp / 2);
    return half * half * (exp % 2 ? base : 1);'''],
(5,'TaskB3'):[r'''    if (index < 0) return 0;
    if (fseek(fp, (long)index * (long)sizeof s, SEEK_SET) != 0) return 0;
    if (fread(&s, sizeof s, 1, fp) != 1) return 0;
    s.units = units;
    if (fseek(fp, -(long)sizeof s, SEEK_CUR) != 0) return 0;
    return fwrite(&s, sizeof s, 1, fp) == 1;'''],
(5,'TaskB4'):[r'''        int capacity = list->capacity == 0 ? 2 : list->capacity * 2;
        Donor *p = realloc(list->data, (size_t)capacity * sizeof *p);
        if (p == NULL) return 0;
        list->data = p;
        list->capacity = capacity;''']}
expected={
(4,'Task02'):'502 1.2 kg Chennai-600077 12/10/2026\n503 2.8 kg Coimbatore-641001 13/10/2026\n501 4.5 kg Madurai-625001 12/10/2026\n',
(4,'Task03'):'sizeof union = 8, sizeof struct reading = 12\nTemp 31.5 C\nHumidity 68%\nStatus OK\n',
(4,'Task05'):'static: 1001 1002 1003\nauto  : 1001 1001 1001\n',
(5,'TaskB1'):'linear: 1073741824 in 31 calls\nfast  : 1073741824 in 6 calls\n',
(5,'TaskB3'):'update record 3: done\nupdate record 9: failed\n1:40 2:25 3:12 4:20 5:30 \n',
(5,'TaskB4'):''.join(f'added {7001+i} ({g}): size = {i+1}, capacity = {c}\n' for i,(g,c) in enumerate(zip(['O+','A+','B-','AB+','O-'],[2,2,4,4,8]))) }
for number,names in tasks.items():
    a=R/f'Assignment{number}-CO{number}';text=(a/'reference/assignment.txt').read_text(encoding='utf-8')
    blocks=re.findall(r'#include <stdio.h>.*?\n}\s*\nExpected output:',text,re.S)
    assert len(blocks)==3
    for task,block in zip(names,blocks):
        starter=block.rsplit('Expected output:',1)[0].rstrip()+'\n';folder=a/task
        (folder/'starter.txt').write_text(starter,encoding='utf-8')
        parts=re.split(r'(\s*// TODO[^\n]*(?:\n\s*//[^\n]*)*\n)',starter)
        assert len(parts)//2==len(bodies[number,task]),(number,task,len(parts))
        for i in range(1,len(parts),2):parts[i+1]=bodies[number,task].pop(0)+'\n'+parts[i+1]
        (folder/'complete_the_code.c').write_text(''.join(parts),encoding='utf-8')
        (folder/'expected').mkdir(exist_ok=True)
        (folder/'expected/complete_the_code.txt').write_bytes(expected[number,task].encode().replace(b'\n',b'\r\n'))
