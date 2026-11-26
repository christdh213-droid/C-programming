# CSA02 Assignment 4 CO4

Chris Abraham George | Register Number 1911260256  
SIMATS Engineering | B.E / B.Tech CSE | CSA02 C Programming | 50 Marks  
Repository: https://github.com/christdh213-droid/C-programming

## Exact detected GCC version

```text
gcc.exe (Rev4, Built by MSYS2 project) 16.2.0
Copyright (C) 2026 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

## Reproduction

From the repository root use `python engineering_support/execute.py 4 TASK_NAME` for each task.
All C compilations use `-std=c11 -Wall -Wextra`. Inputs, exact stdout/stderr, compiler logs and manifests are retained per task.
Intentional compile failures and isolated stress/sanitizer probes are separately labelled. Zero measured CPU ticks stay zero.
For manual `<` redirection, use cmd.exe or another supporting shell; the Python runner works from PowerShell.

```text
gcc -std=c11 -Wall -Wextra Task01/patient_register.c -o build/Task01_patient_register.exe
build/Task01_patient_register.exe < Task01/input.txt
gcc -std=c11 -Wall -Wextra Task02/complete_the_code.c -o build/Task02_complete_the_code.exe
build/Task02_complete_the_code.exe < Task02/input.txt
gcc -std=c11 -Wall -Wextra Task02/courier_full.c -o build/Task02_courier_full.exe
build/Task02_courier_full.exe < Task02/input.txt
gcc -std=c11 -Wall -Wextra Task02/starter_layout.c -o build/Task02_starter_layout.exe
build/Task02_starter_layout.exe < Task02/input.txt
gcc -std=c11 -Wall -Wextra Task03/complete_the_code.c -o build/Task03_complete_the_code.exe
build/Task03_complete_the_code.exe < Task03/input.txt
gcc -std=c11 -Wall -Wextra Task03/weather_lab.c -o build/Task03_weather_lab.exe
build/Task03_weather_lab.exe < Task03/input.txt
gcc -std=c11 -Wall -Wextra Task04/address_proof.c -o build/Task04_address_proof.exe
build/Task04_address_proof.exe < Task04/input.txt
gcc -std=c11 -Wall -Wextra Task04/forensics_bug.c -o build/Task04_forensics_bug.exe
gcc -std=c11 -Wall -Wextra Task04/repaired_bank.c -o build/Task04_repaired_bank.exe
build/Task04_repaired_bank.exe < Task04/input.txt
gcc -std=c11 -Wall -Wextra Task05/argument_order.c -o build/Task05_argument_order.exe
build/Task05_argument_order.exe < Task05/input.txt
gcc -std=c11 -Wall -Wextra Task05/complete_the_code.c -o build/Task05_complete_the_code.exe
build/Task05_complete_the_code.exe < Task05/input.txt
gcc -std=c11 -Wall -Wextra Task05/counter_four_ways.c Task05/extern_store.c -o build/Task05_counter_four_ways.exe
build/Task05_counter_four_ways.exe < Task05/input.txt
gcc -std=c11 -Wall -Wextra Task05/extern_store.c -c -o build/Task05_extern_store.o
gcc -std=c11 -Wall -Wextra Task05/two_counters.c Task05/extern_store.c -o build/Task05_two_counters.exe
build/Task05_two_counters.exe < Task05/input.txt
gcc -std=c11 -Wall -Wextra Task06/canteen_system.c -o build/Task06_canteen_system.exe
build/Task06_canteen_system.exe < Task06/input.txt
```

## Results

Task01 capacity checks and age sorting PASS. Task02 nested/flat sizes160/160; starter44-byte layout PASS. Task03 tagged12-byte packet and actual inactive-member experiment captured. Task04 intentional compile failure, distinct addresses and corrected balances PASS. Task05 multi-file extern and two independent counters PASS; immutable main auto  : spacing is documented. Task06 five atomic rejections and revenue420.00 PASS.

## Evidence

- The Word report contains the full analysis, pseudocode, source code, measured tables and execution images.
- `qa/verification.txt` records independent checks; `qa/screenshots.json` records image dimensions, DPI and transcript-line coverage.
- Transcript images are 300-DPI dark-terminal renderings of actual captured commands/output, not OS-window photographs. Raw bytes remain authoritative.
- Complete-the-Code starters are preserved in `starter.txt`; only TODO blocks were filled. Fixtures include exact spaces and Windows CRLF.
- Cover Section and Submission Date fields are blank. The linked GitHub repository contains progressive task commits.
