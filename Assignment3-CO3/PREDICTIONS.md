# Predictions before execution

Q1: the starter visits 3,3,4,4 midpoints. Linear search best 1, worst n, uniform successful mean (n+1)/2. Binary worst floor(log2(n))+1: 17 for 100000. Uniform generated keys favour interpolation; hash load <0.5 should keep probes low, but neither has a general worst-case guarantee better than O(n).

Q2: for sorted n, early-exit bubble and insertion use n-1 key comparisons, selection n(n-1)/2. Reverse data maximizes bubble swaps and insertion shifts to n(n-1)/2. Input 6,2,5,1,4,3 should end 1,2,3,4,5,6. Late registrations should favour insertion over the quadratic selection scan; counting sort benefits from a small key range.

Q3: descending stable merge of the starter lists is 98,95,91(A),91(B),85,80,72. Empty input copies the other list. For m=n and interleaved inputs, merge uses 2n-1 comparisons; simple in-place shifting can be quadratic. All-equal merge places A before B.

Q4: hand data rows (10,20,30,40), (0,0,0,0), (20,30,40,50) give annual totals 100,0,140; monthly averages 10,16.6666667,23.3333333,30; maximum row2 month3 =50; mean annual80 and deficient threshold48, only row1 deficient (zero-based). Row traversal should usually beat column traversal for the large contiguous array, but measured CPU times determine the result.

Q5: the starter yields Words: 7 and palindrome flags 1 0. Space-only separators would count a tab-separated pair as one word; choosing isspace in the TODO counts two. A repeated non-hoisted length scan performs quadratic work; cached length and two-pointer reversal are linear. Punctuation is retained in uppercase/reverse but ignored for palindrome comparison.

Q6: index and pointer sorting should remove whole-string copies. strcmp may inspect up to L characters; case-insensitive comparison should group Apple/apple. A capacity30 fgets buffer stores 29 characters plus NUL; a length30 line requires draining one remaining character before the next input. Count and report stored characters and truncation separately.

Q7: votes [1,2,2,3,1,0,-1,4] with c=3 give counts2,2,1; valid5 invalid3; tie between1 and2. One-pass counting visits exactly v votes. Linear candidate-name lookup grows with c; sort-and-count adds comparison sorting. Large timings will be actual clock() values, not predicted speedups.
