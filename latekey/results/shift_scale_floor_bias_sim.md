# Floor-misspecification simulation

300 replicates per row. Truth: key-first c' + (1 − c') σ(1.2 (6 − d)), 100 pairs per depth; the analysis is told the floor is 0.05, and the true plateau c' is either 0.05 (correct) or 0.20 (accuracy levels off above the assumed floor).

| truth | true plateau | depths | floor fixed: median LL(shift) − LL(scale) | floor fixed: share picking the truth | floor estimated: median | floor estimated: share picking the truth |
|---|---|---|---|---|---|---|
| shift, Δ = 1.2 | 0.05 | 2–12 (key-first reaches the plateau) | +2.04 | 0.84 | +2.05 | 0.84 |
| shift, Δ = 1.2 | 0.05 | 2–6 (key-first stays high) | +1.18 | 0.75 | +0.73 | 0.70 |
| shift, Δ = 1.2 | 0.20 | 2–12 (key-first reaches the plateau) | +4.13 | 0.99 | +1.31 | 0.79 |
| shift, Δ = 1.2 | 0.20 | 2–6 (key-first stays high) | +1.50 | 0.85 | +0.52 | 0.69 |
| scale, r = 1.2 | 0.05 | 2–12 (key-first reaches the plateau) | -1.22 | 0.78 | -1.21 | 0.77 |
| scale, r = 1.2 | 0.05 | 2–6 (key-first stays high) | -0.68 | 0.70 | -0.75 | 0.76 |
| scale, r = 1.2 | 0.20 | 2–12 (key-first reaches the plateau) | +1.55 | 0.16 | -0.83 | 0.73 |
| scale, r = 1.2 | 0.20 | 2–6 (key-first stays high) | -0.13 | 0.53 | -0.56 | 0.74 |
