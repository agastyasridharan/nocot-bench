# Shift vs. scale: what holds, what doesn't, and how to get a clean answer

For Agastya, from Niranjan. Written 2026-10-01, alongside `shift_scale.py`.

## The question

Key-last crosses 50% at a shallower depth than key-first in every informative bank. `shift_scale.py` asks what shape that gap has:

- **Shift:** key-last is key-first with a fixed head start of Δ steps. The curves are parallel and the gap stays constant.
- **Scale:** each step costs r times as much in key-last, so the gap grows with depth.

## Where things stand

The answer depends on the chance floor c that the curves are fitted with. The script now fits every model twice: once with c fixed at `analyze.py`'s chance floor, and once with c estimated from the data (one floor shared by both arms). Full tables are in `../results/report__shift_scale__gpt-6.1-sol.md`, in the "Robustness to the floor" section.

| | floor fixed | floor estimated |
|---|---|---|
| Pooled LL(shift) − LL(scale), 12 banks | −3.3 [−16.7, 9.9], inconclusive | −28.1 [−41.5, −14.6], favours scale, and still does after dropping any one bank |
| Banks with a CI excluding 0 | scale: chainbig, progpred_loop, progpred_unrolled; shift: ordertrack, routing | scale: chainbig, progpred_unrolled, soundchange |

**Robust under both floors:** chainbig and progpred_unrolled favour scale. **No bank robustly favours shift.** Ordertrack, routing, progpred_loop and soundchange change verdict with the floor. The other six lean the same way under both floors but are not significant under both.

So the earlier reading, that ordertrack and routing are shift-like tasks, is not supported. The cleanest statement the current data allows: two banks are scale-like, the pooled evidence leans scale once the floor is estimated, and nothing is reliably shift-like.

## The problem: the fixed floors are wrong in several banks

In several banks, accuracy levels off well above the chance floor `analyze.py` uses, and the fixed-floor model then fits badly. Deviance compares the 4-parameter "both" model with a perfect per-(arm, depth) fit; a value far above df means poor fit.

| bank | fixed floor | estimated floor [CI] | deviance/df, floor fixed | deviance/df, floor estimated |
|---|---|---|---|---|
| progpred_loop | 0.035 | 0.185 [0.154, 0.214] | 238/8 | 11/7 |
| routing | 0.200 | 0.538 [0.504, 0.575] | 190/14 | 23/13 |
| boxpush | 0.073 | 0.235 [0.180, 0.285] | 85/26 | 34/25 |
| soundchange | 0.002 | 0.135 [0.007, 0.238] | 72/32 | 51/31 |
| progpred_unrolled | 0.035 | 0.107 [0.077, 0.137] | 58/8 | 18/7 |
| ordertrack | 0.095 | 0.548 [0.413, 0.635] | 53/18 | 21/17 |

Freeing the floor gains up to 117 log-likelihood units, against shift-vs-scale differences of 6 units or less. The simulation in `../results/shift_scale_floor_bias_sim.md` shows why it matters: when accuracy levels off above the assumed floor and the depths run deep, a true scale effect is picked correctly 16% of the time with the fixed floor and 73% with the estimated floor.

The plateaus have at least two different causes:

1. **The answer is partly predictable without the key (routing).** With the rule table fixed, re-solving each item from all 20 possible starting desks and stamp sets, and taking the most common answer, gives about **0.43** at every depth. That's the best accuracy available to a strategy that ignores the key entirely, against an assumed floor of 0.20. Key-first accuracy at depth levels off at about 0.49. (Computed for 877 of 900 items; 23 didn't parse.)
2. **A plateau that isn't guessing (progpred).** The same calculation, over all 765 `(a, u0)` starts, gives about **0.05** at every depth, close to the assumed 0.035. Yet key-first sits at about 0.21 from depth 4 to 8 in the loop form. Some deep items are being solved for a reason the logistic curve doesn't capture.

Estimating the floor is a patch, not a fix. It is weakly identified where key-first barely decays: ordertrack's estimated 0.55 is above its lowest observed accuracy (0.49), and shortpath's CI runs from 0 to 0.48. It also assumes one floor shared by both arms.

## What to do, in order

### 1. Rerun on the raw runs (no API calls, a few minutes)

`runs/` isn't in the repo, so the current numbers rebuild pairs from the per-depth counts in the results JSON. That drops the 56 pairs at depths with fewer than 10 pairs, which matters most for soundchange's deepest items. From the repo root:

```bash
python latekey/shift_scale.py --tag gpt-6.1-sol --runs latekey/runs/main__gpt-6.1-sol.jsonl.gz latekey/runs/p3x__gpt-6.1-sol.jsonl.gz
python latekey/shift_scale.py --tag gpt-6.1-sol --runs latekey/runs/main__gpt-6.1-sol.jsonl.gz latekey/runs/p3x__gpt-6.1-sol.jsonl.gz --drop-invalid
```

### 2. Compute the key-ignorant floor for every bank (no API calls)

For each item, keep the steps, draw the key from the generator's own key distribution (enumerate it where it's small), re-solve with the existing solvers, and record how often the most common answer comes up. Average per bank and depth. This gives a floor per depth that has nothing to do with the model, and it replaces the single majority-baseline floor.

- Routing and progpred are done above. The others need their key sampler pointed at a fixed set of steps. Where a step names something that only exists in some keys (ordertrack items, for example), keep only valid keys.
- `shift_scale.py` takes one floor per bank today. Accepting a floor per depth is a small change; Niranjan can make it once the floors exist.

### 3. Work out what the deep plateau is where it isn't guessing (raw runs, no API calls)

For progpred (both forms), chain and boxpush, look at which deep items the model gets right.

- Are they the same items in both arms?
- Do they share a feature: the trajectory reaches a fixed point, one branch never fires, or the answer equals a number in the prompt?

If a subset of deep items is easy for a structural reason, either filter it out in the generator or model the mixture explicitly. Until then, any one-curve-per-bank model is misspecified in these banks, whichever floor it uses.

### 4. Collect data that separates shift from scale (API calls)

The two models disagree most at shallow depth, where the current data sits at ceiling. Using the fitted parameters, the key-last − key-first logit gap at depth 1 is predicted to be −1.4 under shift and −0.3 under scale in brew, −2.6 vs −0.3 in cfgpatch, and −0.9 vs −0.2 in chainbig. Shift predicts a 3–12× larger penalty in every bank.

- **(a) A hard one-step control**, as in the original plan: one dependent step, made hard enough for about 70% accuracy (large-number arithmetic for chain, many distractor variables for cfgpatch, and so on). With about 150 pairs per bank the standard error on the gap is at most about 0.25 logits, which easily separates those predictions. The caveat is that this assumes the format penalty measured on hard single steps carries over to the sweep items.
- **(b) More pairs at depths where both arms are between 20% and 80%.** Many current items sit at ceiling (routing at depths 2–3, brew at 2–3, cfgpatch at 2–5) and carry almost no information.
- **(c) Deeper items where key-first never reaches 50%** (ordertrack, soundchange). Otherwise leave those banks out of the shift-vs-scale comparison.
- **(d) A second draw of the main run.** There is only one, and temperature-0 output is not deterministic on these endpoints.

Rough costs, from the README's $58 for 31,200 calls (about $0.0019 per call):

| addition | calls | cost |
|---|---|---|
| (a) hard one-step control, 12 banks × 150 pairs × 2 arms | 3,600 | ~$7 |
| (b) 100 more pairs at 4 informative depths per bank | 9,600 | ~$18 |
| (c) 4 deeper levels × 100 pairs for 2 banks | 1,600 | ~$3 |
| (d) second draw of the main run | 31,200 | ~$58 |

### 5. Reporting rule

Call a bank shift-like or scale-like only if the verdict's CI excludes 0 on the same side under the nominal floor, the estimated floor, and the key-ignorant per-depth floor from step 2. Report the pooled number under each.

### 6. Housekeeping

- **Phase-3x floors.** The committed `data_p3x/` files carry the Phase-3 chance floors, but `gen.py --p3x` computes its own (boxpush 0.0975 vs 0.0733, rulebook 0.15 vs 0.1233, soundchange 0.0025 vs 0.0017). The analysis uses the committed values. Decide which is intended and make the generator match.
- **Token counts.** `trailing_span_tokens` doesn't reproduce on a different `tiktoken` version. Pin it in `requirements.txt`.
- **Small depths.** `analyze.py` leaves depths with fewer than 10 pairs out of `cells`. Keep them in the JSON, even if they're not plotted, so the per-depth counts are complete.

## Commands

```bash
python latekey/shift_scale.py --tag gpt-6.1-sol                    # both floors, from the results JSON
python latekey/shift_scale.py --simulate                           # recovery check, including a bank that levels off above its floor
python latekey/shift_scale.py --floor-bias-sim 300                 # what a mis-set floor does to the verdict (about 4 minutes on 8 cores)
```
