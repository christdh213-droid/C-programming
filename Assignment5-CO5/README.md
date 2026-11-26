# CSA02 Assignment5 CO5

Chris Abraham George | 1911260256 | SIMATS Engineering | B.E / B.Tech CSE  
CSA02 C Programming | 50 marks | [Repository](https://github.com/christdh213-droid/C-programming)

## Exact detected compiler

```text
gcc.exe (Rev4, Built by MSYS2 project) 16.2.0
Copyright (C) 2026 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

## Reproduce from the repository root

```text
python engineering_support/execute.py 5 TaskB1
python Assignment5-CO5/probe_b1.py
python engineering_support/execute.py 5 TaskB2
python Assignment5-CO5/probe_b2.py
python engineering_support/execute.py 5 TaskB3
python engineering_support/execute.py 5 TaskB4
python Assignment5-CO5/probe_b4.py
```

The runner sets the installed GCC PATH, compiles with zero diagnostics, captures exact stdout/stderr, and checks byte fixtures. Run B3 before B4. B3 data directory is retained; B2 init resets stock; valid-name registration appends to its demonstration log. Stress and unsafe cases run in separate children with bounded waits and recorded exit codes. Do not run the unsafe child in a production process.

Exact successful C compilation commands (working directory Assignment5-CO5):

```text
gcc -std=c11 -Wall -Wextra TaskB1/complete_the_code.c -o build/TaskB1_complete_the_code.exe
gcc -std=c11 -Wall -Wextra TaskB1/recursion_lab.c -o build/TaskB1_recursion_lab.exe
gcc -std=c11 -Wall -Wextra TaskB1/stack_limit.c -o build/TaskB1_stack_limit.exe
gcc -std=c11 -Wall -Wextra TaskB2/adversarial_scanf_demo.c -o build/TaskB2_adversarial_scanf_demo.exe
gcc -std=c11 -Wall -Wextra TaskB2/bloodbank_cli.c -o build/TaskB2_bloodbank_cli.exe
gcc -std=c11 -Wall -Wextra TaskB3/complete_the_code.c -o build/TaskB3_complete_the_code.exe
gcc -std=c11 -Wall -Wextra TaskB3/file_benchmark.c -o build/TaskB3_file_benchmark.exe
gcc -std=c11 -Wall -Wextra TaskB4/complete_the_code.c -o build/TaskB4_complete_the_code.exe
gcc -std=c11 -Wall -Wextra TaskB4/nightly_report.c -o build/TaskB4_nightly_report.exe -lpsapi
```

Representative manual runs (same assignment working directory; use cmd.exe for `<`):

```text
build/TaskB1_complete_the_code.exe
build/TaskB1_recursion_lab.exe
build/TaskB1_stack_limit.exe iterative 64000
build/TaskB2_adversarial_scanf_demo.exe < TaskB2/inputs/overlong.txt
build/TaskB2_bloodbank_cli.exe find O+
build/TaskB2_bloodbank_cli.exe issue A- 2
build/TaskB2_bloodbank_cli.exe register O+ < TaskB2/inputs/name.txt
build/TaskB3_complete_the_code.exe
build/TaskB3_file_benchmark.exe
build/TaskB4_complete_the_code.exe
build/TaskB4_nightly_report.exe
build/TaskB4_nightly_report.exe stream
```

## Results and limits

- B1: all value tests pass; linear/halving counts match recurrences. First failing sweep exponent64000 returned0xC00000FD, iterative64000 and128000 succeeded. This is not the smallest crash threshold. Literal duplicate-halves gives63 calls; odd-decrement variant gives the requested61.
- B2: all16 adversarial CLI cases match expected statuses. Safe fgets truncates/drains, CLI rejects oversized names. Native unbounded scanf child returned0xC0000005; this is not sanitizer evidence.
- B3:10-record round trips and1000/10000/100000 datasets pass field checks. Sizes and clock-derived write/read/update/bulk measurements are in raw outputs. The text fixture is smaller than88-byte fixed records; bulk single-call writing was slower in this one run, so no universal speed ranking is claimed.
- B4:100000 donors/25 hospitals give67047 eligible, youngest ID7001, identical25 hospital totals. In-memory runtime0.021000000s and peak18104320 bytes; batch256 runtime0.011000000s and peak5099520 bytes. These are separate-process local measurements. Doubling uses17 growth calls, capacity131072. Injected allocation failure preserves the old owner and contents.
- **Sanitizer/Valgrind requirement remains unverified.** Actual GCC `-fsanitize=address` and `-fsanitize=address,leak` link attempts fail: `cannot find -lasan`. Valgrind is absent. No zero-leak claim is made. B2/B4 retain verbatim failure transcripts; repeat on a supported toolchain to close this gap.
- All three starter outputs pass exact bytes. Preserve B1 `fast  :` and B3 trailing space from immutable main despite conflicting shortened examples in the request.
- Runtime fields labelled cpu in B3 are raw C clock()-derived seconds, implementation-dependent on Windows. Timings are single-run and include documented I/O/verification costs; cache effects and resolution remain.
- Eligibility is an assignment model: age18..65,90-day interval ending by end of next7 days, simulated26Nov2026; not clinical guidance.

## Report and evidence

`CSA02_1911260256_Assignment5_Report.docx` includes PartA algorithms/prototypes,300DPI diagrams/charts, complete C sources, measurements and real-output terminal renderings. `PART_A.md` is the design source. Section and Submission Date cover fields are blank.

`qa/verification.txt` checks immutable starter structure, exact output bytes, compiler logs, SHA256 records, file sizes, all CLI statuses, observed stack status and an independent Python eligibility calculation. `qa/screenshots.json` records300DPI image dimensions/nonblank checks and complete transcript-line coverage. Images are terminal-style renderings from real transcripts, not OS-window captures.

Generate the Word report using a Python environment with python-docx, Pillow and matplotlib: `python Assignment5-CO5/build_report.py`. In PowerShell 7 render with `& ./engineering_support/render_report.ps1 -Number 5`, then audit with `python engineering_support/audit_report.py 5`. The rendering script requires PowerShell 7 because legacy Windows PowerShell stalled in Word COM export here. The Word rendering step uses installed Microsoft Word; the rendered PDF/pages are local QA artifacts.
