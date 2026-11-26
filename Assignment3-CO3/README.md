# CSA02 Assignment 3 CO3

Student A: Chris Abraham George | Register No: 1911260256  
SIMATS Engineering | B.E / B.Tech CSE | Pair Work | 50 marks  
Repository: https://github.com/christdh213-droid/C-programming

Student B name/register/repository, Section and Submission Date are blank in the report.
The role-labelled sections and contribution table cover the prescribed Student A, Student B and joint responsibilities.

## Detected compiler

```text
gcc (Rev4, Built by MSYS2 project) 16.2.0
Copyright (C) 2026 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

## Compile, execute and verify

```powershell
python run_all.py
python verify.py
```

Every final C source compiles with `-std=c11 -O2 -Wall -Wextra`, with zero warnings.
The runner creates `build/`, preserves byte-exact stdout/stderr, records actual commands and SHA-256 hashes,
rejects failed runs/diagnostics, and compares starter outputs including trailing spaces and CRLF.
For manual `<` input redirection use cmd.exe or another supporting shell; the runner works directly in PowerShell.

### Exact commands recorded from execution

```text
gcc -std=c11 -O2 -Wall -Wextra Q1/complete_the_code.c -o build/Q1_complete_the_code.exe
build/Q1_complete_the_code.exe < Q1/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q1/library_search_lab.c -o build/Q1_library_search_lab.exe
build/Q1_library_search_lab.exe < Q1/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q2/seating_sort_lab.c -o build/Q2_seating_sort_lab.exe
build/Q2_seating_sort_lab.exe < Q2/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q3/complete_the_code.c -o build/Q3_complete_the_code.exe
build/Q3_complete_the_code.exe < Q3/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q3/merit_merge_lab.c -o build/Q3_merit_merge_lab.exe
build/Q3_merit_merge_lab.exe < Q3/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q3/starter_extra_tests.c -o build/Q3_starter_extra_tests.exe
build/Q3_starter_extra_tests.exe < Q3/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q4/rainfall_lab.c -o build/Q4_rainfall_lab.exe
build/Q4_rainfall_lab.exe < Q4/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q5/complete_the_code.c -o build/Q5_complete_the_code.exe
build/Q5_complete_the_code.exe < Q5/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q5/sms_analyser_lab.c -o build/Q5_sms_analyser_lab.exe
build/Q5_sms_analyser_lab.exe < Q5/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q5/starter_extra_tests.c -o build/Q5_starter_extra_tests.exe
build/Q5_starter_extra_tests.exe < Q5/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q6/hostel_directory_lab.c -o build/Q6_hostel_directory_lab.exe
build/Q6_hostel_directory_lab.exe < Q6/input.txt
gcc -std=c11 -O2 -Wall -Wextra Q7/election_lab.c -o build/Q7_election_lab.exe
build/Q7_election_lab.exe < Q7/input.txt
```

## Results and evidence

- Q1: exact binary-search starter PASS. 48 measured search rows cover 1000/10000/100000 entries, first/middle/last/missing keys, linear, binary, hash and interpolation. Binary worst observed 17; successful mean 15.689460 at 100000. Hash collisions are tested explicitly.
- Q2: 6-element traces plus 52 benchmark rows cover 4 sorts, 4 orders, 3 sizes and 20 late entries. Late-entry insertion takes 11499 comparisons vs bubble 519500 and selection 519690. Counting sort uses the known small integer range.
- Q3: exact starter and separate empty-list driver PASS. Campus A wins equal-score ties. At 10000 per campus, merge uses 19999 comparisons/20000 writes; simple in-place merge makes 50004999 record writes. qsort internal moves are NA, not invented.
- Q4: hand 3x4 and full 38x12 data verified. Separate functions implement all 4 computations. Actual CPU timings compare 2000x2000 traversal and 2D/flat/separate-row storage; pointer overhead is 304 bytes on this target.
- Q5: exact starter PASS, tab-separated extra test PASS; manual/library outputs agree. Safe truncation is executed; overflowing strcpy is explained but never executed. Real strlen calls through a volatile function pointer demonstrate repeated vs cached length. Recursive depths are recorded.
- Q6: direct/index insertion use equal comparison counts; index and pointer views copy no name characters. At 5000 names direct sorting copies 79476320 characters including NUL. Length29 fits, length30 is flagged and drained. Present/missing search counts and case-insensitive duplicates are recorded.
- Q7: the hand tally gives 2,2,1; valid5/invalid3; tie1/2. All three methods agree for 5000/500000 votes and 12/500 candidates. Count-array visits are exactly v; generated dataset totals and linear-name comparison counts are independently checked.

All raw outputs are in Q*/outputs. All source files, including the exact starter completions, are listed in the Word report.
Each task has input.txt and paginated 300-DPI dark-terminal transcript renderings, derived directly from captured commands and output.
Tabs use eight-column terminal stops; raw bytes remain authoritative. Screenshots are renderings of execution records, not OS-window photographs.
The six charts in charts/ read qa/data.json parsed from real output; CSV tables accompany them.

## Timing and count definitions

clock() measures process CPU seconds with CLOCKS_PER_SEC=1000 here. Values of 0.000000000 are real zero-tick observations,
not proof of zero work or a portable speedup. Q1 rows report batch CPU time and their own repetition count; other timings are single captured algorithm runs or explicitly labelled traversals.
Counts measure instrumented source-level operations. qsort comparator counts are observable; internal swaps and storage are not.
Binary-search steps count midpoint visits, as required by the supplied expected output, rather than every primitive == and <.
The standard C library does not prescribe qsort's algorithm; its O(n log n) discussion is the intended comparison-sort model.

## Files

- `CSA02_1911260256_Assignment3_Report.docx`: final role-labelled report with complete code, tables, charts and execution images.
- `PREDICTIONS.md`: committed before experiments.
- `qa/verification.txt`, `qa/data.json`: independent checks and parsed raw measurements.
- `qa/screenshots.json`: dimensions, DPI and exact transcript-line coverage.
- `complete_starters.py`: optional helper rebuilding TODO completions from the retained PDF text.
- `build_report.py`: artifact builder requiring python-docx, Pillow and matplotlib.
- `reference/`: supplied PDF and extracted text.

To regenerate artifacts after execution: `python verify.py`, then `python build_report.py` with those packages installed.
The workspace's bundled Python includes these dependencies. Rendering for visual QA used Microsoft Word read-only PDF export because bundled LibreOffice is unavailable on this Windows runtime.

The Student B sections describe the prescribed role's design and evidence; no unnamed partner's identity or independent execution is attested.
