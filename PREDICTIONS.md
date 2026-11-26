# Predictions recorded before execution

Q1 uses integer price, quantity and senior for the original expression. Bills (99,3,1), (500,2,0), (1200,1,1) predict total/net of 267/267, 1050/1000, 1080/1030. Left associative multiplication/division truncates discount and GST separately. Corrected GST is applied after the senior discount: net 265.0725, 1000, 1021. No defined prediction is possible for count = count++ + 1.

Q2 dataset: age 60+(i%3==0), eligible (i%4!=0), disability (i%10==0), i=0..999. Senior-and-eligible passengers bypass verification in the cheap-first OR. Server-first and eager evaluation call the verifier 1000 times. Nested if should equal cheap-first.

Q3 starter state after initialization 0, light on 1, AC on 5, show 5, fan toggle 7, light off 6, show 6, printf 6. Experimental sequence sets bit 7 (128), sets bit 0 (129), toggles bit 7 (1), clears bit 0 (0).

Q4 boundaries: -1 and 101 invalid; 0 F; 49 F; 50 D; 59 D; 60 C; 69 C; 70 B; 79 B; 80 A; 89 A; 90 S; 100 S. Removing case 10's return makes 100 fall through to the A return if case 9 is likewise grouped with 10.

Q5 prime division counts: 97 -> naive 95, sqrt 8; 100 -> 1 and 1; 7919 -> 7917 and 87; 1000003 -> 1000001 and 999. All loop variants agree. n=2,3 need no trial division. Unsigned 32-bit 65536 squared wraps to 0.

Q6 unrounded hand recurrence Bnext=1.02B-payment: balances after payments of 2000 are 8200, 6364, 4491.28, 2581.1056, 632.727712, 0. Final payment 645.38226624; interest 645.38226624, six months. As payment approaches 200 from above, months grow; payment at or below 200 cannot amortize a 10000 loan at 2%. A 360-month cap should stop unresolved cases explicitly.

Q7 objective: at least halve ALL counted integer divisions for primes 7919 and 1000003 versus Q5's sqrt loop. Testing 2,3 and candidates 6k-1,6k+1 should reduce modulo attempts roughly two thirds; count loop-condition quotient divisions as well to avoid hiding work. Constant auxiliary storage; small composites may not improve.
