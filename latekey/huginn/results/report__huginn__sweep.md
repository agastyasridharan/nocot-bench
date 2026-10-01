# Huginn loop sweep: sweep

Source: latekey/huginn/results/runs/huginn__sweep.jsonl. Rows: 47600. Bootstrap: 1000 pair resamples. Depth: `dependent_depth`. Default crossing level: floor-adjusted midpoint c + (1-c)/2. Core grid for the slope tests: [4, 8, 16, 32, 64].

Penalty metrics (key-last vs key-first, `both` model): crossing ratio kf/kl (> 1 = key-last crosses shallower), Δ_m (centred gap at the median depth d_m; > 0 = key-last shifted shallower), r (> 1 = key-last pays more per step). **Prediction if the penalty reflects serial depth after the key: all three shrink with N (negative slopes on log N), and the kl:dep:logN coefficient of the continuous regression is positive.**

## Condition: full

### Key-first accuracy by num_steps (all depths)

| bank | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 | N=64 |
|---|---|---|---|---|---|---|---|
| brew | 0.278 | 0.249 | 0.268 | 0.454 | 0.486 | 0.491 | 0.487 |
| cfgpatch | 0.092 | 0.107 | 0.072 | 0.195 | 0.261 | 0.258 | 0.255 |
| chain | 0.054 | 0.108 | 0.134 | 0.269 | 0.344 | 0.338 | 0.343 |
| ordertrack | 0.207 | 0.203 | 0.328 | 0.570 | 0.470 | 0.465 | 0.461 |

### Accuracy by depth (kf / kl)

**brew** (floor 0.333)

| N | d=1 | d=2 | d=3 | d=4 |
|---|---|---|---|---|
| 1 | 0.26 / 0.25 | 0.30 / 0.29 | 0.28 / 0.25 | 0.27 / 0.27 |
| 2 | 0.23 / 0.24 | 0.24 / 0.21 | 0.24 / 0.20 | 0.28 / 0.20 |
| 4 | 0.26 / 0.25 | 0.32 / 0.23 | 0.24 / 0.19 | 0.26 / 0.23 |
| 8 | 0.42 / 0.46 | 0.44 / 0.46 | 0.49 / 0.52 | 0.46 / 0.43 |
| 16 | 0.46 / 0.47 | 0.52 / 0.53 | 0.53 / 0.55 | 0.45 / 0.47 |
| 32 | 0.46 / 0.47 | 0.52 / 0.57 | 0.55 / 0.53 | 0.44 / 0.47 |
| 64 | 0.47 / 0.47 | 0.52 / 0.57 | 0.54 / 0.55 | 0.42 / 0.44 |

**cfgpatch** (floor 0.111)

| N | d=1 | d=2 | d=3 | d=4 |
|---|---|---|---|---|
| 1 | 0.10 / 0.10 | 0.08 / 0.09 | 0.10 / 0.10 | 0.10 / 0.07 |
| 2 | 0.10 / 0.12 | 0.11 / 0.10 | 0.10 / 0.12 | 0.11 / 0.12 |
| 4 | 0.07 / 0.09 | 0.07 / 0.08 | 0.07 / 0.09 | 0.08 / 0.04 |
| 8 | 0.43 / 0.32 | 0.14 / 0.14 | 0.12 / 0.11 | 0.10 / 0.09 |
| 16 | 0.60 / 0.61 | 0.14 / 0.12 | 0.14 / 0.14 | 0.16 / 0.18 |
| 32 | 0.57 / 0.60 | 0.15 / 0.12 | 0.17 / 0.11 | 0.14 / 0.18 |
| 64 | 0.57 / 0.61 | 0.17 / 0.11 | 0.14 / 0.10 | 0.14 / 0.18 |

**chain** (floor 0.111)

| N | d=1 | d=2 | d=3 | d=4 | d=5 |
|---|---|---|---|---|---|
| 1 | 0.06 / 0.03 | 0.06 / 0.02 | 0.07 / 0.03 | 0.05 / 0.02 | 0.04 / 0.04 |
| 2 | 0.12 / 0.13 | 0.14 / 0.08 | 0.07 / 0.09 | 0.09 / 0.08 | 0.12 / 0.08 |
| 4 | 0.18 / 0.20 | 0.16 / 0.12 | 0.12 / 0.10 | 0.10 / 0.06 | 0.11 / 0.11 |
| 8 | 0.93 / 0.71 | 0.14 / 0.16 | 0.12 / 0.10 | 0.07 / 0.10 | 0.07 / 0.09 |
| 16 | 1.00 / 0.98 | 0.37 / 0.30 | 0.20 / 0.17 | 0.09 / 0.08 | 0.06 / 0.06 |
| 32 | 1.00 / 1.00 | 0.40 / 0.29 | 0.17 / 0.16 | 0.07 / 0.07 | 0.05 / 0.05 |
| 64 | 1.00 / 1.00 | 0.41 / 0.32 | 0.17 / 0.17 | 0.09 / 0.07 | 0.05 / 0.05 |

**ordertrack** (floor 0.265)

| N | d=1 | d=2 | d=3 | d=4 |
|---|---|---|---|---|
| 1 | 0.27 / 0.26 | 0.20 / 0.18 | 0.18 / 0.16 | 0.18 / 0.13 |
| 2 | 0.23 / 0.14 | 0.20 / 0.10 | 0.18 / 0.12 | 0.20 / 0.13 |
| 4 | 0.43 / 0.52 | 0.32 / 0.37 | 0.28 / 0.36 | 0.28 / 0.34 |
| 8 | 0.71 / 0.66 | 0.58 / 0.45 | 0.51 / 0.47 | 0.47 / 0.38 |
| 16 | 0.60 / 0.42 | 0.41 / 0.31 | 0.46 / 0.32 | 0.41 / 0.28 |
| 32 | 0.56 / 0.38 | 0.43 / 0.28 | 0.45 / 0.33 | 0.42 / 0.31 |
| 64 | 0.53 / 0.38 | 0.45 / 0.29 | 0.45 / 0.33 | 0.41 / 0.31 |

### Per-N fits (`both` model)

Crossings at the default level; CIs for the 50% crossings, gap, r and Δ_m are SS's per-N pair bootstrap.

| bank | N | pairs | kf cross | kl cross | ratio kf/kl | gap | Δ_m [CI] | r [CI] | 50%: kf / kl | 50% gap [CI] | shift vs scale | own-fit abs dmu |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| brew | 1 | 800 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -880.73) | | | | | | | | | |
| brew | 2 | 800 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -880.73) | | | | | | | | | |
| brew | 4 | 800 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -880.73) | | | | | | | | | |
| brew | 8 | 800 | *not identified* (on bound: mu; extrapolated cross_kf, cross_kl; crossings -30.00 / -43.64) | | | | | | | | | |
| brew | 16 | 800 | *not identified* (on bound: mu, log_r; extrapolated cross_kf, cross_kl; crossings -30.00 / -349.98) | | | | | | | | | |
| brew | 32 | 800 | *not identified* (on bound: mu; extrapolated cross_kf, cross_kl; crossings -30.00 / -47.21) | | | | | | | | | |
| brew | 64 | 800 | *not identified* (extrapolated cross_kf, cross_kl; crossings -10.12 / -13.19) | | | | | | | | | |
| cfgpatch | 1 | 800 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -880.73) | | | | | | | | | |
| cfgpatch | 2 | 800 | *not identified* (on bound: mu, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -175.69) | | | | | | | | | |
| cfgpatch | 4 | 800 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -880.73) | | | | | | | | | |
| cfgpatch | 8 | 800 | 0.81 | 0.46 | 1.739 | 0.34 | -0.16 [-1.17, 4.10] | 0.752 [0.184, 3.603] | 0.89 / 0.58 | 0.31 [-0.03, 0.75] | can't distinguish (leans shift, P(shift)=0.77) | 0.0000 |
| cfgpatch | 16 | 800 | 1.07 | 1.04 | 1.021 | 0.02 | 0.98 [-0.02, 4.70] | 1.659 [0.990, 4.146] | 1.14 / 1.09 | 0.05 [-0.03, 0.14] | can't distinguish (leans scale, P(shift)=0.45) | 0.0000 |
| cfgpatch | 32 | 800 | 1.02 | 1.04 | 0.981 | -0.02 | 1.47 [-0.01, 6.54] | 2.020 [1.000, 5.431] | 1.11 / 1.08 | 0.03 [-0.06, 0.11] | can't distinguish (leans shift, P(shift)=0.69) | 0.0000 |
| cfgpatch | 64 | 800 | *not identified* (on bound: log_r; crossings 1.03 / 1.01) | | | | | | | | | |
| chain | 1 | 1000 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -886.32) | | | | | | | | | |
| chain | 2 | 1000 | *not identified* (kf not above floor at the shallowest depth; crossings 0.65 / 0.67) | | | | | | | | | |
| chain | 4 | 1000 | *not identified* (extrapolated cross_kf; crossings -1.65 / 0.41) | | | | | | | | | |
| chain | 8 | 1000 | 1.43 | 1.20 | 1.191 | 0.23 | -0.43 [-1.39, 0.42] | 0.631 [0.251, 1.095] | 1.48 / 1.27 | 0.20 [-0.08, 0.34] | can't distinguish (leans shift, P(shift)=0.94) | 0.0000 |
| chain | 16 | 1000 | 1.95 | 1.75 | 1.114 | 0.20 | -0.68 [-0.74, -0.62] | 0.297 [0.249, 0.345] | 1.96 / 1.80 | 0.16 [0.08, 0.24] | shift; both also needs r != 1 | 0.0000 |
| chain | 32 | 1000 | 1.96 | 1.93 | 1.016 | 0.03 | 0.05 [0.04, 0.08] | 1.016 [1.016, 1.029] | 1.98 / 1.94 | 0.03 [0.01, 0.05] | scale | 0.0000 |
| chain | 64 | 1000 | 1.96 | 1.94 | 1.013 | 0.02 | 0.04 [0.02, 0.07] | 1.013 [1.012, 1.025] | 1.98 / 1.95 | 0.02 [0.00, 0.05] | can't distinguish (leans scale, P(shift)=0.12) | 0.0000 |
| ordertrack | 1 | 800 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -880.73) | | | | | | | | | |
| ordertrack | 2 | 800 | *not identified* (on bound: mu, log_beta, Delta, log_r; kf not above floor at the shallowest depth; extrapolated cross_kf, cross_kl; crossings -30.00 / -880.73) | | | | | | | | | |
| ordertrack | 4 | 800 | *not identified* (extrapolated cross_kl; crossings 0.02 / -0.24) | | | | | | | | | |
| ordertrack | 8 | 800 | 1.72 | 0.88 | 1.951 | 0.84 | 1.06 [0.58, 1.90] | 1.138 [0.781, 1.623] | 3.26 / 2.23 | 1.02 [0.59, 1.73] | can't distinguish (leans shift, P(shift)=0.67) | — |
| ordertrack | 16 | 800 | *not identified* (extrapolated cross_kf, cross_kl; crossings -0.08 / -0.62) | | | | | | | | | |
| ordertrack | 32 | 800 | *not identified* (extrapolated cross_kf, cross_kl; crossings -0.76 / -3.32) | | | | | | | | | |
| ordertrack | 64 | 800 | *not identified* (extrapolated cross_kf, cross_kl; crossings -1.81 / -3.89) | | | | | | | | | |

### Main test: slope of the penalty on log(num_steps), joint pair bootstrap

Only identified N enter a bank's slope (not identified = a `both` parameter on its bound, key-first not above the floor at the shallowest depth (binomial p > 0.01), or a crossing outside the tested depths +- 1). N used per bank: brew []; cfgpatch [8, 16, 32]; chain [8, 16, 32, 64]; ordertrack []. At least 3 are needed.

| bank | metric | slope per unit log N | 95% CI | P(slope < 0) | usable draws |
|---|---|---|---|---|---|
| cfgpatch | ratio | -0.546 | [-8.731, 0.053] | 0.935 | 947/1000 |
| cfgpatch | Delta_m | +1.177 | [-1.532, 4.371] | 0.066 | 1000/1000 |
| cfgpatch | r | +0.914 | [-0.919, 3.082] | 0.056 | 1000/1000 |
| chain | ratio | -0.092 | [-0.141, -0.003] | 0.982 | 1000/1000 |
| chain | Delta_m | +0.310 | [0.036, 0.715] | 0.018 | 1000/1000 |
| chain | r | +0.269 | [0.121, 0.431] | 0.005 | 1000/1000 |
| mean over banks | ratio | -0.319 | [-4.433, -0.014] | 0.982 | 947/1000 |
| mean over banks | Delta_m | +0.743 | [-0.649, 2.386] | 0.052 | 1000/1000 |
| mean over banks | r | +0.592 | [-0.338, 1.689] | 0.045 | 1000/1000 |

### Model-free: paired gold log-prob penalty kf − kl, per depth and N

Mean over pairs of log p(gold | kf) − log p(gold | kl), both normalised over the candidate set; > 0 = key-last worse. 95% pair-bootstrap CIs. Last column: OLS slope of the penalty on log N over the core grid (joint resample of pairs across N); negative = the penalty shrinks with recurrence.

**brew**

| depth | pairs | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 | N=64 | slope on log N [CI] |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 200 | +0.09 [-0.03, 0.22] | -0.02 [-0.11, 0.06] | +0.02 [-0.03, 0.08] | -0.04 [-0.06, -0.01] | -0.00 [-0.04, 0.03] | -0.02 [-0.05, 0.01] | -0.03 [-0.05, -0.00] | -0.012 [-0.031, 0.007] |
| 2 | 200 | +0.06 [-0.06, 0.19] | +0.09 [0.00, 0.18] | +0.15 [0.10, 0.21] | -0.06 [-0.09, -0.04] | -0.04 [-0.06, -0.01] | -0.07 [-0.09, -0.04] | -0.06 [-0.09, -0.04] | -0.063 [-0.082, -0.045] |
| 3 | 200 | +0.03 [-0.10, 0.17] | +0.12 [0.05, 0.20] | +0.20 [0.13, 0.26] | -0.03 [-0.05, -0.01] | -0.06 [-0.09, -0.04] | -0.05 [-0.08, -0.03] | -0.05 [-0.07, -0.03] | -0.074 [-0.093, -0.054] |
| 4 | 200 | +0.10 [-0.03, 0.24] | +0.20 [0.11, 0.28] | +0.20 [0.13, 0.27] | -0.05 [-0.08, -0.02] | -0.10 [-0.13, -0.07] | -0.10 [-0.13, -0.07] | -0.11 [-0.13, -0.08] | -0.095 [-0.117, -0.073] |

**cfgpatch**

| depth | pairs | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 | N=64 | slope on log N [CI] |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 200 | -0.01 [-0.13, 0.11] | -0.02 [-0.10, 0.05] | -0.02 [-0.05, 0.00] | +0.25 [0.14, 0.36] | -0.02 [-0.18, 0.12] | -0.09 [-0.24, 0.06] | -0.14 [-0.29, -0.00] | -0.084 [-0.146, -0.023] |
| 2 | 200 | -0.04 [-0.16, 0.09] | -0.01 [-0.08, 0.06] | +0.03 [-0.00, 0.06] | +0.06 [-0.03, 0.13] | +0.51 [0.34, 0.67] | +0.31 [0.16, 0.47] | +0.24 [0.09, 0.38] | +0.097 [0.033, 0.165] |
| 3 | 200 | +0.01 [-0.11, 0.12] | -0.05 [-0.11, 0.03] | +0.04 [0.01, 0.08] | +0.10 [0.02, 0.17] | +0.32 [0.20, 0.44] | +0.30 [0.17, 0.43] | +0.23 [0.10, 0.35] | +0.083 [0.031, 0.134] |
| 4 | 200 | +0.03 [-0.08, 0.14] | +0.01 [-0.07, 0.09] | +0.06 [0.02, 0.09] | +0.01 [-0.08, 0.09] | +0.12 [0.02, 0.23] | -0.00 [-0.12, 0.11] | -0.04 [-0.15, 0.06] | -0.030 [-0.077, 0.018] |

**chain**

| depth | pairs | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 | N=64 | slope on log N [CI] |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 200 | +0.41 [0.27, 0.57] | -0.04 [-0.13, 0.05] | -0.21 [-0.28, -0.15] | +0.57 [0.50, 0.64] | +0.12 [0.10, 0.15] | +0.05 [0.04, 0.06] | +0.05 [0.04, 0.06] | +0.001 [-0.023, 0.024] |
| 2 | 200 | +0.54 [0.39, 0.70] | +0.10 [0.01, 0.19] | -0.14 [-0.22, -0.06] | -0.14 [-0.23, -0.07] | +0.22 [0.14, 0.30] | +0.28 [0.17, 0.37] | +0.27 [0.18, 0.37] | +0.180 [0.135, 0.226] |
| 3 | 200 | +0.36 [0.23, 0.51] | +0.15 [0.06, 0.23] | -0.11 [-0.21, -0.03] | +0.05 [-0.01, 0.12] | +0.09 [0.03, 0.15] | +0.04 [-0.03, 0.11] | +0.04 [-0.02, 0.11] | +0.044 [0.000, 0.089] |
| 4 | 200 | +0.37 [0.23, 0.52] | +0.06 [-0.02, 0.13] | +0.08 [0.00, 0.16] | -0.08 [-0.14, -0.03] | +0.07 [0.03, 0.12] | -0.03 [-0.08, 0.02] | -0.02 [-0.07, 0.03] | -0.021 [-0.055, 0.015] |
| 5 | 200 | +0.26 [0.13, 0.41] | +0.20 [0.10, 0.30] | +0.03 [-0.04, 0.11] | -0.12 [-0.17, -0.07] | +0.09 [0.05, 0.12] | -0.00 [-0.03, 0.03] | +0.01 [-0.02, 0.04] | +0.010 [-0.018, 0.038] |

**ordertrack**

| depth | pairs | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 | N=64 | slope on log N [CI] |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 200 | +0.11 [-0.04, 0.27] | +0.19 [0.05, 0.32] | -0.15 [-0.22, -0.09] | +0.13 [0.08, 0.18] | +0.27 [0.20, 0.35] | +0.36 [0.30, 0.43] | +0.33 [0.26, 0.39] | +0.171 [0.136, 0.208] |
| 2 | 200 | +0.21 [0.05, 0.37] | +0.28 [0.16, 0.39] | -0.32 [-0.44, -0.21] | +0.32 [0.21, 0.43] | +0.31 [0.18, 0.42] | +0.40 [0.30, 0.50] | +0.39 [0.29, 0.48] | +0.217 [0.167, 0.267] |
| 3 | 220 | +0.38 [0.23, 0.54] | +0.32 [0.20, 0.45] | -0.28 [-0.38, -0.17] | +0.10 [-0.00, 0.20] | +0.34 [0.22, 0.44] | +0.39 [0.28, 0.49] | +0.38 [0.27, 0.48] | +0.233 [0.181, 0.282] |
| 4 | 180 | +0.36 [0.20, 0.52] | +0.24 [0.09, 0.38] | -0.38 [-0.47, -0.27] | +0.17 [0.07, 0.28] | +0.34 [0.23, 0.45] | +0.39 [0.28, 0.49] | +0.37 [0.26, 0.47] | +0.247 [0.193, 0.294] |


### Continuous version: gold log-prob (normalised over candidates) ~ kl × depth × log N, SEs clustered by pair

| fit | n rows | pairs | kl | kl:dep | kl:logN | **kl:dep:logN** (p) | dep:logN |
|---|---|---|---|---|---|---|---|
| brew | 8000 | 800 | +0.0158 ± 0.0055 | +0.0038 ± 0.0050 | +0.0647 ± 0.0053 | **+0.0262 ± 0.0047** (3.06e-08) | +0.0205 ± 0.0136 |
| cfgpatch | 8000 | 800 | -0.1130 ± 0.0213 | -0.0069 ± 0.0192 | -0.0186 ± 0.0146 | **-0.0147 ± 0.0130** (0.258) | -0.0168 ± 0.0267 |
| chain | 10000 | 1000 | -0.0594 ± 0.0095 | +0.0322 ± 0.0049 | -0.0495 ± 0.0089 | **+0.0182 ± 0.0050** (0.000259) | -0.1425 ± 0.0062 |
| ordertrack | 8000 | 800 | -0.1930 ± 0.0189 | +0.0058 ± 0.0147 | -0.2208 ± 0.0124 | **-0.0245 ± 0.0103** (0.0174) | +0.0334 ± 0.0122 |
| pooled | 34000 | 3400 | — | — | — | **+0.0049 ± 0.0040** (0.216) | — |

Caveat: the regression is linear in log-prob, which is compressed at the floor and the ceiling, so the sign of kl:dep:logN is not a clean test on its own. On the synthetic fixture (`--simulate`), where the truth is a key-last shift that shrinks with log N at r = 1 in logit space, kl:dep:logN comes out negative. Read it together with the logit-space slopes above.


Figures: `figs/huginn__sweep/goldlp_vs_depth__full.png`, `figs/huginn__sweep/acc_vs_depth__full.png`, `figs/huginn__sweep/penalty_vs_logN__full.png`, `figs/huginn__sweep/kf_acc_vs_steps__full.png`
