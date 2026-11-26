# CSA02 Assignment 2 CO2

Chris Abraham George | Register number 1911260256  
SIMATS Engineering | B.E / B.Tech CSE  
Course: CSA02 C Programming | Maximum marks: 50

Repository link: https://github.com/christdh213-droid/C-programming

## Environment

Detected compiler (not a hardcoded requirement):

```text
gcc.exe (Rev4, Built by MSYS2 project) 16.2.0
Copyright (C) 2026 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

git version 2.56.0.windows.2; Python 3.13.15.

## Reproduce all programs

From this directory with gcc and Python on PATH:

```powershell
python run_all.py
python verify.py
```

All final C programs use `-std=c11 -Wall -Wextra`; Q6 additionally uses `-lm`.
Only Q1/ub_demo.c intentionally emits a real `-Wsequence-point` warning, compiled with `-std=c11 -Wall`.
The runner rejects any unexpected compiler diagnostic, failed run or expected-output mismatch.
It preserves stdout/stderr bytes without newline normalization and writes the actual commands and hashes.
No timings are claimed. Counts refer to source-level operations.

## Exact compile and run commands

The runner creates `build/` first. The following commands are recorded from actual runs.
For manual input redirection use a shell supporting `<`, such as `cmd.exe`; the Python runner works directly from PowerShell.

```text
gcc -std=c11 -Wall -Wextra Q1/billing.c -o build/Q1_billing.exe
build/Q1_billing.exe < Q1/inputs/billing.txt
gcc -std=c11 -Wall Q1/ub_demo.c -o build/Q1_ub_demo.exe
build/Q1_ub_demo.exe < Q1/inputs/ub_demo.txt
gcc -std=c11 -Wall -Wextra Q2/concession.c -o build/Q2_concession.exe
build/Q2_concession.exe < Q2/inputs/concession.txt
gcc -std=c11 -Wall -Wextra Q3/complete.c -o build/Q3_complete.exe
build/Q3_complete.exe < Q3/inputs/complete.txt
gcc -std=c11 -Wall -Wextra Q3/register_compare.c -o build/Q3_register_compare.exe
build/Q3_register_compare.exe < Q3/inputs/register_compare.txt
gcc -std=c11 -Wall -Wextra Q4/classifiers.c -o build/Q4_classifiers.exe
build/Q4_classifiers.exe < Q4/inputs/classifiers.txt
gcc -std=c11 -Wall -Wextra Q4/complete.c -o build/Q4_complete.exe
build/Q4_complete.exe < Q4/inputs/complete.txt
gcc -std=c11 -Wall -Wextra Q4/fallthrough.c -o build/Q4_fallthrough.exe
build/Q4_fallthrough.exe < Q4/inputs/fallthrough.txt
gcc -std=c11 -Wall -Wextra Q5/complete.c -o build/Q5_complete.exe
build/Q5_complete.exe < Q5/inputs/complete.txt
gcc -std=c11 -Wall -Wextra Q5/loops_sieve.c -o build/Q5_loops_sieve.exe
build/Q5_loops_sieve.exe < Q5/inputs/loops_sieve.txt
gcc -std=c11 -Wall -Wextra Q5/naive_complete.c -o build/Q5_naive_complete.exe
build/Q5_naive_complete.exe < Q5/inputs/naive_complete.txt
gcc -std=c11 -Wall -Wextra Q6/loan.c -o build/Q6_loan.exe -lm
build/Q6_loan.exe < Q6/inputs/loan.txt
gcc -std=c11 -Wall -Wextra Q7/redesign.c -o build/Q7_redesign.exe
build/Q7_redesign.exe < Q7/inputs/redesign.txt
```

## Results

- Q1: original bill totals/nets agree with precommitted predictions; discounted-base GST corrects senior bills. Integer truncation and real undefined-behaviour diagnostics are analysed.
- Q2: 333 concessions for all five orders; 750 verifier calls for cheap-first/nested if versus 1000 for server-first/eager/full audit. The audit output covers all 1000 passenger IDs.
- Q3: starter output matches exactly; bit and byte-array operations agree; states use 1 versus 8 bytes per home on the detected target.
- Q4: 22 boundary inputs and all 301 integers -100..200 agree across ladder, switch and table. Missing return changes the S results to A. Scholarship thresholds are explicit experimental policy, since the assignment gives no numeric income bands.
- Q5: modulo counts for 1000003 fall from 1000001 to 999. All four loop variants agree with the sieve over 0..10000. Safe conditions additionally count quotient divisions. The sieve performs 2122051 marking visits in 1000004 bytes and finds 78499 primes.
- Q6: six-month hand schedule matches independent Decimal arithmetic; interest Rs 645.38226624. A Rs 200.01 repayment hits the 360-month cap; the formula predicts 501 months. Rs 200 or less is rejected as non amortizing.
- Q7: total divisions on 1000003 drop 1999 -> 501 (74.937%). Validation agrees with the sieve for all 1000004 values 0..1000003; original/revised also agree over 0..10000.

## Starter fidelity and the Q5 printed-output discrepancy

Q3, Q4 and Q5 retain the PDF starter in `starter.txt`. Only TODO blocks receive code; `main()` is identical.
Fixtures compare actual bytes, including Q4's trailing space and Windows CRLF line endings.
Q5 uses the overflow-safe equivalent `i <= n / i` to implement the mathematical `i*i <= n` condition.
The PDF's displayed expected block has inconsistent leading whitespace for 97 and 1000003 relative to its own `%8lu` format.
The exact main is preserved, and the fixture follows that format: six leading spaces for 97, five for 100, four for 7919 and one for 1000003.
The report documents the literal printed-block mismatch; no output has been modified to hide it.

## Files and evidence

- `Q1/` through `Q7/`: C sources, input files, expected fixtures where applicable, raw output files, compilation diagnostics, command transcripts, execution manifests and 300 DPI transcript images.
- `PREDICTIONS.md`: predictions committed before execution.
- `charts/`: charts generated from raw measured values.
- `qa/verification.txt`: independent checks; `qa/screenshots.json`: dimensions, nonblank checks and line coverage.
- `CSA02_1911260256_Assignment2_Report.docx`: complete report, analysis, measurements, screenshots and final source listings.
- `reference/`: supplied assignment and extracted text.
- `author_tasks.py`: source materialization helper (requires pypdf, only needed to regenerate sources from the reference PDF).
- `build_report.py`: creates screenshot renderings, charts, README and Word report (requires Pillow, matplotlib, python-docx).

Transcript images are rendered from captured execution records, not photographs of an OS terminal window. Long transcripts are paginated without omitting lines. Complete raw outputs remain authoritative.

## Git and submission

This directory is Assignment 2 within the combined C-programming repository; its earlier progressive Git history is retained.
Use `git log --oneline --reverse` to inspect progressive setup, task and final-documentation commits.
The report cover now points to the combined C-programming GitHub repository.
The combined repository uses the configured origin at https://github.com/christdh213-droid/C-programming.git; push from the repository root and grant faculty access as required.
The cover leaves Section and Submission Date blank.
