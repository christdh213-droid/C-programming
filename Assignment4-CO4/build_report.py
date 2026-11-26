from pathlib import Path
import sys,json,re,hashlib,struct
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'engineering_support'))
from artifacts import Report,screenshots,readme,ROOT
R=Path(__file__).resolve().parent
def raw(t,n):return (R/t/'outputs'/f'{n}.stdout.txt').read_text()
def verify():
    checks=[]
    for task in ('Task02','Task03','Task05'):
        a=(R/task/'starter.txt').read_text();b=(R/task/'complete_the_code.c').read_text();assert a[a.index('int main(void)'):]==b[b.index('int main(void)'):]
        parts=re.split(r'(\s*// TODO[^\n]*(?:\n\s*//[^\n]*)*\n)',a);position=0
        for i,part in enumerate(parts):
            if i and i%2==0:part=part.lstrip('\n')
            at=b.find(part,position);assert at>=position;(position:=at+len(part))
        assert (R/task/'expected/complete_the_code.txt').read_bytes()==(R/task/'outputs/complete_the_code.stdout.txt').read_bytes()
        checks.append(task+' Complete-the-Code: PASS; preserved main and exact fixture bytes')
    for manifest in R.glob('Task*/outputs/manifest.json'):
        for row in json.loads(manifest.read_text()):
            if row.get('intentional_error'):assert row['compile_exit']!=0;continue
            assert (manifest.parent/(Path(row['source']).stem+'.compiler.txt')).read_bytes()==b''
            if row.get('object_only'):continue
            assert hashlib.sha256((manifest.parent/(Path(row['source']).stem+'.stdout.txt')).read_bytes()).hexdigest()==row['stdout_sha256']
    assert 'PATIENT Bala age=28' in raw('Task01','patient_register') and 'after=2' in raw('Task01','patient_register')
    assert 'array=641001 pointer=641001' in raw('Task02','courier_full')
    assert hex(struct.unpack('<I',struct.pack('<f',31.5))[0])[2:] in raw('Task03','weather_lab')
    for v in ('5200.00','12480.00','832.00'):assert v in raw('Task04','repaired_bank')
    addresses=re.findall(r'(CALLER|VALUE) address=(\S+)',raw('Task04','address_proof'));assert all(addresses[i][1]!=addresses[i+1][1] for i in (0,2,4))
    assert raw('Task06','canteen_system').count('UNCHANGED stock and revenue')==5
    assert 'TOTAL revenue=420.00' in raw('Task06','canteen_system') and 'year_boundary_days=1 leap_boundary_days=2' in raw('Task06','canteen_system')
    checks+=['All successful builds: zero compiler diagnostics; all captured stdout hashes PASS','Patient capacity, courier pointer path, union bit pattern and distinct value-copy addresses PASS','Bank balances, five atomic sale rejections, revenue totals and calendar boundaries PASS','Task05 literal requested auto: conflicts with preserved main auto  :; fixture follows exact starter main']
    (R/'qa/verification.txt').write_text('\n'.join(checks)+'\n');print('\n'.join(checks))
verify();screenshots(R)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
fig,ax=plt.subplots(figsize=(7,2.7));ax.set_xlim(0,21);ax.set_ylim(-.4,2.3);ax.axis('off')
for y,label,parts in [(1.3,'Tagged reading',[(0,4,'tag'),(4,8,'overlapping union payload')]),(.3,'All fields with tag',[(0,4,'tag'),(4,4,'float'),(8,4,'int'),(12,8,'status[8]')])]:
    ax.text(0,y+.65,label,fontsize=10)
    for offset,size,label in parts:
        ax.add_patch(Rectangle((offset,y),size,.5,facecolor='#dce8f0',edgecolor='#536777'));ax.text(offset+size/2,y+.25,label,ha='center',va='center',fontsize=8);ax.text(offset,y-.14,str(offset),fontsize=8)
    ax.text(sum(p[1] for p in parts),y-.14,str(sum(p[1] for p in parts)),fontsize=8)
fig.tight_layout();fig.savefig(R/'charts/weather_layout.png',dpi=300);plt.close(fig)
d=Report(R,4,'Structures Unions and Storage Classes')
d.chapter('Assessment and execution method')
d.p('The six tasks diagnose data-model errors, design nested records, measure unions, prove structure-copy behaviour, compare storage classes and implement canteen billing. Sizes, addresses, compiler diagnostics and CPU readings are captured from actual GCC runs. Conceptual assignment-copy bytes are distinguished from hardware memory traffic.')
d.table(['Task','Competency','Marks'],[[1,'PHC data design',6],[2,'Courier nested structures',8],[3,'Unions and memory layout',9],[4,'Structure forensics',7],[5,'Storage classes',7],[6,'Canteen design challenge',13],['Total','',50]])
d.code((ROOT/'engineering_support/environment/gcc.txt').read_text(),8)
d.p('All successful builds use -std=c11 -Wall -Wextra with no diagnostics. forensics_bug.c intentionally fails compilation; extern_store.c is compiled as an object and linked into both counter applications. clock() reports process CPU time; zero ticks are retained. PREDICTIONS.md was committed before execution. Full raw output is stored under each task outputs folder. Pseudocode uses named algorithms, INPUT/OUTPUT, numbered steps, BEGIN/END and structured control words, with no C replacing the algorithms.')
d.chapter('Task01 PHC Patient Register')
d.h('Diagnosis')
d.table(['Deficiency','Clinic failure'],[['Parallel arrays','A partial move or sort pairs a name with another patient’s age or phone.'],['phone[10]','Ten digits leave no NUL; strcpy writes past the field and can corrupt another record.'],['One float for BP','Systolic and diastolic values cannot be represented independently; ratios lose meaning.'],['visitDate[8]','dd/mm/yyyy needs ten characters plus NUL; text admits invalid dates and awkward comparisons.'],['Unbounded count','The 101st insertion writes outside every array.'],['Global mutable count and arrays','Unrelated functions can alter registration state or mix clinics.'],['Unbounded strcpy and short name','A long name or phone can overflow storage.'],['Field-wise sorting','Every parallel column must move together, increasing inconsistency risk.']])
d.h('Repaired design')
d.p('Patient groups name, age and a ten-digit phone with its NUL. Date and BloodPressure are nested types. addPatient receives the destination array, count pointer, capacity and a const source record. It validates capacity, age, phone digits, BP ordering and Gregorian date before writing. The demonstration stores three records, rejects the third insertion into a separate two-record capacity test, then sorts whole patients by age.')
d.code(raw('Task01','patient_register'),8)
d.h('Design Defence')
defence='A Patient keeps related fields together, so one structure swap preserves identity while sorting. Nested Date and BloodPressure make each component explicit and reusable. A pointer-based insertion interface updates only the caller’s chosen register and checks capacity before writing. Const input documents that the source patient is read only. New fields can be added to Patient without coordinating another parallel array, and functions can receive one coherent record instead of several unrelated arguments.'
assert len(defence.split())<=100;d.p(defence)
d.h('Alternative Concept and Complexity Analysis')
d.p('The measured Patient is 76 bytes, comprising 75 field bytes and one alignment byte before BP. One hundred equivalent SoA records use 7500 bytes versus 7600 for AoS. The original smaller but defective arrays are not a fair equal-field comparison. Two actual selection-sort swaps imply 456 AoS assignment bytes versus 450 equivalent field-by-field SoA bytes, using three assignments per swap; compiler/ABI optimizations can remove physical copies. Both selection sorts take O(n²) comparisons, with O(record size) work per complete swap and O(1) temporary record storage. SoA is useful for vectorized age-only scans or column analytics, but requires disciplined synchronization when records move. An index sort avoids moving either representation’s payload.')
d.evidence('Task01');d.sources('Task01')
d.chapter('Task02 Courier Parcel Tracking')
d.h('Entity model and definitions')
d.p('Parcel owns ID, weight, Date booked, sender Address, receiver Address, Service and charge in integer paise. Address owns name, city and PIN. The full application stores the day’s bookings in an array of Parcel records; the starter uses its smaller supplied address model. Receiver city filtering uses exact case-sensitive equality.')
d.h('SIMATS algorithmic pseudocode')
d.code('ALGORITHM SORT PARCELS BY WEIGHT\nINPUT: bookings and count n\nOUTPUT: bookings in nondecreasing weight order\nBEGIN\n1. FOR position FROM 0 TO n minus 2 DO\n2.   SET lightest TO position\n3.   FOR candidate FROM position plus 1 TO n minus 1 DO\n4.     IF candidate weight is smaller THEN SET lightest TO candidate\n5.   END FOR\n6.   IF lightest differs from position THEN SWAP the complete records\n7. END FOR\nEND\n\nALGORITHM FILTER RECEIVER CITY\nINPUT: bookings, n and requested city\nOUTPUT: all matching bookings\nBEGIN\n1. FOR EACH booking DO\n2.   IF receiver city equals requested city THEN DISPLAY booking\n3. END FOR\nEND',8)
d.h('Access expressions and Complete the Code')
d.code('list[2].to.pincode\n(ptr + 2)->to.pincode',8);d.code(raw('Task02','complete_the_code')+raw('Task02','starter_layout')+raw('Task02','courier_full'),8)
d.p('The requested single-space output is implemented inside TODO 1 without changing main. The starter parcel measures 44 bytes, so a whole-record exchange with a temporary has 132 conceptual copy bytes. The third original parcel PIN is 641001 by either access path. Sorting keeps all sender, receiver, date and charge fields attached.')
d.h('Alternative Concept and Complexity Analysis')
d.p('A flat structure repeats sender_name, sender_city, sender_pin and receiver equivalents; nested fields use from.name and to.pincode. Reusable Address supports both parties consistently. The equivalent field order gives 160 bytes in both full nested and flat designs on this GCC target; nesting does not inherently add allocation or pointer overhead. Both provide O(1) field access and O(n) city filtering. Selection sort makes O(n²) weight comparisons and O(n) whole-record swaps, with O(1) temporary records. Other member orders may change padding, so sizeof evidence is essential.')
d.evidence('Task02');d.sources('Task02')
d.chapter('Task03 Weather Station Packets')
d.h('Design prediction and measured layout')
d.p('A structure holding temperature, humidity and status simultaneously wastes inactive fields when each packet carries one kind. The tagged union stores one payload plus an enum indicating its valid interpretation. Prediction on this target was float4, int4, status8, union8 aligned4 and tag4 plus union8 equals12. The actual output verifies this layout.')
d.code(raw('Task03','complete_the_code')+raw('Task03','weather_lab'),8)
d.p('AllValues is 16 bytes; adding a tag to all fields gives 20. In reading, type occupies bytes0..3 and value occupies bytes4..11. All union members overlap at that same offset, so their sizes are not summed. The largest member is status[8], with union alignment4; no extra tail padding is needed beyond byte11. These sizes are ABI observations, not a portable language guarantee.')
d.picture('charts/weather_layout.png','Byte-offset schematic based on measured sizes and offsetof; this is a memory-layout diagram, not an address capture.')
d.h('Misuse experiment')
d.p('Writing 31.5f and reading percent yields the recorded inactive integer 1107034112. memcpy independently observes binary32 bits 0x41fc0000: sign0, biased exponent131 and fraction0x7c0000 represent 1.96875 times 2^4. Interpreting those bits as this target’s integer is not a numeric conversion to31. Production code must dispatch on the tag; other representations or trap representations can make inactive-member use unsuitable or unsafe.')
d.h('Alternative Concept and Complexity Analysis')
d.p('For 30000 mixed packets, tagged storage uses360000 known bytes. Compact type-specific arrays need160000 payload bytes but group data by type and lose arbitrary arrival order unless tags/indices are added. The malloc plus void-pointer design uses640000 known descriptor-and-payload bytes and30000 individual allocations; allocator overhead was not measured. Its descriptor is16 bytes because a pointer needs8-byte alignment. Reads remain O(1) after locating an element, but pointer dispatch adds indirection and allocation bookkeeping. All build/read loops are O(n); zero measured read ticks do not prove equal speed. Tagged arrays offer predictable compact records and simpler ownership for the station.')
d.evidence('Task03');d.sources('Task03')
d.chapter('Task04 Bank Structure Forensics')
d.h('Defects and address evidence')
d.p('addInterest takes an account value, modifies only the local copy and returns nothing, so caller balances stay unchanged. p is a pointer, so p.number and p.balance are invalid member expressions; the compiler’s real diagnostic is retained in compile_error.txt. The working evidence program uses valid expressions and prints caller and parameter addresses with %p and void* conversion. Distinct live objects prove the copy; addresses may vary across runs.')
d.code(raw('Task04','address_proof')+raw('Task04','repaired_bank'),8)
d.h('Repair and prevention guideline')
d.p('Use struct account *a and a->balance to update the caller. The observed balances are5200,12480 and832. Pass by value for an independent snapshot or a returned transformed record; pass a pointer for intended caller mutation; pass const struct account * for a read-only view when copying is unnecessary. Const through one pointer does not make all aliases immutable, and pointer lifetime must outlast the call.')
d.h('Alternative Concept and Complexity Analysis')
d.code('list[i] = returned_interest(list[i], 4);',8)
d.p('The account is8 bytes and an account pointer8 bytes on this target. The value-return model conceptually copies2*sizeof(account)=16 bytes per call, versus passing one pointer. This is a source-level model: calling conventions and optimization can eliminate copies. The captured million-call CPU times are shown above, and no general speed ratio is inferred. Both methods take O(1) per fixed record, or O(S) record-copy work versus O(1) pointer passing for a structure of S bytes. Each call uses bounded stack space here; recursion would multiply that per-call cost.')
d.evidence('Task04');d.sources('Task04')
d.chapter('Task05 Hostel Mess Tokens and Storage Classes')
d.h('Four implementations and Complete the Code')
d.code(raw('Task05','complete_the_code')+raw('Task05','counter_four_ways')+raw('Task05','argument_order')+raw('Task05','two_counters'),8)
d.p('The exact supplied main contains auto  : with two spaces before the colon; preserving it cannot also produce the user-requested auto:. The byte fixture follows the immutable main. The combined printf observation is1003 1002 1001 on this run; C leaves argument evaluation order unspecified. Calls execute without interleaving their function bodies, but the output order cannot be assumed. Separate statements make issuance and printing order explicit.')
d.table(['Storage','Scope','Lifetime and initial value','Risk'],[['auto local','Function block','Each call; indeterminate unless initialized','Reinitializing1000 repeats1001; cannot retain state'],['static local','Function block','Whole execution; zero unless initialized, here1000','Hidden state complicates reset, tests and independent instances'],['extern global','External linkage across source files','Whole execution; initialized once to1000','Any authorized file can accidentally modify shared state'],['register loop','Loop block','Automatic; initialized in for','Address may not be taken in C11; compiler need not use a hardware register']])
d.h('Two counter change effort')
d.p('The auto, static and extern models each add one second state cell and one selector parameter, and must select the correct cell. The extern variant’s two cells live in extern_store.c and are linked into two_counters.c. The auto model still resets on every call. The register change affects the loop declaration only and provides no persistent token state. The pointer function body is unchanged when adding the second counter: the caller adds one integer and passes its address. These counts describe state/API modifications, not claimed line-count diffs or measured runtime work.')
d.h('Alternative Concept and Complexity Analysis')
d.p('int next_token(int *counter) increments caller-owned state. Veg and non-veg each start at1000 and independently issue1001,1002. All increment operations take O(1), and each counter uses sizeof(int) storage. A caller-local counter survives for the containing scope; a heap-owned or enclosing object can extend lifetime deliberately. This design makes ownership and reset explicit, supports any number of counters and avoids duplicated hidden statics. Pointer validity and concurrent access must still be managed.')
d.evidence('Task05');d.sources('Task05')
d.chapter('Task06 College Canteen Inventory and Billing')
d.h('Stage 1 Interpret and Testable Rules')
d.p('Items have unique IDs, names, prices in integer paise and a kind. Packaged items have expiry dates; cooked items have preparation times; combos contain one to three existing non-combo item IDs. Repeated component IDs accumulate demand. Sales must have a known ID and positive quantity, must not exceed component stock or use expired packaged stock, and must update all stock and revenue atomically. Warnings include dates zero to two days ahead and distinguish expired items. Revenue summaries must be nonincreasing and reconcile to the daily total.')
d.h('Stage 2 Data Model')
d.p('Canteen owns an array of Item, matching Bill aggregates and the simulated Date. Item nests a tagged union of Date expiry, Time prepared and combo count/IDs. A combo has derived availability from component stock, not an independent physical stock count. Bill records aggregate sales by sold item, so constituent revenue is not counted again.')
d.h('Stage 3 Critical Decisions')
d.p('Build a temporary demand array, validate every required component and only then deduct. Reject nested combos to avoid cycles. Date differences use Gregorian day ordinals with leap-year validation, not integer subtraction of ddmmyyyy. Packaged stock is rejected after expiry; expiry day itself is allowed in this declared application policy. Cooked preparation time is recorded but no unsupported freshness threshold is invented. Canteen state belongs to main and is passed by pointer; helper functions have internal linkage, and no mutable global or persistent static data is necessary for this single-session application. Fixed sample prices and bounded int quantities keep sale products within long long for these experiments.')
d.h('Stage 4 Structures Prototypes and SIMATS Pseudocode')
d.code('int sale(Canteen *canteen, int item_id, int quantity);\nvoid expiry_warning(const Canteen *canteen);\nint find(const Canteen *canteen, int item_id);',8)
d.code('ALGORITHM RECORD SALE\nINPUT: canteen by reference, item ID, positive quantity\nOUTPUT: success or rejection with unchanged state\nBEGIN\n1. FIND requested item; REJECT unknown ID or nonpositive quantity\n2. INITIALIZE every component demand to zero\n3. IF combo THEN ADD quantity for each referenced component\n4. ELSE ADD quantity for the requested stock item\n5. FOR EACH component with demand DO\n6.   IF missing, nested, expired or insufficient THEN RETURN rejection\n7. END FOR\n8. DEDUCT all validated demands\n9. ADD sold quantity and price times quantity to the sold item bill\n10. RETURN success\nEND\n\nALGORITHM WARN EXPIRY\nINPUT: inventory and today\nOUTPUT: near-expiry and expired packaged items\nBEGIN\n1. FOR EACH packaged item DO\n2.   SET days TO ordinal(expiry) minus ordinal(today)\n3.   IF days is negative THEN DISPLAY expired warning\n4.   ELSE IF days is at most two THEN DISPLAY near-expiry warning\n5. END FOR\nEND',8)
d.h('Stage 5 Implementation and Demonstration')
d.code(raw('Task06','canteen_system'),8)
d.p('Three accepted sales total420.00: combo240.00, rice120.00 and juice60.00 in descending revenue order. Five rejected transactions are checked against snapshots and leave all stock/revenue unchanged. The repeated-ingredient TripleJuice combo needs six juices when only five remain and is rejected before deduction. Year-end and leap-February date differences are independently exercised.')
d.h('Alternative Concept and Complexity Analysis')
d.p('For an unsorted array, indexed access is O(1), ID lookup O(n), appending with spare capacity O(1), and middle insertion/removal O(n) due to shifting. A linked list can insert or remove in O(1) once the predecessor/node is already known, but finding an ID or predecessor is O(n); appending is O(1) only with a maintained tail. Every node adds a next pointer, measured8 bytes here, plus possible alignment and allocator overhead. An Item itself is64 bytes. For this small fixed-capacity canteen the array avoids allocation ownership and improves locality. Sale validation is O(n*k) with linear ID lookup and at most three combo components, hence O(n); ranking bill aggregates uses the intended O(n log n) comparison-sort model, though C does not prescribe qsort’s implementation.')
d.evidence('Task06');d.sources('Task06')
d.chapter('Reproduction and Verification');d.code((R/'qa/verification.txt').read_text(),8);d.h('Common support header');d.code((ROOT/'engineering_support/lab.h').read_text());d.p('Reference: supplied CO4_Assignment_4.docx.pdf, Tasks1–6 and mark distribution. Source PDF and extracted text are retained in reference. All real diagnostics, outputs and addresses remain in raw files; images are terminal-style renderings of those records.')
path=d.save();readme(R,4,'Task01 capacity checks and age sorting PASS. Task02 nested/flat sizes160/160; starter44-byte layout PASS. Task03 tagged12-byte packet and actual inactive-member experiment captured. Task04 intentional compile failure, distinct addresses and corrected balances PASS. Task05 multi-file extern and two independent counters PASS; immutable main auto  : spacing is documented. Task06 five atomic rejections and revenue420.00 PASS.');print(path)
