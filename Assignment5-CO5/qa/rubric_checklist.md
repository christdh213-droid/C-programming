# Rubric evidence map

| Component | Evidence | Status |
| --- | --- | --- |
| A1 decomposition, prototypes, two returns, globals | PART_A.md; report; a1_structure_chart.png | Covered |
| A2 algorithms, traces, recurrences, stack, alternatives | PART_A.md; report; a2_call_stack.png | Covered |
| A3 pointer expressions, lowest element, CLI, index alternative | PART_A.md; executed pointer case; a3_pointer_memory.png | Covered |
| A4 doubling, temporary pointer, memory errors, +10 growth | PART_A.md; TaskB4 injected failure | Covered |
| A5 text/binary, in-place algorithm, text rewrite | PART_A.md; TaskB3 runs | Covered |
| B1 values, call counts, actual crash, iterative repeat | TaskB1 outputs; b1_recursion_calls.png | PASS |
| B2 adversarial inputs, files, CLI validation | TaskB2 outputs/adversarial_cases.json | 16 expected statuses PASS |
| B2 unsafe scanf native child | TaskB2 outputs/unsafe_native.transcript.txt | Observed access violation; not ASan evidence |
| B2 ASan/Valgrind | TaskB2 outputs/sanitizer_probe.transcript.txt | UNAVAILABLE: missing libasan; requirement not fulfilled |
| B3 round trips, three sizes, update, bulk comparison | TaskB3 outputs and retained data; b3_text_vs_binary.png | PASS |
| B4 100000 donors,25 hospitals, runtime/RAM/growth, decision | TaskB4 outputs; independent Python verification | PASS |
| B4 ASan/Valgrind clean leak check | TaskB4 outputs/sanitizer_probe.transcript.txt | UNAVAILABLE: missing libasan; requirement not fulfilled |
| Three immutable starter completions | starters, fixtures, manifests; verification.txt | Exact bytes PASS |
| Report/readme/screenshots | Word report, README.md, artifact_audit.json | Rendered and visually reviewed |

Requested B1 spacing/count contradictions are documented: immutable main prints `fast  :`; literal duplicate-half recursion measures63, while the additional odd-decrement variant measures61. No measured value was altered to match an inconsistent example.
