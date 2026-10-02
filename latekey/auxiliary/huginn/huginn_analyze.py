#!/usr/bin/env python3
"""huginn_analyze.py — does more recurrence shrink the key-last penalty? (plan section C, Analysis)

    python latekey/auxiliary/huginn/huginn_analyze.py --runs 'latekey/auxiliary/huginn/results/runs/huginn__sweep__s*.jsonl' --tag sweep
    python latekey/auxiliary/huginn/huginn_analyze.py --simulate          # smoke test on a synthetic fixture

For each condition (mode = full recurrence, or per-token with a given low count) and bank:

1. Per num_steps N: the floored-sigmoid fits of latekey/shift_scale.py on argmax correctness
   (SS.bank_from_pairs + SS.analyse_bank; pairs = (dependent depth, y_kf, y_kl)). Reported: the
   key-first / key-last crossings, their ratio kf/kl, the gap, Delta, r and the centred gap
   Delta_m (read with .get(); if shift_scale.py does not provide it yet it is computed as
   Delta - d_m (1 - r), d_m = median dependent depth of the bank's pairs, which is the same
   reparameterisation of the `both` model).
   Crossing level: Huginn is far below the frontier models, so key-first may never reach 50%.
   The default level is therefore the floor-adjusted midpoint p = c + (1 - c)/2 (logit 0:
   kf crossing = mu, kl crossing = (mu - Delta)/r); --cross-level 0.5 uses 50% as in the
   write-up. Both are in the JSON.
2. Main test: regress each per-N penalty (crossing ratio kf/kl, r, Delta_m) on log(N) over the
   core grid. CI by a JOINT pair bootstrap: one multinomial resample of the bank's pairs per
   draw, applied to every N (the same items are scored at every N), the `both` model refitted
   at every N, the OLS slope recomputed. The bootstrap refits use a local copy of the `both`
   likelihood (same model as shift_scale.py) so they do not depend on its internals; the local
   point fit is checked against SS's (column `own-fit |dmu|`). Predicted: negative slopes.
3. Continuous version: OLS of the normalised gold log-prob on kl x depth x log(N) (statsmodels,
   SEs clustered by pair), per bank and pooled with bank-specific lower-order terms. Predicted:
   positive kl:depth:logN.
4. Key-first accuracy against N (does recurrence buy depth at all?).

Writes results/report__huginn__<tag>.md, results/huginn__<tag>.json, results/figs/huginn__<tag>/*.png.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")                               # one BLAS thread per worker process
import argparse
import collections
import glob
import gzip
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy import optimize, stats
from scipy.special import expit, log_expit, logit

HERE = os.path.dirname(os.path.abspath(__file__))
LATEKEY = os.path.dirname(os.path.dirname(HERE))           # latekey (this file is in latekey/auxiliary/huginn)
sys.path.insert(0, LATEKEY)
sys.path.insert(0, HERE)
import shift_scale as SS                                         # noqa: E402

CORE = [4, 8, 16, 32, 64]
KF_COL, KL_COL = "#2a6fdb", "#d9480f"
BOUNDS = [(-30.0, 80.0), (-5.0, 4.0), (-40.0, 40.0), (-2.5, 2.5)]


# ---------------------------------------------------------------- data

def load(patterns):
    rows = []
    for pat in patterns:
        for fn in sorted(glob.glob(pat)):
            for line in (gzip.open(fn, "rt") if fn.endswith(".gz") else open(fn)):
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    seen, out = set(), []
    for r in rows:                                               # dedupe resumed / repeated rows
        k = (r["problem_number"], r["num_steps"], r["mode"], r.get("n_lo"), r.get("init_scale"), r.get("init_seed"))
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def cond_name(r):
    return "full" if r["mode"] == "full" else f"pertoken_lo{r['n_lo']}"


def pairs_for(rows, depth_key):
    P = collections.defaultdict(dict)
    for r in rows:
        P[r["pair_id"]][r["arm"]] = r
    out = {}
    for pid, v in P.items():
        if "kf" in v and "kl" in v:
            out[pid] = (float(v["kf"][depth_key]), int(v["kf"]["correct"]), int(v["kl"]["correct"]))
    return out


# ---------------------------------------------------------------- local both-model fit (bootstrap)

def _terms(z, k, n, c):
    lp = np.logaddexp(math.log(c), math.log1p(-c) + log_expit(z))         # log p
    l1p = math.log1p(-c) + log_expit(-z)                                    # log(1 - p)
    ll = np.sum(k * lp + (n - k) * l1p)
    g = k * np.exp(math.log1p(-c) + log_expit(z) + log_expit(-z) - lp) - (n - k) * expit(z)   # d ll / dz
    return ll, g


def _nll(th, d, kf, nf, kl, nl, c):
    """Negative log-lik of the `both` model and its gradient in theta = [mu, log beta, Delta, log r]."""
    mu, lb, D, lr = th
    beta, r = math.exp(lb), math.exp(lr)
    z1, z2 = beta * (mu - d), beta * (mu - D - r * d)
    l1, g1 = _terms(z1, kf, nf, c)
    l2, g2 = _terms(z2, kl, nl, c)
    G = np.array([beta * (g1.sum() + g2.sum()), np.sum(g1 * z1) + np.sum(g2 * z2),
                  -beta * g2.sum(), -beta * r * np.sum(g2 * d)])
    return -(l1 + l2), -G


def fit_both(agg, c, starts):
    d, kf, nf, kl, nl = agg
    best = None
    for s in starts:
        x0 = np.clip(np.asarray(s, float), [b[0] for b in BOUNDS], [b[1] for b in BOUNDS])
        res = optimize.minimize(_nll, x0, args=(d, kf, nf, kl, nl, c), jac=True, method="L-BFGS-B", bounds=BOUNDS)
        if np.isfinite(res.fun) and (best is None or res.fun < best.fun):
            best = res
    return best.x


def metrics(th, c, d_m, level):
    mu, beta, D, r = th[0], math.exp(th[1]), th[2], math.exp(th[3])
    zs = 0.0 if level == "mid" else float(logit((level - c) / (1 - c)))
    kf = mu - zs / beta
    kl = (mu - D - zs / beta) / r
    return dict(cross_kf=kf, cross_kl=kl, ratio=kf / kl if kl > 0 else float("nan"), gap=kf - kl,
                Delta=D, r=r, Delta_m=D - d_m * (1 - r), mu=mu, beta=beta)


def agg_from(depths, ykf, ykl, w):
    du = np.unique(depths)
    ind = (depths[None, :] == du[:, None]).astype(float)
    n = ind @ w
    return du, ind @ (w * ykf), n, ind @ (w * ykl), n


# ---------------------------------------------------------------- per (condition, bank)

def analyse_unit(job):
    cond, bank, rows_by_N, chance, B, seed, depth_key, level, steps_core = job
    out = dict(condition=cond, bank=bank, chance=chance, per_N={})
    pair_tabs = {N: pairs_for(rs, depth_key) for N, rs in rows_by_N.items()}
    out["skipped_N"] = {N: len(t) for N, t in pair_tabs.items() if len(t) < 20}   # incomplete (e.g. a run in progress)
    pair_tabs = {N: t for N, t in pair_tabs.items() if len(t) >= 20}
    common = sorted(set.intersection(*[set(t) for t in pair_tabs.values()])) if pair_tabs else []
    d_all = np.array([pair_tabs[min(pair_tabs)][p][0] for p in common]) if common else np.array([])
    d_m_default = float(np.median(d_all)) if len(d_all) else float("nan")
    ss_seed = np.random.SeedSequence(seed)
    th0 = {}
    for i, N in enumerate(sorted(pair_tabs)):
        tab = pair_tabs[N]
        pairs = list(tab.values())
        bk = SS.bank_from_pairs(f"{bank}@N{N}", chance, pairs)
        u = SS.analyse_bank((bk, B, ss_seed.spawn(1)[0]))
        mb = u["models"]["both"]
        d_m = mb.get("d_m", d_m_default)
        bci = u["boot_ci"]
        draws = u.get("boot_draws", {})
        dm_ci = bci.get("Delta_m_both")
        if dm_ci is None and "Delta_both" in draws:
            dmb = np.array(draws["Delta_both"]) - d_m * (1 - np.array(draws["r_both"]))
            dm_ci = SS.ci(dmb)
        th_ss = np.array([mb["mu"], math.log(mb["beta"]), mb["Delta"], math.log(mb["r"])])
        th0[N] = th_ss
        m_mid = metrics(th_ss, chance, d_m, "mid")
        m_50 = metrics(th_ss, chance, d_m, 0.5)
        dd = collections.defaultdict(lambda: [0, 0, 0])
        for dep, a, b in pairs:
            dd[dep][0] += 1
            dd[dep][1] += a
            dd[dep][2] += b
        # degenerate fit: a parameter on its bound, or key-first not above the floor even at the shallowest depth
        dmin = min(dd)
        n0, k0 = dd[dmin][0], dd[dmin][1]
        p_above = float(stats.binomtest(k0, n0, chance, alternative="greater").pvalue)
        on_bound = [nm for nm, v, (lo, hi) in zip(("mu", "log_beta", "Delta", "log_r"), th_ss, BOUNDS)
                    if v <= lo + 1e-3 or v >= hi - 1e-3]
        # identification: both crossings (default level) inside the tested depth range +- 1 step
        mlev = metrics(th_ss, chance, d_m, level)
        dlo, dhi = min(dd) - 1, max(dd) + 1
        extrap = [a for a in ("cross_kf", "cross_kl") if not (dlo <= mlev[a] <= dhi)]
        degenerate = bool(on_bound) or p_above > 0.01 or bool(extrap)
        out["per_N"][N] = dict(
            n_pairs=len(pairs), d_m=d_m, Delta_m_ss=mb.get("Delta_m"),
            degenerate=degenerate, on_bound=on_bound, p_kf_above_floor_at_dmin=p_above, extrapolated=extrap,
            both_mid=m_mid, both_50=m_50, ss_both={k: mb[k] for k in ("mu", "beta", "Delta", "r", "LL", "cross_kf", "cross_kl", "gap", "ratio")},
            boot_ci={k: bci[k] for k in bci}, Delta_m_ci=dm_ci,
            shift_vs_scale=u["shift_vs_scale"], reading=u["reading"],
            acc=[dict(dep=k, n=v[0], acc_kf=v[1] / v[0], acc_kl=v[2] / v[0]) for k, v in sorted(dd.items())])
    # ---- joint pair bootstrap of the slope of each penalty on log N (core grid, common pairs)
    Ns = [N for N in sorted(pair_tabs) if N in steps_core and not out["per_N"][N]["degenerate"]]
    out["slope_excluded_degenerate"] = [N for N in sorted(pair_tabs) if N in steps_core and out["per_N"][N]["degenerate"]]
    out["slope"] = {}
    if len(Ns) >= 3 and common:
        rng = np.random.default_rng(seed + 7)
        arrs = {N: (np.array([pair_tabs[N][p][0] for p in common]), np.array([pair_tabs[N][p][1] for p in common], float),
                    np.array([pair_tabs[N][p][2] for p in common], float)) for N in Ns}
        x = np.log(np.array(Ns, float))
        d_m = out["per_N"][Ns[0]]["d_m"]
        own = {}
        for N in Ns:
            dep, a, b = arrs[N]
            own[N] = fit_both(agg_from(dep, a, b, np.ones(len(common))), chance, [th0[N]])
            out["per_N"][N]["own_fit_abs_dmu"] = float(abs(own[N][0] - th0[N][0]))

        def slopes(ths):
            res = {}
            for lv in ("mid", 0.5):
                M = [metrics(ths[N], chance, d_m, lv) for N in Ns]
                for key in ("ratio", "r", "Delta_m", "gap", "cross_kf", "cross_kl"):
                    y = np.array([m[key] for m in M])
                    res[f"{key}@{lv}"] = float(np.polyfit(x, y, 1)[0]) if np.all(np.isfinite(y)) else float("nan")
            return res
        point = slopes(th0)
        draws = collections.defaultdict(list)
        for _ in range(B):
            w = rng.multinomial(len(common), np.full(len(common), 1 / len(common))).astype(float)
            ths = {N: fit_both(agg_from(arrs[N][0], arrs[N][1], arrs[N][2], w), chance, [own[N]]) for N in Ns}
            for k, v in slopes(ths).items():
                draws[k].append(v)
        for k in point:
            v = np.array(draws[k])
            ok = np.isfinite(v)
            out["slope"][k] = dict(slope=point[k], ci=SS.ci(v), n_ok=int(ok.sum()), B=B,
                                   p_neg=float(np.mean(v[ok] < 0)) if ok.any() else float("nan"), draws=v.tolist())
        out["slope_Ns"] = Ns
        out["n_common_pairs"] = len(common)
    return out


# ---------------------------------------------------------------- continuous regression

def paired_penalty(rows, depth_key, steps_core, B, seed):
    """Model-free view: per (bank, depth, N) the mean paired penalty kf - kl in normalised gold log-prob,
    with a pair-bootstrap CI, and per (bank, depth) the OLS slope of that penalty on log N over the core
    grid (same pairs at every N, so one resample of pairs is applied to all N)."""
    rng = np.random.default_rng(seed + 11)
    T = collections.defaultdict(dict)                    # (bank, dep) -> pid -> N -> [kf, kl]
    for r in rows:
        T[(r["bank"], r[depth_key])].setdefault(r["pair_id"], {}).setdefault(r["num_steps"], {})[r["arm"]] = r["gold_lp_norm"]
    out = collections.defaultdict(dict)
    for (b, dep), P in sorted(T.items()):
        Ns = sorted({N for v in P.values() for N in v})
        pids = [p for p, v in P.items() if all(N in v and len(v[N]) == 2 for N in Ns)]
        if len(pids) < 10:
            continue
        M = np.array([[P[p][N]["kf"] - P[p][N]["kl"] for N in Ns] for p in pids])      # pairs x N
        idx = rng.integers(0, len(pids), size=(B, len(pids)))
        boots = M[idx].mean(axis=1)                                                     # B x N
        cells = {N: dict(mean=float(M[:, j].mean()), ci=SS.ci(boots[:, j])) for j, N in enumerate(Ns)}
        cj = [j for j, N in enumerate(Ns) if N in steps_core]
        slope = None
        if len(cj) >= 3:
            x = np.log(np.array([Ns[j] for j in cj], float))
            sl = np.polyfit(x, boots[:, cj].T, 1)[0]
            slope = dict(slope=float(np.polyfit(x, M[:, cj].mean(axis=0), 1)[0]), ci=SS.ci(sl),
                         p_neg=float(np.mean(sl < 0)), Ns=[Ns[j] for j in cj])
        out[b][dep] = dict(n_pairs=len(pids), cells=cells, slope=slope)
    return out


def regressions(rows, depth_key, steps_core):
    import pandas as pd
    import statsmodels.formula.api as smf
    df = pd.DataFrame([dict(bank=r["bank"], pair=r["pair_id"], kl=int(r["arm"] == "kl"), dep=float(r[depth_key]),
                            logN=math.log(r["num_steps"]), y=r["gold_lp_norm"], N=r["num_steps"]) for r in rows])
    df = df[df.N.isin(steps_core)].copy()
    out = {}
    if df.empty:
        return out
    df["dep"] = df["dep"] - df["dep"].mean()
    df["logN"] = df["logN"] - df["logN"].mean()
    for name, sub, f in [(b, df[df.bank == b], "y ~ kl * dep * logN") for b in sorted(df.bank.unique())] + \
                        [("pooled", df, "y ~ C(bank) * (kl + dep + logN + kl:dep + kl:logN + dep:logN) + kl:dep:logN")]:
        if sub.pair.nunique() < 5:
            continue
        groups = pd.factorize(sub.pair)[0]
        fit = smf.ols(f, data=sub).fit(cov_type="cluster", cov_kwds={"groups": groups})
        keep = [k for k in fit.params.index if "C(bank)" not in k]
        if name == "pooled":                                     # lower-order terms there are the reference bank's
            keep = [k for k in keep if k == "kl:dep:logN"]
        out[name] = dict(n=int(len(sub)), n_pairs=int(sub.pair.nunique()),
                         coef={k: float(fit.params[k]) for k in keep}, se={k: float(fit.bse[k]) for k in keep},
                         p={k: float(fit.pvalues[k]) for k in keep}, formula=f)
    return out


# ---------------------------------------------------------------- report / plots

def f2(x, nd=2):
    return "—" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{nd}f}"


def fci(v, nd=2):
    return "[—]" if v is None else f"[{f2(v[0], nd)}, {f2(v[1], nd)}]"


def kf_table(rows):
    T = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r["arm"] == "kf":
            T[(r["bank"], r["num_steps"])][0] += 1
            T[(r["bank"], r["num_steps"])][1] += r["correct"]
    return T


def report(res):
    L = [f"# Huginn loop sweep: {res['tag']}", "",
         f"Source: {res['source']}. Rows: {res['n_rows']}. Bootstrap: {res['B']} pair resamples. "
         f"Depth: `{res['depth_key']}`. Default crossing level: {'floor-adjusted midpoint c + (1-c)/2' if res['level'] == 'mid' else res['level']}. "
         f"Core grid for the slope tests: {res['core']}.", "",
         "Penalty metrics (key-last vs key-first, `both` model): crossing ratio kf/kl (> 1 = key-last crosses shallower), "
         "Δ_m (centred gap at the median depth d_m; > 0 = key-last shifted shallower), r (> 1 = key-last pays more per step). "
         "**Prediction if the penalty reflects serial depth after the key: all three shrink with N (negative slopes on log N), "
         "and the kl:dep:logN coefficient of the continuous regression is positive.**", ""]
    if res.get("matched"):
        L += [f"**Matched comparison:** every condition restricted to the {res['matched']['n_pairs']} pairs and "
              f"num_steps {res['matched']['num_steps']} that all conditions share.", ""]
    if res.get("simulated"):
        L += [f"**Synthetic fixture.** {res['sim_truth']}", ""]
    for cond, C in res["conditions"].items():
        L += [f"## Condition: {cond}", "", "### Key-first accuracy by num_steps (all depths)", "",
              "| bank | " + " | ".join(f"N={N}" for N in C["Ns"]) + " |", "|---|" + "---|" * len(C["Ns"])]
        for b, accs in C["kf_acc"].items():
            L.append(f"| {b} | " + " | ".join(f2(accs.get(str(N), accs.get(N)), 3) for N in C["Ns"]) + " |")
        L += ["", "### Accuracy by depth (kf / kl)", ""]
        for u in C["units"]:
            Ns = sorted(u["per_N"], key=int)
            deps = [a["dep"] for a in u["per_N"][Ns[0]]["acc"]]
            L += [f"**{u['bank']}** (floor {u['chance']:.3f})", "", "| N | " + " | ".join(f"d={d:g}" for d in deps) + " |",
                  "|---|" + "---|" * len(deps)]
            for N in Ns:
                a = {x["dep"]: x for x in u["per_N"][N]["acc"]}
                L.append(f"| {N} | " + " | ".join(f"{a[d]['acc_kf']:.2f} / {a[d]['acc_kl']:.2f}" if d in a else "—" for d in deps) + " |")
            L.append("")
        L += ["### Per-N fits (`both` model)", "",
              "Crossings at the default level; CIs for the 50% crossings, gap, r and Δ_m are SS's per-N pair bootstrap.", "",
              "| bank | N | pairs | kf cross | kl cross | ratio kf/kl | gap | Δ_m [CI] | r [CI] | 50%: kf / kl | 50% gap [CI] | shift vs scale | own-fit abs dmu |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for u in C["units"]:
            for N in sorted(u["per_N"], key=int):
                p = u["per_N"][N]
                m, m5 = p["both_mid" if res["level"] == "mid" else "both_50"], p["both_50"]
                if p.get("degenerate"):
                    why = (["on bound: " + ", ".join(p["on_bound"])] if p["on_bound"] else []) + \
                          (["kf not above floor at the shallowest depth"] if p["p_kf_above_floor_at_dmin"] > 0.01 else []) + \
                          (["extrapolated " + ", ".join(p.get("extrapolated", []))] if p.get("extrapolated") else [])
                    m = p["both_mid" if res["level"] == "mid" else "both_50"]
                    L.append(f"| {u['bank']} | {N} | {p['n_pairs']} | *not identified* ({'; '.join(why)}; "
                             f"crossings {f2(m['cross_kf'])} / {f2(m['cross_kl'])}) | | | | | | | | | |")
                    continue
                L.append(f"| {u['bank']} | {N} | {p['n_pairs']} | {f2(m['cross_kf'])} | {f2(m['cross_kl'])} | {f2(m['ratio'], 3)} | "
                         f"{f2(m['gap'])} | {f2(m['Delta_m'])} {fci(p['Delta_m_ci'])} | {f2(m['r'], 3)} {fci(p['boot_ci'].get('r_both'), 3)} | "
                         f"{f2(m5['cross_kf'])} / {f2(m5['cross_kl'])} | {f2(m5['gap'])} {fci(p['boot_ci'].get('gap_both'))} | "
                         f"{p['reading']} | {f2(p.get('own_fit_abs_dmu'), 4)} |")
        L += ["", "### Main test: slope of the penalty on log(num_steps), joint pair bootstrap", "",
              "Only identified N enter a bank's slope (not identified = a `both` parameter on its bound, key-first not "
              "above the floor at the shallowest depth (binomial p > 0.01), or a crossing outside the tested depths +- 1). "
              "N used per bank: "
              + "; ".join(f"{u['bank']} {u.get('slope_Ns', [])}" for u in C["units"]) + ". At least 3 are needed.", "",
              "| bank | metric | slope per unit log N | 95% CI | P(slope < 0) | usable draws |", "|---|---|---|---|---|---|"]
        lv = "mid" if res["level"] == "mid" else "0.5"
        for u in C["units"]:
            for key in ("ratio", "Delta_m", "r"):
                s = u["slope"].get(f"{key}@{lv}")
                if s:
                    L.append(f"| {u['bank']} | {key} | {s['slope']:+.3f} | {fci(s['ci'], 3)} | {f2(s['p_neg'], 3)} | {s['n_ok']}/{s['B']} |")
        if C.get("slope_mean"):
            for key, s in C["slope_mean"].items():
                L.append(f"| mean over banks | {key} | {s['slope']:+.3f} | {fci(s['ci'], 3)} | {f2(s['p_neg'], 3)} | {s['n_ok']}/{s['B']} |")
        L += ["", "### Model-free: paired gold log-prob penalty kf − kl, per depth and N", "",
              "Mean over pairs of log p(gold | kf) − log p(gold | kl), both normalised over the candidate set; "
              "> 0 = key-last worse. 95% pair-bootstrap CIs. Last column: OLS slope of the penalty on log N over the core grid "
              "(joint resample of pairs across N); negative = the penalty shrinks with recurrence.", ""]
        for b, D in C["paired"].items():
            Nb = sorted({N for v in D.values() for N in v["cells"]})
            L += [f"**{b}**", "", "| depth | pairs | " + " | ".join(f"N={N}" for N in Nb) + " | slope on log N [CI] |",
                  "|---|---|" + "---|" * len(Nb) + "---|"]
            for dep, v in sorted(D.items()):
                sl = v["slope"]
                L.append(f"| {dep:g} | {v['n_pairs']} | " + " | ".join(
                    f"{v['cells'][N]['mean']:+.2f} {fci(v['cells'][N]['ci'])}" if N in v["cells"] else "—" for N in Nb)
                    + (f" | {sl['slope']:+.3f} {fci(sl['ci'], 3)} |" if sl else " | — |"))
            L.append("")
        L += ["", "### Continuous version: gold log-prob (normalised over candidates) ~ kl × depth × log N, SEs clustered by pair", "",
              "| fit | n rows | pairs | kl | kl:dep | kl:logN | **kl:dep:logN** (p) | dep:logN |", "|---|---|---|---|---|---|---|---|"]
        for name, g in C["regression"].items():
            c, se, pv = g["coef"], g["se"], g["p"]

            def cs(k):
                return f"{c[k]:+.4f} ± {se[k]:.4f}" if k in c else "—"
            L.append(f"| {name} | {g['n']} | {g['n_pairs']} | {cs('kl')} | {cs('kl:dep')} | {cs('kl:logN')} | "
                     f"**{cs('kl:dep:logN')}** ({pv.get('kl:dep:logN', float('nan')):.3g}) | {cs('dep:logN')} |")
        L += ["", "Caveat: the regression is linear in log-prob, which is compressed at the floor and the ceiling, so "
              "the sign of kl:dep:logN is not a clean test on its own. On the synthetic fixture (`--simulate`), where the "
              "truth is a key-last shift that shrinks with log N at r = 1 in logit space, kl:dep:logN comes out "
              "negative. Read it together with the logit-space slopes above.", ""]
        L += ["", "Figures: " + ", ".join(f"`{os.path.relpath(p, os.path.join(HERE, 'results'))}`" for p in C["figs"]), ""]
    return "\n".join(L)


def plots(res, rows_by_cond, figdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(figdir, exist_ok=True)
    figs = {}
    for cond, C in res["conditions"].items():
        rows = rows_by_cond[cond]
        banks = [u["bank"] for u in C["units"]]
        Ns = C["Ns"]
        paths = []
        cmap = plt.get_cmap("viridis")
        # 1. mean normalised gold log-prob vs depth, per arm, one line per N
        fig, axes = plt.subplots(len(banks), 2, figsize=(9, 3.0 * len(banks)), squeeze=False, sharey="row")
        for i, b in enumerate(banks):
            for j, arm in enumerate(("kf", "kl")):
                ax = axes[i, j]
                for k, N in enumerate(Ns):
                    g = collections.defaultdict(list)
                    for r in rows:
                        if r["bank"] == b and r["arm"] == arm and r["num_steps"] == N:
                            g[r[res["depth_key"]]].append(r["gold_lp_norm"])
                    ds = sorted(g)
                    m = [np.mean(g[d]) for d in ds]
                    se = [np.std(g[d], ddof=1) / math.sqrt(len(g[d])) if len(g[d]) > 1 else 0 for d in ds]
                    ax.errorbar(ds, m, yerr=se, color=cmap(k / max(1, len(Ns) - 1)), marker="o", ms=3, lw=1, capsize=2, label=f"N={N}")
                ch = np.mean([r["chance"] for r in rows if r["bank"] == b])
                ax.axhline(math.log(ch), color="gray", ls=":", lw=0.8)
                ax.set_title(f"{b}, {'key-first' if arm == 'kf' else 'key-last'}", fontsize=10)
                ax.set_xlabel("dependent depth")
                ax.set_ylabel("mean log p(gold), normalised")
            axes[i, 0].legend(fontsize=7, ncol=2)
        fig.suptitle(f"Huginn: gold log-prob vs depth ({cond})", fontsize=11)
        fig.tight_layout()
        p = os.path.join(figdir, f"goldlp_vs_depth__{cond}.png")
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths.append(p)
        # 2. accuracy vs depth per arm with the both-model fit, one panel per (bank, N)
        fig, axes = plt.subplots(len(banks), len(Ns), figsize=(2.6 * len(Ns), 2.5 * len(banks)), squeeze=False, sharey=True)
        for i, u in enumerate(C["units"]):
            for j, N in enumerate(Ns):
                ax = axes[i, j]
                pn = u["per_N"].get(N) or u["per_N"].get(str(N))
                if not pn:
                    ax.axis("off")
                    continue
                ds = np.array([a["dep"] for a in pn["acc"]])
                xx = np.linspace(ds.min(), ds.max(), 60)
                m = pn["both_mid"]
                for arm, col in (("kf", KF_COL), ("kl", KL_COL)):
                    ax.plot(ds, [a[f"acc_{arm}"] for a in pn["acc"]], "o", color=col, ms=3)
                    z = m["beta"] * (m["mu"] - xx) if arm == "kf" else m["beta"] * (m["mu"] - m["Delta"] - m["r"] * xx)
                    ax.plot(xx, u["chance"] + (1 - u["chance"]) * expit(z), "-", color=col, lw=0.9)
                ax.axhline(u["chance"], color="gray", ls=":", lw=0.7)
                ax.set_ylim(-0.02, 1.02)
                ax.set_title(f"{u['bank']} N={N}", fontsize=8)
        fig.suptitle(f"Accuracy vs dependent depth (blue kf, orange kl) with `both` fits ({cond})", fontsize=10)
        fig.tight_layout()
        p = os.path.join(figdir, f"acc_vs_depth__{cond}.png")
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths.append(p)
        # 3. penalty vs log N
        lv = "mid" if res["level"] == "mid" else 0.5
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
        for ax, key, ref in zip(axes, ("ratio", "Delta_m", "r"), (1, 0, 1)):
            for k, u in enumerate(C["units"]):
                Nu = [N for N in sorted(u["per_N"], key=int)]
                y = [u["per_N"][N]["both_mid" if lv == "mid" else "both_50"][key] for N in Nu]
                ax.plot(np.log(np.array(Nu, float)), y, "o-", ms=4, label=u["bank"])
            ax.axhline(ref, color="k", lw=0.5)
            ax.set_xlabel("log num_steps")
            ax.set_title(key, fontsize=10)
        axes[0].legend(fontsize=8)
        fig.suptitle(f"Key-last penalty vs recurrence ({cond})", fontsize=10)
        fig.tight_layout()
        p = os.path.join(figdir, f"penalty_vs_logN__{cond}.png")
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths.append(p)
        # 4. key-first accuracy vs N
        fig, ax = plt.subplots(figsize=(5.5, 3.6))
        for b in banks:
            a = C["kf_acc"][b]
            ax.plot(Ns, [a.get(N, a.get(str(N))) for N in Ns], "o-", label=b)
        ax.set_xscale("log", base=2)
        ax.set_xlabel("num_steps")
        ax.set_ylabel("key-first accuracy (all depths)")
        ax.legend(fontsize=8)
        fig.tight_layout()
        p = os.path.join(figdir, f"kf_acc_vs_steps__{cond}.png")
        fig.savefig(p, dpi=120)
        plt.close(fig)
        paths.append(p)
        figs[cond] = paths
    return figs


# ---------------------------------------------------------------- synthetic fixture

def simulate(path, seed=0):
    """Pairs with an item effect shared across arms and N; key-first improves with log N and the
    key-last shift shrinks with log N (true Delta_m slope < 0, r = 1)."""
    rng = np.random.default_rng(seed)
    banks = {"sim_chain": (1 / 9, [1, 2, 3, 4, 5, 6]), "sim_brew": (0.25, [1, 2, 3, 4, 5])}
    Ns = [1, 2, 4, 8, 16, 32, 64]
    rows = []
    for b, (c, deps) in banks.items():
        for d in deps:
            for k in range(120):
                pid = f"{b}|d{d}|{k}"
                u = rng.normal(0, 0.6)
                for N in Ns:
                    mu = 0.5 + 0.8 * math.log2(N)
                    D = max(0.0, 1.6 - 0.3 * math.log2(N))
                    for arm in ("kf", "kl"):
                        z = 1.1 * (mu - d) + u if arm == "kf" else 1.1 * (mu - D - d) + u
                        p = c + (1 - c) * expit(z)
                        y = int(rng.random() < p)
                        pg = float(np.clip(p + rng.normal(0, 0.05), 1e-4, 1 - 1e-4))
                        rows.append(dict(problem_number=f"{pid}|{arm}", pair_id=pid, bank=b, arm=arm, nominal_depth=d,
                                         dependent_depth=d, chance=c, num_steps=N, mode="full", n_lo=None,
                                         init_scale=1.0, init_seed=0, correct=y, gold_lp_norm=math.log(pg),
                                         p_gold_norm=pg))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return ("synthetic banks sim_chain (floor 1/9, depths 1-6) and sim_brew (floor 1/4, depths 1-5), 120 pairs/depth; "
            "kf mu = 0.5 + 0.8 log2 N, beta 1.1; key-last shift Delta = max(0, 1.6 - 0.3 log2 N), r = 1; shared item effect "
            "sd 0.6. Truth: Delta_m and the ratio fall with log N (negative slopes; Delta_m slope ≈ -0.43 per unit ln N "
            "until it hits 0), r slope 0, kl:dep:logN ≈ 0 in logit space.")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="*", default=[os.path.join(HERE, "results", "runs", "huginn__*.jsonl")])
    ap.add_argument("--tag", default="sweep")
    ap.add_argument("--B", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--depth", default="dependent_depth", choices=["dependent_depth", "nominal_depth"])
    ap.add_argument("--cross-level", default="mid", help="'mid' (floor-adjusted midpoint) or a probability, e.g. 0.5")
    ap.add_argument("--core", default=",".join(map(str, CORE)), help="num_steps used in the slope tests")
    ap.add_argument("--banks", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--match-conditions", action="store_true",
                    help="restrict every condition (full, per-token) to the pairs and num_steps they all share")
    a = ap.parse_args()
    level = "mid" if a.cross_level == "mid" else float(a.cross_level)
    core = [int(x) for x in a.core.split(",")]
    res = dict(B=a.B, depth_key=a.depth, level=level, core=core)
    if a.simulate:
        fx = os.path.join(HERE, "results", "sim", "huginn__simfixture.jsonl")
        res["sim_truth"] = simulate(fx, a.seed)
        res["simulated"] = True
        a.runs, a.tag = [fx], "simulate"
    rows = [r for r in load(a.runs) if "timing" not in r]
    rows = [r for r in rows if "correct" in r]
    if a.banks:
        rows = [r for r in rows if r["bank"] in a.banks]
    by_cond = collections.defaultdict(list)
    for r in rows:
        by_cond[cond_name(r)].append(r)
    if a.match_conditions and len(by_cond) > 1:              # same pairs and the same N in every condition
        pids = set.intersection(*[{r["pair_id"] for r in rs} for rs in by_cond.values()])
        Ns = set.intersection(*[{r["num_steps"] for r in rs} for rs in by_cond.values()])
        rows = [r for r in rows if r["pair_id"] in pids and r["num_steps"] in Ns]
        by_cond = collections.defaultdict(list)
        for r in rows:
            by_cond[cond_name(r)].append(r)
        core = [N for N in core if N in Ns]
        res["core"] = core
        res["matched"] = dict(n_pairs=len(pids), num_steps=sorted(Ns))
    res.update(tag=a.tag, source=", ".join(a.runs), n_rows=len(rows))
    jobs = []
    for cond, rs in by_cond.items():
        byb = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rs:
            byb[r["bank"]][r["num_steps"]].append(r)
        for b, byN in sorted(byb.items()):
            chance = float(np.mean([r["chance"] for r in rs if r["bank"] == b]))
            jobs.append((cond, b, dict(byN), chance, a.B, a.seed + len(jobs), a.depth, level, core))
    if a.workers > 1 and len(jobs) > 1:
        with Pool(min(a.workers, len(jobs))) as pool:
            units = pool.map(analyse_unit, jobs)
    else:
        units = [analyse_unit(j) for j in jobs]
    res["conditions"] = {}
    for cond, rs in by_cond.items():
        U = [u for u in units if u["condition"] == cond]
        Ns = sorted({r["num_steps"] for r in rs})
        T = kf_table(rs)
        kf_acc = {u["bank"]: {N: T[(u["bank"], N)][1] / T[(u["bank"], N)][0] for N in Ns if T[(u["bank"], N)][0]} for u in U}
        C = dict(units=U, Ns=Ns, kf_acc=kf_acc, regression=regressions(rs, a.depth, core),
                 paired=paired_penalty(rs, a.depth, core, a.B, a.seed))
        lv = "mid" if level == "mid" else "0.5"
        sm = {}                                                  # mean slope over banks (banks resampled independently)
        for key in ("ratio", "Delta_m", "r"):
            ss = [u["slope"][f"{key}@{lv}"] for u in U if f"{key}@{lv}" in u["slope"]]
            if len(ss) >= 2:
                D = np.mean(np.array([s["draws"] for s in ss]), axis=0)
                ok = np.isfinite(D)
                sm[key] = dict(slope=float(np.mean([s["slope"] for s in ss])), ci=SS.ci(D), n_ok=int(ok.sum()), B=a.B,
                               p_neg=float(np.mean(D[ok] < 0)) if ok.any() else float("nan"), banks=[u["bank"] for u in U])
        C["slope_mean"] = sm
        for u in U:
            for s in u["slope"].values():
                s.pop("draws", None)
        res["conditions"][cond] = C
    figdir = os.path.join(HERE, "results", "figs", f"huginn__{a.tag}")
    figs = plots(res, by_cond, figdir)
    for cond in res["conditions"]:
        res["conditions"][cond]["figs"] = figs[cond]
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    jp = os.path.join(HERE, "results", f"huginn__{a.tag}.json")
    json.dump(res, open(jp, "w"), indent=1, default=float)
    md = report(res)
    mp = os.path.join(HERE, "results", f"report__huginn__{a.tag}.md")
    open(mp, "w").write(md)
    print(md)
    print(jp, mp, sep="\n")


if __name__ == "__main__":
    main()
