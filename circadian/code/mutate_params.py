#!/usr/bin/env python3
"""
mutate_params.py

Read parameters*.txt files from a flat directory,
mutate one allele in indices_temp, update p_scaled accordingly (via PROB ratio),
and write mutated parameters into output directory.

Usage:
    python3 mutate_params.py --input <input_dir> --output <output_dir> [--seed N] [--overwrite]

Assumptions:
- Each parameters file contains a genotype list somewhere like:
    indices_temp = [7, 2, 7, ...]
  and a p_scaled vector somewhere like:
    p_scaled = [1.00e+02 7.50e+01 ...]
  The script is tolerant to whitespace and line breaks in those arrays.
"""
import argparse
import ast
import math
import os
import random
import re
import sys
from pathlib import Path
from datetime import datetime
import shutil

import numpy as np

# PROB as you specified
PROB = np.linspace(0.25, 2.0, 8)  # [0.25,0.5,0.75,1.0,1.25,1.5,1.75,2.0]

# regex to find a bracketed [...] substring (non-greedy)
BRACKET_RE = re.compile(r'\[.*?\]', re.S)

# float regex to extract numeric tokens (handles scientific notation)
FLOAT_RE = re.compile(r'[-+]?\d*\.\d+([eE][-+]?\d+)?|[-+]?\d+[eE][-+]?\d+|[-+]?\d+')

def find_first_bracketed(text):
    m = BRACKET_RE.search(text)
    return m.group(0) if m else None

def parse_indices(text):
    """
    Locate the first bracketed list and parse it as Python list of ints.
    """
    b = find_first_bracketed(text)
    if not b:
        return None
    try:
        obj = ast.literal_eval(b)
        return [int(x) for x in obj]
    except Exception:
        # fallback: extract integers directly
        nums = re.findall(r'\d+', b)
        if len(nums) >= 15:
            return [int(x) for x in nums[:15]]
        return None

def parse_p_scaled(text):
    """
    Locate first bracketed substring after 'p_scaled' or any bracketed substring and extract floats.
    Returns list of floats or None.
    """
    # try to find 'p_scaled' followed by bracketed expression first
    m = re.search(r'p_scaled\s*=\s*(\[[^\]]*\])', text, re.S)
    if m:
        bracket = m.group(1)
    else:
        bracket = find_first_bracketed(text)
    if not bracket:
        return None
    # extract floats from bracket (works even if commas are missing)
    tokens = FLOAT_RE.findall(bracket)
    # FLOAT_RE.findall returns tuples if group present, unify:
    # simpler: use finditer to get full matches
    tokens = [mo.group(0) for mo in FLOAT_RE.finditer(bracket)]
    try:
        vals = [float(x) for x in tokens]
        return vals
    except Exception:
        return None

def mutate_one_locus(indices):
    """
    Choose a random locus and mutate its allele to a different value 0..7.
    Returns (mutated_indices, locus, old, new).
    """
    if len(indices) < 15:
        raise ValueError("genotype length < 15")
    i = random.randrange(15)
    old = int(indices[i])
    choices = [v for v in range(8) if v != old]
    new = random.choice(choices)
    out = list(indices)
    out[i] = new
    return out, i, old, new

def update_p_scaled_by_ratio(p_scaled, locus, old_allele, new_allele):
    """
    Update p_scaled in-place (or return new list) by multiplying element at locus
    by PROB[new] / PROB[old]. Returns a new list of floats.
    """
    if locus >= len(p_scaled):
        raise IndexError("p_scaled length shorter than expected")
    ratio = float(PROB[new_allele] / PROB[old_allele])
    new_p = list(p_scaled)
    new_p[locus] = new_p[locus] * ratio
    return new_p

def format_p_scaled(p_scaled):
    """
    Format p_scaled as a bracketed list with values in scientific notation,
    separated by spaces, and line-wrapped to ~8 values per line for readability.
    """
    fmt_vals = [f"{v:.2e}" for v in p_scaled]
    per_line = 8
    lines = []
    for i in range(0, len(fmt_vals), per_line):
        lines.append(" ".join(fmt_vals[i:i+per_line]))
    inside = ("\n ").join(lines)  # indent subsequent lines for readability
    return "[{}]".format(inside)

def process_one_file(src_path, dst_path, seed):
    text = src_path.read_text()
    indices = parse_indices(text)
    if indices is None:
        raise ValueError("Could not parse indices_temp list")
    p_scaled = parse_p_scaled(text)
    if p_scaled is None:
        raise ValueError("Could not parse p_scaled list")

    if len(indices) < 15:
        raise ValueError(f"indices length {len(indices)} < 15")
    if len(p_scaled) < 15:
        raise ValueError(f"p_scaled length {len(p_scaled)} < 15")

    mutated_indices, locus, old, new = mutate_one_locus(indices)
    new_p_scaled = update_p_scaled_by_ratio(p_scaled, locus, old, new)

    # write mutated file: preserve minimal relevant format
    with dst_path.open("w") as out:
        out.write(f"indices_temp = {mutated_indices}\n")
        out.write("p_scaled = ")
        out.write(format_p_scaled(new_p_scaled))
        out.write("\n")
        out.write(f"# from: {src_path}\n")
        out.write(f"# mutated_locus: {locus}\n")
        out.write(f"# old_allele: {old}\n")
        out.write(f"# new_allele: {new}\n")
        out.write(f"# seed: {seed}\n")
        out.write(f"# timestamp: {datetime.utcnow().isoformat()}Z\n")

def process_flat_directory(input_dir: Path, output_dir: Path, seed=None, overwrite=False):
    """
    Process a flat directory of parameters*.txt files (no group subdirectories).
    """
    if seed is not None:
        random.seed(seed)

    if output_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Output directory {output_dir} exists; use --overwrite to allow replacement.")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Find all parameters*.txt files in the input directory
    src_files = sorted([p for p in input_dir.iterdir() 
                       if p.is_file() and p.name.startswith("parameters") and p.name.endswith(".txt")])
    
    if not src_files:
        raise FileNotFoundError(f"No parameters*.txt files found in {input_dir}")

    total = 0
    errors = []

    print(f"Found {len(src_files)} parameter files to process...")

    for src in src_files:
        dst = output_dir / src.name
        try:
            process_one_file(src, dst, seed)
            total += 1
            
            # Progress indicator
            if total % 100 == 0:
                print(f"Processed {total}/{len(src_files)} files...")
                
        except Exception as e:
            errors.append((src, str(e)))

    return total, errors

def main():
    ap = argparse.ArgumentParser(description="Mutate one locus in each parameters*.txt, updating p_scaled by PROB ratio.")
    ap.add_argument("--input", required=True, help="Input directory containing parameters*.txt files")
    ap.add_argument("--output", required=True, help="Output directory to write mutated parameters")
    ap.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing output directory if present")
    args = ap.parse_args()

    inp = Path(args.input).resolve()
    out = Path(args.output).resolve()
    
    if not inp.is_dir():
        print(f"Error: input directory not found: {inp}", file=sys.stderr)
        sys.exit(1)

    try:
        total, errors = process_flat_directory(inp, out, seed=args.seed, overwrite=args.overwrite)
    except Exception as e:
        print("Fatal error:", e, file=sys.stderr)
        sys.exit(1)

    print(f"\nProcessed {total} parameter files. Output written to: {out}")
    if errors:
        print("\nErrors (files skipped):")
        for src, msg in errors[:10]:
            print(f" {src.name}: {msg}")
        if len(errors) > 10:
            print(f" ... and {len(errors)-10} more")

if __name__ == "__main__":
    main()
