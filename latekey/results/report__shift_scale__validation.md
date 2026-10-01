# Shift vs. scale reanalysis: synthetic validation

Source: synthetic banks: floor 0.2, mu 8, beta 0.9, depths 1-14, 80 pairs/depth; sim_null (Δ 0, r 1), sim_shift (Δ 1.5), sim_scale (r 1.3). Bootstrap: 2000 pair resamples per bank. Sweep items only, complete pairs only, dependent depth, floors as in analyze.py. 

Models (key-last logit; key-first is `beta (mu - d)` in all four): null `beta (mu - d)`, shift `beta (mu - Delta - d)`, scale `beta (mu - r d)`, both `beta (mu - Delta - r d)`. **Scale assumes the two arms' latent curves agree at d = 0**, i.e. the key-last penalty is zero for a zero-step item; any constant format penalty is forced into r. Both is a reparameterisation of the write-up's two separate floor fits, so its crossings should reproduce the write-up's.

## Pooled across banks

**Summed LL(shift) − LL(scale) = +0.29, 95% CI [-4.58, 5.41], P(shift better) = 0.548** over 3 banks (2000/2000 resamples usable).

Summed LRTs (rough; df = number of banks): shift vs both χ² = 3.6, p = 0.31; scale vs both χ² = 4.2, p = 0.24.

Leave one bank out:

| dropped | summed diff | 95% CI | P(shift better) |
|---|---|---|---|
| sim_null | +0.33 | [-4.47, 5.33] | 0.557 |
| sim_shift | -1.10 | [-4.34, 2.17] | 0.247 |
| sim_scale | +1.35 | [-2.35, 5.46] | 0.764 |

## Shift vs. scale per bank

LL(shift) − LL(scale) > 0 favours shift. Same parameter count, so log-likelihoods compare directly. CIs are 95% pair-bootstrap percentiles (the primary uncertainty measure).

| bank | n pairs | LL(shift) − LL(scale) [CI] | P(shift better) | Δ (shift) [CI] | r (scale) [CI] | Δ (both) [CI] | r (both) [CI] | reading |
|---|---|---|---|---|---|---|---|---|
| sim_null | 1120 | -0.04 [-0.72, 0.76] | 0.462 | 0.01 [-0.42, 0.41] | 1.008 [0.954, 1.061] | -1.19 [-3.72, 0.67] | 1.159 [0.918, 1.477] | can't distinguish (leans scale, P(shift)=0.46) |
| sim_shift | 1120 | +1.39 [-2.34, 5.59] | 0.771 | 1.51 [1.05, 1.98] | 1.235 [1.157, 1.320] | 1.42 [-0.44, 2.89] | 1.016 [0.780, 1.314] | can't distinguish (leans shift, P(shift)=0.77) |
| sim_scale | 1120 | -1.06 [-4.18, 2.17] | 0.246 | 1.63 [1.27, 1.97] | 1.274 [1.209, 1.344] | 0.26 [-2.08, 2.03] | 1.232 [0.944, 1.616] | can't distinguish (leans scale, P(shift)=0.25) |

## Centred parameterisation (§0.1)

Key-last logit `beta (mu - Delta_m - r (d - d_m) - d_m)`, with `d_m` the bank's median dependent depth over pairs. `Delta_m` is the key-last gap, in key-first steps, at `d_m`; `r` is the slope ratio. Same MLE as the `both` model (`Delta = Delta_m + d_m (1 - r)`). The last two columns are the bootstrap correlation of r with the d = 0 intercept Delta and with Delta_m. Joint scatter: `figs/shift_scale_joint__<tag>.png`.

| bank | d_m | Delta_m [CI] | r [CI] | Delta at d=0 [CI] | corr(Delta, r) | corr(Delta_m, r) |
|---|---|---|---|---|---|---|
| sim_null | 7.5 | -0.01 [-0.50, 0.43] | 1.159 [0.918, 1.477] | -1.19 [-3.72, 0.67] | -0.98 | -0.15 |
| sim_shift | 7.5 | +1.54 [0.96, 2.17] | 1.016 [0.780, 1.314] | +1.42 [-0.44, 2.89] | -0.96 | +0.64 |
| sim_scale | 7.5 | +2.00 [1.42, 2.75] | 1.232 [0.944, 1.616] | +0.26 [-2.08, 2.03] | -0.98 | +0.80 |

## Log-likelihoods and likelihood-ratio tests

LRT p-values treat the two arms of a pair as independent, which they are not; read them as rough.

| bank | LL null | LL shift | LL scale | LL both | null→shift χ² (p) | null→scale χ² (p) | shift→both χ² (p) | scale→both χ² (p) |
|---|---|---|---|---|---|---|---|---|
| sim_null | -824.1 | -824.1 | -824.1 | -823.4 | 0.0 (0.97) | 0.1 (0.77) | 1.4 (0.23) | 1.3 (0.25) |
| sim_shift | -964.5 | -942.4 | -943.8 | -942.4 | 44.1 (<1e-4) | 41.3 (<1e-4) | 0.0 (0.9) | 2.8 (0.094) |
| sim_scale | -877.3 | -841.1 | -840.1 | -840.1 | 72.3 (<1e-4) | 74.5 (<1e-4) | 2.2 (0.14) | 0.1 (0.81) |

## 50% crossings under each model

kf / kl in dependent-depth steps. Under shift the gap equals Δ; under scale the ratio kf/kl equals r.

| bank | floor c | write-up kf / kl | null | shift | scale | both | both: gap [CI] |
|---|---|---|---|---|---|---|---|
| sim_null | 0.2000 | — | 8.60 / 8.60 | 8.61 / 8.60 | 8.64 / 8.57 | 8.68 / 8.52 | +0.16 [-0.32, 0.61] |
| sim_shift | 0.2000 | — | 7.91 / 7.91 | 8.65 / 7.14 | 8.74 / 7.07 | 8.66 / 7.13 | +1.53 [0.98, 2.06] |
| sim_scale | 0.2000 | — | 7.56 / 7.56 | 8.34 / 6.71 | 8.42 / 6.61 | 8.41 / 6.62 | +1.79 [1.38, 2.20] |

## Point estimates

| bank | model | mu | beta | Δ | r | LL | AIC |
|---|---|---|---|---|---|---|---|
| sim_null | null | 8.07 | 0.954 | 0.00 | 1.000 | -824.10 | 1652.20 |
| sim_null | shift | 8.07 | 0.954 | 0.01 | 1.000 | -824.10 | 1654.20 |
| sim_null | scale | 8.10 | 0.950 | 0.00 | 1.008 | -824.05 | 1654.11 |
| sim_null | both | 8.10 | 0.893 | -1.19 | 1.159 | -823.39 | 1654.77 |
| sim_shift | null | 7.25 | 0.781 | 0.00 | 1.000 | -964.49 | 1932.99 |
| sim_shift | shift | 8.03 | 0.820 | 1.51 | 1.000 | -942.43 | 1890.87 |
| sim_shift | scale | 8.05 | 0.738 | 0.00 | 1.235 | -943.82 | 1893.65 |
| sim_shift | both | 8.03 | 0.814 | 1.42 | 1.016 | -942.43 | 1892.85 |
| sim_scale | null | 7.08 | 1.064 | 0.00 | 1.000 | -877.32 | 1758.63 |
| sim_scale | shift | 7.92 | 1.213 | 1.63 | 1.000 | -841.15 | 1688.29 |
| sim_scale | scale | 7.95 | 1.096 | 0.00 | 1.274 | -840.09 | 1686.17 |
| sim_scale | both | 7.95 | 1.111 | 0.26 | 1.232 | -840.06 | 1688.12 |

## Diagnostic: empirical floor-adjusted logits

`q = ((k + 0.5)/(n + 1) − c)/(1 − c)`, logit(q); — where q ≤ 0 or q ≥ 1. Parallel arms suggest shift; arms fanning out from d = 0 suggest scale. Fitted columns are the model's floor-adjusted logits.

### sim_null

| dep | n | k kf | k kl | logit kf | logit kl | kl − kf | shift fit kl − kf | scale fit kl − kf |
|---|---|---|---|---|---|---|---|---|
| 1 | 80 | 80 | 80 | 4.86 | 4.86 | 0.00 | -0.01 | -0.01 |
| 2 | 80 | 79 | 80 | 3.74 | 4.86 | 1.11 | -0.01 | -0.02 |
| 3 | 80 | 80 | 80 | 4.86 | 4.86 | 0.00 | -0.01 | -0.02 |
| 4 | 80 | 77 | 79 | 2.86 | 3.74 | 0.88 | -0.01 | -0.03 |
| 5 | 80 | 75 | 76 | 2.38 | 2.60 | 0.22 | -0.01 | -0.04 |
| 6 | 80 | 71 | 73 | 1.76 | 2.03 | 0.27 | -0.01 | -0.05 |
| 7 | 80 | 65 | 62 | 1.16 | 0.92 | -0.24 | -0.01 | -0.05 |
| 8 | 80 | 53 | 52 | 0.30 | 0.24 | -0.06 | -0.01 | -0.06 |
| 9 | 80 | 37 | 34 | -0.71 | -0.93 | -0.22 | -0.01 | -0.07 |
| 10 | 80 | 24 | 22 | -1.92 | -2.23 | -0.31 | -0.01 | -0.08 |
| 11 | 80 | 16 | 14 | -5.37 | — | — | -0.01 | -0.08 |
| 12 | 80 | 14 | 18 | — | -3.30 | — | -0.01 | -0.09 |
| 13 | 80 | 13 | 16 | — | -5.37 | — | -0.01 | -0.10 |
| 14 | 80 | 14 | 21 | — | -2.42 | — | -0.01 | -0.11 |

### sim_shift

| dep | n | k kf | k kl | logit kf | logit kl | kl − kf | shift fit kl − kf | scale fit kl − kf |
|---|---|---|---|---|---|---|---|---|
| 1 | 80 | 80 | 77 | 4.86 | 2.86 | -1.99 | -1.24 | -0.17 |
| 2 | 80 | 79 | 80 | 3.74 | 4.86 | 1.11 | -1.24 | -0.35 |
| 3 | 80 | 78 | 76 | 3.22 | 2.60 | -0.62 | -1.24 | -0.52 |
| 4 | 80 | 79 | 72 | 3.74 | 1.89 | -1.85 | -1.24 | -0.69 |
| 5 | 80 | 78 | 65 | 3.22 | 1.16 | -2.06 | -1.24 | -0.87 |
| 6 | 80 | 69 | 61 | 1.53 | 0.84 | -0.69 | -1.24 | -1.04 |
| 7 | 80 | 55 | 46 | 0.43 | -0.13 | -0.56 | -1.24 | -1.22 |
| 8 | 80 | 52 | 23 | 0.24 | -2.06 | -2.31 | -1.24 | -1.39 |
| 9 | 80 | 33 | 20 | -1.01 | -2.64 | -1.63 | -1.24 | -1.56 |
| 10 | 80 | 33 | 19 | -1.01 | -2.93 | -1.92 | -1.24 | -1.74 |
| 11 | 80 | 19 | 17 | -2.93 | -3.89 | -0.96 | -1.24 | -1.91 |
| 12 | 80 | 16 | 16 | -5.37 | -5.37 | 0.00 | -1.24 | -2.08 |
| 13 | 80 | 18 | 18 | -3.30 | -3.30 | 0.00 | -1.24 | -2.26 |
| 14 | 80 | 17 | 14 | -3.89 | — | — | -1.24 | -2.43 |

### sim_scale

| dep | n | k kf | k kl | logit kf | logit kl | kl − kf | shift fit kl − kf | scale fit kl − kf |
|---|---|---|---|---|---|---|---|---|
| 1 | 80 | 80 | 80 | 4.86 | 4.86 | 0.00 | -1.97 | -0.30 |
| 2 | 80 | 79 | 80 | 3.74 | 4.86 | 1.11 | -1.97 | -0.60 |
| 3 | 80 | 80 | 80 | 4.86 | 4.86 | 0.00 | -1.97 | -0.90 |
| 4 | 80 | 80 | 77 | 4.86 | 2.86 | -1.99 | -1.97 | -1.20 |
| 5 | 80 | 78 | 68 | 3.22 | 1.43 | -1.78 | -1.97 | -1.50 |
| 6 | 80 | 70 | 53 | 1.64 | 0.30 | -1.34 | -1.97 | -1.80 |
| 7 | 80 | 65 | 36 | 1.16 | -0.78 | -1.94 | -1.97 | -2.11 |
| 8 | 80 | 52 | 20 | 0.24 | -2.64 | -2.89 | -1.97 | -2.41 |
| 9 | 80 | 29 | 14 | -1.35 | — | — | -1.97 | -2.71 |
| 10 | 80 | 22 | 21 | -2.23 | -2.42 | -0.19 | -1.97 | -3.01 |
| 11 | 80 | 9 | 19 | — | -2.93 | — | -1.97 | -3.31 |
| 12 | 80 | 19 | 16 | -2.93 | -5.37 | -2.45 | -1.97 | -3.61 |
| 13 | 80 | 14 | 17 | — | -3.89 | — | -1.97 | -3.91 |
| 14 | 80 | 10 | 21 | — | -2.42 | — | -1.97 | -4.21 |

## Validation: parameter recovery

| bank | true Δ, r | Δ (shift) [CI] | r (scale) [CI] | Δ (both) [CI] | r (both) [CI] | LL(shift) − LL(scale) [CI] | P(shift better) | leans toward truth? |
|---|---|---|---|---|---|---|---|---|
| sim_null | Δ 0.0, r 1.0 | 0.01 [-0.42, 0.41] | 1.008 [0.954, 1.061] | -1.19 [-3.72, 0.67] | 1.159 [0.918, 1.477] | -0.04 [-0.72, 0.76] | 0.462 | n/a (null) |
| sim_shift | Δ 1.5, r 1.0 | 1.51 [1.05, 1.98] | 1.235 [1.157, 1.320] | 1.42 [-0.44, 2.89] | 1.016 [0.780, 1.314] | +1.39 [-2.34, 5.59] | 0.771 | yes |
| sim_scale | Δ 0.0, r 1.3 | 1.63 [1.27, 1.97] | 1.274 [1.209, 1.344] | 0.26 [-2.08, 2.03] | 1.232 [0.944, 1.616] | -1.06 [-4.18, 2.17] | 0.246 | yes |

Recovered mu / beta under the true model: sim_null: mu 8.07, beta 0.954; sim_shift: mu 8.03, beta 0.820; sim_scale: mu 7.95, beta 1.096 (truth mu 8, beta 0.9).
