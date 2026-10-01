# Huginn loop sweep: simulate

Source: /Users/agastyasridharan/j-lens/nocot-bench/latekey/huginn/results/sim/huginn__simfixture.jsonl. Rows: 18480. Bootstrap: 50 pair resamples. Depth: `dependent_depth`. Default crossing level: floor-adjusted midpoint c + (1-c)/2. Core grid for the slope tests: [4, 8, 16, 32, 64].

Penalty metrics (key-last vs key-first, `both` model): crossing ratio kf/kl (> 1 = key-last crosses shallower), Δ_m (centred gap at the median depth d_m; > 0 = key-last shifted shallower), r (> 1 = key-last pays more per step). **Prediction if the penalty reflects serial depth after the key: all three shrink with N (negative slopes on log N), and the kl:dep:logN coefficient of the continuous regression is positive.**

**Synthetic fixture.** synthetic banks sim_chain (floor 1/9, depths 1-6) and sim_brew (floor 1/4, depths 1-5), 120 pairs/depth; kf mu = 0.5 + 0.8 log2 N, beta 1.1; key-last shift Delta = max(0, 1.6 - 0.3 log2 N), r = 1; shared item effect sd 0.6. Truth: Delta_m and the ratio fall with log N (negative slopes; Delta_m slope ≈ -0.43 per unit ln N until it hits 0), r slope 0, kl:dep:logN ≈ 0 in logit space.

## Condition: full

### Key-first accuracy by num_steps (all depths)

| bank | N=1 | N=2 | N=4 | N=8 | N=16 | N=32 | N=64 |
|---|---|---|---|---|---|---|---|
| sim_brew | 0.347 | 0.385 | 0.510 | 0.627 | 0.707 | 0.812 | 0.882 |
| sim_chain | 0.197 | 0.299 | 0.349 | 0.496 | 0.571 | 0.688 | 0.783 |

### Accuracy by depth (kf / kl)

**sim_brew** (floor 0.250)

| N | d=1 | d=2 | d=3 | d=4 | d=5 |
|---|---|---|---|---|---|
| 1 | 0.53 / 0.42 | 0.42 / 0.25 | 0.28 / 0.23 | 0.33 / 0.25 | 0.18 / 0.18 |
| 2 | 0.68 / 0.48 | 0.42 / 0.38 | 0.34 / 0.35 | 0.26 / 0.24 | 0.22 / 0.26 |
| 4 | 0.79 / 0.65 | 0.60 / 0.47 | 0.53 / 0.33 | 0.35 / 0.33 | 0.28 / 0.27 |
| 8 | 0.92 / 0.84 | 0.82 / 0.64 | 0.67 / 0.49 | 0.45 / 0.42 | 0.28 / 0.23 |
| 16 | 0.97 / 0.95 | 0.89 / 0.85 | 0.72 / 0.68 | 0.60 / 0.49 | 0.34 / 0.32 |
| 32 | 0.99 / 0.99 | 0.96 / 0.95 | 0.89 / 0.87 | 0.73 / 0.65 | 0.48 / 0.48 |
| 64 | 1.00 / 0.99 | 0.98 / 0.99 | 0.93 / 0.93 | 0.82 / 0.84 | 0.68 / 0.77 |

**sim_chain** (floor 0.111)

| N | d=1 | d=2 | d=3 | d=4 | d=5 | d=6 |
|---|---|---|---|---|---|---|
| 1 | 0.42 / 0.15 | 0.34 / 0.15 | 0.12 / 0.13 | 0.07 / 0.10 | 0.13 / 0.07 | 0.09 / 0.12 |
| 2 | 0.59 / 0.39 | 0.49 / 0.23 | 0.25 / 0.13 | 0.17 / 0.12 | 0.14 / 0.10 | 0.15 / 0.08 |
| 4 | 0.80 / 0.67 | 0.57 / 0.39 | 0.33 / 0.25 | 0.20 / 0.12 | 0.09 / 0.07 | 0.11 / 0.14 |
| 8 | 0.89 / 0.80 | 0.78 / 0.59 | 0.63 / 0.38 | 0.32 / 0.16 | 0.23 / 0.15 | 0.13 / 0.10 |
| 16 | 0.96 / 0.93 | 0.89 / 0.80 | 0.60 / 0.68 | 0.49 / 0.41 | 0.32 / 0.23 | 0.17 / 0.13 |
| 32 | 0.99 / 0.97 | 0.93 / 0.97 | 0.85 / 0.82 | 0.68 / 0.68 | 0.42 / 0.40 | 0.25 / 0.22 |
| 64 | 0.99 / 1.00 | 0.96 / 0.95 | 0.90 / 0.91 | 0.84 / 0.79 | 0.63 / 0.51 | 0.38 / 0.37 |

### Per-N fits (`both` model)

Crossings at the default level; CIs for the 50% crossings, gap, r and Δ_m are SS's per-N pair bootstrap.

| bank | N | pairs | kf cross | kl cross | ratio kf/kl | gap | Δ_m [CI] | r [CI] | 50%: kf / kl | 50% gap [CI] | shift vs scale | own-fit abs dmu |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sim_brew | 1 | 600 | 0.56 | 0.81 | 0.688 | -0.25 | 11.78 [0.96, 23.68] | 6.494 [1.111, 12.182] | 1.24 / 0.91 | 0.33 [0.04, 0.91] | can't distinguish (leans scale, P(shift)=0.08) | — |
| sim_brew | 2 | 600 | 1.21 | 0.04 | 34.375 | 1.18 | -0.03 [-0.79, 1.07] | 0.593 [0.249, 1.167] | 1.73 / 0.90 | 0.83 [0.36, 1.84] | shift | — |
| sim_brew | 4 | 600 | 2.05 | 1.10 | 1.868 | 0.95 | 1.10 [0.43, 2.02] | 1.078 [0.694, 1.643] | 2.84 / 1.83 | 1.01 [0.51, 1.61] | can't distinguish (leans shift, P(shift)=0.74) | 0.0000 |
| sim_brew | 8 | 600 | 3.05 | 2.24 | 1.360 | 0.81 | 0.73 [0.35, 1.15] | 0.904 [0.696, 1.242] | 3.68 / 2.94 | 0.74 [0.24, 1.09] | can't distinguish (leans shift, P(shift)=0.88) | 0.0000 |
| sim_brew | 16 | 600 | 3.62 | 3.24 | 1.116 | 0.37 | 0.38 [0.12, 0.75] | 0.996 [0.793, 1.307] | 4.22 / 3.84 | 0.37 [0.04, 0.81] | can't distinguish (leans shift, P(shift)=0.68) | 0.0000 |
| sim_brew | 32 | 600 | 4.42 | 4.22 | 1.046 | 0.20 | 0.22 [-0.21, 0.57] | 0.978 [0.728, 1.335] | 4.97 / 4.79 | 0.18 [-0.35, 0.60] | can't distinguish (leans shift, P(shift)=0.62) | 0.0000 |
| sim_brew | 64 | 600 | 5.15 | 5.69 | 0.905 | -0.54 | -0.08 [-0.58, 0.36] | 0.828 [0.532, 1.210] | 5.76 / 6.43 | -0.67 [-2.36, -0.00] | can't distinguish (leans scale, P(shift)=0.12) | 0.0000 |
| sim_chain | 1 | 720 | 0.63 | -2.66 | — | 3.29 | 1.25 [-0.43, 20.48] | 0.668 [0.226, 8.359] | 0.84 / -2.34 | 3.18 [0.11, 14.10] | can't distinguish (leans shift, P(shift)=0.86) | — |
| sim_chain | 2 | 720 | 1.34 | 0.40 | 3.346 | 0.94 | 2.17 [1.09, 4.20] | 1.399 [1.003, 2.253] | 1.62 / 0.60 | 1.02 [0.49, 1.61] | can't distinguish (leans scale, P(shift)=0.50) | — |
| sim_chain | 4 | 720 | 2.03 | 1.42 | 1.436 | 0.62 | 0.68 [0.24, 1.46] | 1.030 [0.782, 1.406] | 2.24 / 1.61 | 0.62 [0.35, 0.93] | can't distinguish (leans shift, P(shift)=0.80) | 0.0000 |
| sim_chain | 8 | 720 | 3.08 | 2.11 | 1.455 | 0.96 | 1.15 [0.71, 1.98] | 1.138 [0.811, 1.749] | 3.32 / 2.33 | 0.99 [0.72, 1.27] | can't distinguish (leans shift, P(shift)=0.58) | 0.0000 |
| sim_chain | 16 | 720 | 3.61 | 3.33 | 1.084 | 0.28 | 0.28 [-0.08, 0.54] | 1.013 [0.851, 1.248] | 3.85 / 3.57 | 0.28 [-0.09, 0.56] | can't distinguish (leans shift, P(shift)=0.54) | 0.0000 |
| sim_chain | 32 | 720 | 4.46 | 4.37 | 1.021 | 0.09 | 0.04 [-0.21, 0.28] | 1.059 [0.857, 1.246] | 4.69 / 4.59 | 0.10 [-0.19, 0.43] | can't distinguish (leans scale, P(shift)=0.36) | 0.0000 |
| sim_chain | 64 | 720 | 5.28 | 4.99 | 1.058 | 0.29 | 0.19 [-0.33, 0.52] | 1.068 [0.757, 1.341] | 5.53 / 5.22 | 0.31 [-0.09, 0.63] | can't distinguish (leans scale, P(shift)=0.44) | 0.0000 |

### Main test: slope of the penalty on log(num_steps), joint pair bootstrap

| bank | metric | slope per unit log N | 95% CI | P(slope < 0) | usable draws |
|---|---|---|---|---|---|
| sim_brew | ratio | -0.323 | [-0.552, -0.160] | 1.000 | 49/50 |
| sim_brew | Delta_m | -0.414 | [-0.675, -0.148] | 1.000 | 50/50 |
| sim_brew | r | -0.062 | [-0.213, 0.091] | 0.660 | 50/50 |
| sim_chain | ratio | -0.171 | [-0.270, -0.111] | 1.000 | 50/50 |
| sim_chain | Delta_m | -0.302 | [-0.581, -0.090] | 1.000 | 50/50 |
| sim_chain | r | -0.000 | [-0.122, 0.147] | 0.420 | 50/50 |
| mean over banks | ratio | -0.247 | [-0.363, -0.149] | 1.000 | 49/50 |
| mean over banks | Delta_m | -0.358 | [-0.592, -0.176] | 1.000 | 50/50 |
| mean over banks | r | -0.031 | [-0.151, 0.074] | 0.620 | 50/50 |

### Continuous version: gold log-prob (normalised over candidates) ~ kl × depth × log N, SEs clustered by pair

| fit | n rows | pairs | kl | kl:dep | kl:logN | **kl:dep:logN** (p) | dep:logN |
|---|---|---|---|---|---|---|---|
| sim_brew | 6000 | 600 | -0.1007 ± 0.0033 | +0.0009 ± 0.0023 | +0.0854 ± 0.0037 | **-0.0141 ± 0.0026** (5.41e-08) | +0.0713 ± 0.0021 |
| sim_chain | 7200 | 720 | -0.1512 ± 0.0064 | +0.0006 ± 0.0053 | +0.1349 ± 0.0067 | **-0.0158 ± 0.0053** (0.00269) | +0.0860 ± 0.0038 |
| pooled | 13200 | 1320 | -0.1007 ± 0.0033 | +0.0009 ± 0.0023 | +0.0851 ± 0.0036 | **-0.0152 ± 0.0035** (1.26e-05) | +0.0718 ± 0.0027 |

Figures: `figs/huginn__simulate/goldlp_vs_depth__full.png`, `figs/huginn__simulate/acc_vs_depth__full.png`, `figs/huginn__simulate/penalty_vs_logN__full.png`, `figs/huginn__simulate/kf_acc_vs_steps__full.png`
