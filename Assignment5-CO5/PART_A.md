# Part A — District Blood Bank Network (25 marks)

## A1 Functional decomposition (7 marks)

The application owns donor and stock collections. Registration validates a candidate before appending it. Eligibility and group search read donor records; stock changes require a mutable stock pointer. Persistence functions own their opened FILE handles, close them on every return path, and report failures. The final report combines eligibility, hospital counts and youngest eligible ID. No mutable global application state is required.

```c
int register_donor(DonorList *list, const DonorRecord *candidate);
int eligible(const DonorRecord *donor, Date today);
size_t find_donors(const DonorRecord *data, size_t n, const char *group, Date today);
int update_stock(Stock *stock, size_t n, const char *group, int delta);
int save_donors(const char *path, const DonorList *list);
int load_donors(const char *path, DonorList *list);
int summarize_out(const DonorRecord *data, size_t n, Date today,
                  size_t *eligible_count, int *youngest_id);
Summary summarize(const DonorRecord *data, size_t n, Date today);
```

Scalar counts, delta and small Date values are copied. const record/list/string pointers borrow read-only data without copying whole arrays. Mutable list and stock pointers deliberately permit updates. summarize_out writes two caller-owned outputs and returns status; Summary {count, youngest_id} returns one cohesive small value, with youngest_id=-1 for none. Both scan O(n), require O(1) extra space and use a deterministic age then ID tie break. Globals can retain the same O(n) runtime/O(n) record storage, but hide dependencies, complicate independent hospitals, tests and concurrency, and require manual resets.

ALGORITHM REGISTER DONOR
INPUT: mutable list, candidate
OUTPUT: success or unchanged list
BEGIN
1. VALIDATE unique ID, bounded name, group, age, phone and date
2. IF invalid THEN RETURN failure
3. CALL APPEND DONOR with list and candidate
4. RETURN append status
END

ALGORITHM ELIGIBILITY SUMMARY
INPUT: read-only donor array, n, today
OUTPUT: eligible count, youngest eligible ID
BEGIN
1. SET count TO zero; SET youngest ID TO minus one
2. FOR each donor DO
3.   IF age is 18 through 65 AND last donation is not in future AND
       ordinal(last donation) plus 90 is at most ordinal(today) plus 7 THEN
4.     INCREMENT count; UPDATE youngest by age then smaller ID
5.   END IF
6. END FOR
7. RETURN both results
END

The 18–65/90-day rule is an explicitly declared assignment simulation, not clinical guidance. Today is 26 November 2026; already eligible donors are included in the next-week report.

## A2 Recursive design (5 marks)

ALGORITHM DIGITAL ROOT
INPUT: nonnegative integer n
OUTPUT: repeated digit sum
BEGIN
1. IF n is less than 10 THEN RETURN n
2. SET sum TO zero
3. WHILE n is positive DO
4.   ADD n modulo 10 TO sum; SET n TO integer quotient n divided by 10
5. END WHILE
6. RETURN DIGITAL ROOT(sum)
END

ALGORITHM HALVING POWER
INPUT: base b, nonnegative exponent n; result representable
OUTPUT: b raised to n
BEGIN
1. IF n equals zero THEN RETURN one
2. SET half TO HALVING POWER(b, integer quotient n divided by two)
3. IF n is odd THEN RETURN half times half times b
4. ELSE RETURN half times half
END

Trace: digital root 9875 -> 29 -> 11 -> 2. Power 2^30 descends 30,15,7,3,1,0 and returns 1,2,8,128,32768,1073741824. Linear calls C(0)=1, C(n)=C(n-1)+1=n+1. Halving calls H(0)=1, H(n)=H(floor(n/2))+1=floor(log2 n)+2 for n>0. Stack follows these depths. Missing n=0 base case causes endless recursion, with negative exponents also requiring rejection before entry. Linear replacement loops n times in O(n) time/O(1) stack. Iterative square-and-multiply uses O(log n) time/O(1) stack. Digital-root digit processing takes O(d) total time for d input digits; recursion depth is number of successive sums, at most O(d). Loop repetition eliminates recursive frames. Formula n=0 ? 0 : 1+(n-1)%9 uses O(1) machine arithmetic and space for a bounded integer (arbitrary-precision input still costs O(d) to read). Define 0^0=1 for this programming exercise.

## A3 Pointers and CLI (5 marks)

For stock={40,25,12,8,30,9,4,15}, p=stock: p+3 addresses element3, with byte displacement 3*sizeof(int); *(p+3) and p[3] both read8. *p++ means *(p++): read40 at old p then advance p to stock+1. One-past pointers may be formed, never dereferenced.

ALGORITHM LOWEST STOCK
INPUT: mutable stock array and count
OUTPUT: pointer into caller array, or null when empty
BEGIN
1. IF count is zero THEN RETURN null
2. SET best TO address of first stock
3. FOR every remaining element DO
4.   IF its stock is lower than stock at best THEN SET best TO its address
5. END FOR
6. RETURN best
END

Prototype: int *lowest_stock(int *stock, size_t n). Caller may decrement *best after validating positivity. Returning the address of a local temporary leaves a dangling pointer after function return; return an address in the caller's live array instead. An index-returning alternative uses size_t, SIZE_MAX for empty, then stock[index] for updates. Both require O(n) time/O(1) space; a successful realloc invalidates old element pointers, whereas an index can be applied to the new base after checking bounds/order are unchanged.

CLI: bloodbank find O+ has argc3; bloodbank issue A- 2 has argc4. Check argument count before argv access, group against eight allowed names, and strtol end pointer/errno/range/positivity before any file modification. Reject all other combinations with usage and nonzero status. Names use bounded fgets and drain/reject excess characters. A register extension accepts group and reads the full name from stdin.

## A4 Dynamic memory (4 marks)

ALGORITHM APPEND DONOR
INPUT: mutable list with data, size, capacity; donor
OUTPUT: success or unchanged list on allocation failure
BEGIN
1. IF size equals capacity THEN
2.   SET new capacity TO two when capacity is zero, otherwise twice capacity
3.   IF multiplication or byte size would overflow THEN RETURN failure
4.   SET temporary TO REALLOCATE(data, new capacity times record size)
5.   IF temporary is null THEN RETURN failure
6.   SET data TO temporary; SET capacity TO new capacity
7. END IF
8. COPY donor INTO data[size]; INCREMENT size; RETURN success
END

Leak: assigning realloc directly to data loses the old donor allocation on failure; use the temporary. Dangling pointer: retaining &data[i] across realloc can refer to freed storage; retain an index and reacquire. Double free: two hospital views both freeing borrowed donor storage corrupt the allocator; one list owns data, views borrow it, and cleanup frees once then resets pointer/size/capacity. A failure must leave the old allocation owned and usable.

Fixed +10 growth may relocate 10+20+...+n records, O(n^2), while doubling relocation upper bound is 2+4+...<2n, O(n) overall and O(1) amortized append. These are conceptual worst-case copies; realloc can extend in place. +10 leaves at most9 unused slots after an append; doubling leaves fewer than n unused live slots (up to nearly half capacity), trading space for fewer growth calls.

## A5 Persistence (4 marks)

Donor text lines written with fprintf are inspectable/exportable, using delimited bounded fields and explicit dates. Validate delimiters and line lengths. Stock uses fixed binary records with fwrite for direct access; small eight-group tables remain easy to validate. Raw struct binary is local-ABI storage: padding, int sizes, endianness and schema changes prevent unqualified cross-platform exchange. A portable binary format would serialize fixed-width fields in a specified byte order with a version header.

ALGORITHM UPDATE BINARY STOCK
INPUT: open read/write binary file, nonnegative index, units
OUTPUT: success or failure
BEGIN
1. VALIDATE index, units and representable byte offset
2. SEEK TO index times record size FROM file start; IF failure RETURN failure
3. READ one record; IF not one record RETURN failure
4. CHANGE units in the local record
5. SEEK BACK by one record FROM current position; IF failure RETURN failure
6. WRITE one record; CHECK write and flush status; RETURN success only if both succeed
END

The intervening seek also satisfies update-stream read/write sequencing. A beyond-end read fails before writing. Variable-width text (8 becoming100) shifts later bytes, so generally read each record, change the matching one, write a new temporary text file, close/check it, then replace the original on success. This is O(n) work and O(n) replacement disk space versus O(1) record I/O and O(1) extra RAM for a known binary index. Text can be smaller for short fields; raw padded binary has size n*sizeof(record), so measurements rather than assumptions decide size. Neither direct fwrite nor rename alone guarantees crash-durable transactions; production needs locking and recovery.
