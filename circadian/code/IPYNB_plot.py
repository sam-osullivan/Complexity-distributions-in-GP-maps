#!/usr/bin/env python3
"""
IPYNB_Plot.py

Plots the Lempel-Ziv complexity distribution for rand and 0_mut datasets.

Behavior:
- Auto-detects phenotype and complexity columns.
- Chooses a phenotype length common to both files (or falls back to rand).
- Coerces complexity to numeric and plots both histograms if available.
"""

import os
import sys
from collections import Counter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Paths (update if your 0_mut path differs) ===
file_path_rand = "/mnt/users/osullivans/circ/oct24/t0to50/tables/t0to50_table.txt"
file_path_0_mut = "/mnt/users/osullivans/circ/oct24/t0to50/compiled_0mut.txt"  # verify this path
output_path = "/mnt/users/osullivans/circ/oct24/t0to50/tables/IPYNB_table_plot.png"

def try_read(path):
    """Try a few separators and return (df, sep) or raise."""
    tried = {}
    for sep in ['\t', ',', ';', None]:
        try:
            if sep is None:
                df = pd.read_csv(path)
            else:
                df = pd.read_csv(path, sep=sep)
            if df.shape[0] >= 1 and df.shape[1] >= 2:
                return df, sep
            tried[sep] = f"read but shape={df.shape}"
        except Exception as e:
            tried[sep] = str(e)
    raise RuntimeError(f"Failed to read file {path}; tried separators: {tried}")

def detect_phen_and_comp(df):
    """Return (phen_col, phen_length_counts, comp_col) using heuristics."""
    # phenotype candidates by name
    phen_candidates = [c for c in df.columns if ('phen' in c.lower()) or ('binary' in c.lower())]
    def looks_like_binary_series(s, min_len=5):
        s_str = s.astype(str).str.strip()
        sample = s_str[s_str != ''].dropna().head(500).astype(str)
        if sample.shape[0] == 0:
            return False, None
        only01 = sample.map(lambda x: all(ch in '01' for ch in x))
        frac_only01 = only01.sum() / len(sample)
        lengths = sample[only01].str.len()
        most_common_len = int(lengths.mode().iloc[0]) if not lengths.empty else None
        return (frac_only01 >= 0.7 and most_common_len is not None and most_common_len >= min_len), most_common_len

    phen_col = None
    phen_len_counts = Counter()
    # try name candidates
    for c in phen_candidates:
        ok, mc_len = looks_like_binary_series(df[c])
        if ok:
            phen_col = c
            # full length distribution
            s = df[c].astype(str).str.strip()
            phen_len_counts = Counter(s[s != ''].str.len().dropna().astype(int).tolist())
            break

    # scan all columns if not found by name
    if phen_col is None:
        for c in df.columns:
            ok, mc_len = looks_like_binary_series(df[c])
            if ok:
                phen_col = c
                s = df[c].astype(str).str.strip()
                phen_len_counts = Counter(s[s != ''].str.len().dropna().astype(int).tolist())
                break

    # complexity candidate by name
    comp_candidates = [c for c in df.columns if 'complex' in c.lower() or 'lz' in c.lower() or c.lower() == 'k']
    comp_col = None
    if comp_candidates:
        for name in ['complexity_entropy', 'complexity', 'k', 'lz', 'complexity_value']:
            if name in df.columns:
                comp_col = name
                break
        if comp_col is None:
            comp_col = comp_candidates[0]

    # fallback: any numeric column not phenotype
    if comp_col is None:
        numeric_cols = []
        for c in df.columns:
            if c == phen_col:
                continue
            non_na = pd.to_numeric(df[c], errors='coerce').notna().sum()
            if non_na > 0:
                numeric_cols.append((c, non_na))
        if numeric_cols:
            numeric_cols.sort(key=lambda x: -x[1])
            comp_col = numeric_cols[0][0]

    return phen_col, phen_len_counts, comp_col

# === Read rand file ===
if not os.path.exists(file_path_rand):
    print(f"Error: rand file not found at {file_path_rand}")
    sys.exit(1)

df_rand, sep_rand = try_read(file_path_rand)
print(f"Read rand: {file_path_rand} (sep={repr(sep_rand)}), shape={df_rand.shape}")

phen_col_rand, len_counts_rand, comp_col_rand = detect_phen_and_comp(df_rand)
print(f"Rand: phenotype column='{phen_col_rand}', complexity column='{comp_col_rand}'")
print(f"Rand phenotype length counts (top 5): {len_counts_rand.most_common(5)}")

# === Read 0_mut file (optional) ===
df_0 = None
if os.path.exists(file_path_0_mut):
    try:
        df_0, sep_0 = try_read(file_path_0_mut)
        print(f"Read 0_mut: {file_path_0_mut} (sep={repr(sep_0)}), shape={df_0.shape}")
        phen_col_0, len_counts_0, comp_col_0 = detect_phen_and_comp(df_0)
        print(f"0_mut: phenotype column='{phen_col_0}', complexity column='{comp_col_0}'")
        print(f"0_mut phenotype length counts (top 5): {len_counts_0.most_common(5)}")
    except Exception as e:
        print(f"Warning: failed to read 0_mut file: {e}")
        df_0 = None
else:
    print(f"0_mut file not found at: {file_path_0_mut}  --> continuing with rand only")

# === Decide which phenotype column to use and which length to filter ===
# Prefer using rand's phenotype column (if detected), else 0_mut's
phen_col = phen_col_rand or (phen_col_0 if df_0 is not None else None)
if phen_col is None:
    print("Error: could not detect a phenotype column in either file.")
    sys.exit(1)

# choose length: intersection of top lengths from both datasets if both exist, else rand's most common
rand_top = set([l for l, _ in len_counts_rand.most_common(10)])
if df_0 is not None:
    # get top lengths in 0_mut
    _, len_counts_0, _ = detect_phen_and_comp(df_0)
    zero_top = set([l for l, _ in len_counts_0.most_common(10)])
    common = sorted(list(rand_top & zero_top), reverse=True)
    if common:
        chosen_length = common[0]
        print(f"Using common phenotype length between datasets: {chosen_length}")
    else:
        chosen_length = len_counts_rand.most_common(1)[0][0]
        print(f"No common phenotype length found - falling back to rand's most common length: {chosen_length}")
else:
    chosen_length = len_counts_rand.most_common(1)[0][0]
    print(f"Using rand's most common phenotype length: {chosen_length}")

# === Extract and filter complexity values from rand ===
df_rand['phenotype_str'] = df_rand[phen_col].astype(str).str.strip()
df_rand = df_rand[df_rand['phenotype_str'].str.len() == chosen_length].copy()
df_rand[comp_col_rand] = pd.to_numeric(df_rand[comp_col_rand], errors='coerce')
df_rand = df_rand.dropna(subset=[comp_col_rand])
complexities_rand = df_rand[comp_col_rand]

print(f"Rand: {len(complexities_rand)} rows after filtering (L={chosen_length})")

# === Extract and filter complexity values from 0_mut (if available) ===
complexities_0 = None
if df_0 is not None:
    # use same phen_col for consistency; comp col from 0_mut detection if available else fallback
    comp_col_0 = comp_col_0 if 'comp_col_0' in locals() else comp_col_rand
    # add phenotype_str column name if different
    df_0['phenotype_str'] = df_0[phen_col].astype(str).str.strip() if phen_col in df_0.columns else df_0.iloc[:, 2].astype(str).str.strip()
    df_0 = df_0[df_0['phenotype_str'].str.len() == chosen_length].copy()
    # choose complexity column: prefer 0_mut detected comp_col_0, else comp_col_rand
    comp_to_use = comp_col_0 if (df_0 is not None and comp_col_0 in df_0.columns) else comp_col_rand
    df_0[comp_to_use] = pd.to_numeric(df_0[comp_to_use], errors='coerce')
    df_0 = df_0.dropna(subset=[comp_to_use])
    complexities_0 = df_0[comp_to_use]
    print(f"0_mut: {len(complexities_0)} rows after filtering (L={chosen_length})")

# === Plotting histograms for both datasets ===
if (complexities_rand.empty) and (complexities_0 is None or complexities_0.empty):
    print("No data to plot for either dataset. Exiting.")
    sys.exit(0)

# compute bins covering both datasets
all_values = list(complexities_rand.values)
if complexities_0 is not None:
    all_values += list(complexities_0.values)

min_val = np.floor(min(all_values))
max_val = np.ceil(max(all_values))
bin_width = 1
bins = np.arange(min_val - 0.5, max_val + 1.5, bin_width)

hist_rand, _ = np.histogram(complexities_rand, bins=bins, density=True)
hist_0 = None
if complexities_0 is not None and len(complexities_0) > 0:
    hist_0, _ = np.histogram(complexities_0, bins=bins, density=True)

bin_centers = 0.5 * (bins[:-1] + bins[1:])

fig, ax = plt.subplots(figsize=(12, 8))
bar_width = 0.35

ax.bar(bin_centers - bar_width/2, hist_rand, width=bar_width, label=f"rand (n={len(complexities_rand)}, K={complexities_rand.mean():.2f})", alpha=0.8, edgecolor='k')
if hist_0 is not None:
    ax.bar(bin_centers + bar_width/2, hist_0, width=bar_width, label=f"0_mut (n={len(complexities_0)}, K={complexities_0.mean():.2f})", alpha=0.8, edgecolor='k')

ax.set_title(f"LZ Complexity Distribution (L={chosen_length})", fontsize=16)
ax.set_xlabel("Complexity (Lempel-Ziv)", fontsize=14)
ax.set_ylabel("Frequency (Normalized)", fontsize=14)
ax.legend(fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=12)

os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.tight_layout()
plt.savefig(output_path, dpi=200, bbox_inches='tight')
print(f"Plot saved to: {output_path}")
plt.show()
