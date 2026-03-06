#!/usr/bin/env python3
"""
make_1mut_table.py

Creates a compiled table from parameter files, binary outputs, and LZ values.

Usage (example):
python3 make_1mut_table.py \
    --params-dir /path/to/parameters \
    --binary-dir /path/to/binary_out \
    --lz-dir /path/to/lz_values \
    --output /path/to/output/compiled_1mut.txt

Optional args:
    --param-pattern   pattern for parameter files (default: parameters{}.txt)
    --binary-pattern  pattern for binary files (default: binary{}.txt)
    --lz-pattern      pattern for lz files (default: k{}.txt)
    --min-binary-len  minimum binary length to consider (default: 5)
"""
import os
import argparse
import glob
import re
import ast
from pathlib import Path

import pandas as pd
import numpy as np

def extract_genotype_from_params(file_path):
    """
    Extract indices_temp list from parameters file robustly.
    Returns list[int] or None.
    """
    try:
        text = Path(file_path).read_text()
    except Exception as e:
        print(f"Error reading params file {file_path}: {e}")
        return None

    # Look for a Python-like list assignment: indices_temp = [ ... ]
    m = re.search(r'indices_temp\s*=\s*(\[[^\]]*\])', text, re.DOTALL)
    if not m:
        # fallback: try a looser search capturing across newlines
        m = re.search(r'indices_temp\s*=\s*\[(.*?)\]', text, re.DOTALL)
    if not m:
        # nothing found
        return None

    list_text = m.group(1)
    try:
        # Safely evaluate the list using ast.literal_eval (handles whitespace, trailing commas)
        parsed = ast.literal_eval(list_text)
        # Ensure it's a list of ints
        return [int(x) for x in parsed]
    except Exception:
        # Last resort: parse manually splitting on commas
        try:
            tokens = [t.strip() for t in re.split(r',|\s+', list_text) if t.strip() and t.strip() not in ('[', ']')]
            return [int(t.strip().strip(',')) for t in tokens]
        except Exception:
            return None

def read_binary_from_file(binary_path, min_len=5):
    """
    Read binary string from file. Return the first long-ish sequence of 0/1 characters found.
    """
    try:
        text = Path(binary_path).read_text()
    except Exception as e:
        print(f"Error reading binary file {binary_path}: {e}")
        return None

    # Find the first run of 0/1 characters of length >= min_len
    m = re.search(r'([01]{%d,})' % min_len, text.replace('\n', ' '))
    if m:
        return m.group(1).strip()
    # fallback: entire file stripped if it looks binary-like
    s = text.strip()
    if set(s).issubset({'0', '1'}) and len(s) >= min_len:
        return s
    return None

def read_lz_value(lz_file_path):
    """
    Extract first numeric (float) from the LZ file.
    Returns float or None.
    """
    try:
        text = Path(lz_file_path).read_text()
    except Exception as e:
        print(f"Error reading LZ file {lz_file_path}: {e}")
        return None

    # look for a float (handles scientific notation)
    m = re.search(r'([-+]?\d*\.\d+([eE][-+]?\d+)?|[-+]?\d+([eE][-+]?\d+)?)', text)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None

def parse_args():
    p = argparse.ArgumentParser(description="Build compiled table from params, binaries and lz values.")
    p.add_argument('--params-dir', required=True, help='Directory containing parameter files')
    p.add_argument('--binary-dir', required=True, help='Directory containing binary files')
    p.add_argument('--lz-dir', required=True, help='Directory containing LZ value files')
    p.add_argument('--output', required=True, help='Output TSV file path')
    p.add_argument('--param-pattern', default='parameters{}.txt', help='Pattern for parameter filenames with {} for number')
    p.add_argument('--binary-pattern', default='binary{}.txt', help='Pattern for binary filenames with {} for number')
    p.add_argument('--lz-pattern', default='k{}.txt', help='Pattern for LZ filenames with {} for number')
    p.add_argument('--min-binary-len', type=int, default=5, help='Minimum binary substring length to accept')
    p.add_argument('--verbose', action='store_true', help='More verbose output')
    return p.parse_args()

def main():
    args = parse_args()

    params_dir = args.params_dir
    binary_dir = args.binary_dir
    lz_dir = args.lz_dir
    output_file = args.output

    param_pattern = args.param_pattern
    binary_pattern = args.binary_pattern
    lz_pattern = args.lz_pattern
    min_bin_len = args.min_binary_len

    # Verify directories
    for d in (params_dir, binary_dir, lz_dir):
        if not os.path.isdir(d):
            print(f"Error: directory not found: {d}")
            return

    # Find all binary files (use glob for pattern binary*.txt)
    binary_glob = os.path.join(binary_dir, binary_pattern.replace('{}', '*'))
    binary_files = sorted(glob.glob(binary_glob))
    print(f"Found {len(binary_files)} binary files (glob: {binary_glob})")

    output_rows = []
    missing_params = 0
    missing_lz = 0
    failed_parsing = 0

    for i, binary_path in enumerate(binary_files, start=1):
        name = os.path.basename(binary_path)
        m = re.search(r'(\d+)', name)
        if not m:
            if args.verbose:
                print(f"Skipping binary file with no number in name: {name}")
            continue
        file_number = int(m.group(1))

        # Derive expected file names using the provided patterns
        param_file = os.path.join(params_dir, param_pattern.format(file_number))
        lz_file = os.path.join(lz_dir, lz_pattern.format(file_number))

        if not os.path.exists(param_file):
            missing_params += 1
            if args.verbose:
                print(f"Missing parameter file for {file_number}: {param_file}")
            continue
        if not os.path.exists(lz_file):
            missing_lz += 1
            if args.verbose:
                print(f"Missing LZ file for {file_number}: {lz_file}")
            continue

        genotype = extract_genotype_from_params(param_file)
        if genotype is None:
            failed_parsing += 1
            if args.verbose:
                print(f"Could not extract genotype from {param_file}")
            continue

        phenotype_binary = read_binary_from_file(binary_path, min_len=min_bin_len)
        if phenotype_binary is None:
            failed_parsing += 1
            if args.verbose:
                print(f"Could not extract binary string from {binary_path}")
            continue

        complexity = read_lz_value(lz_file)
        if complexity is None:
            failed_parsing += 1
            if args.verbose:
                print(f"Could not extract LZ value from {lz_file}")
            continue

        genotype_str = ','.join(map(str, genotype))
        output_rows.append([file_number, genotype_str, phenotype_binary, round(float(complexity), 6)])

        # progress print
        if i % 200 == 0:
            print(f"Processed {i} binary files, collected {len(output_rows)} rows...")

    print(f"\nFinished scanning. Collected {len(output_rows)} rows.")
    if missing_params:
        print(f"Missing parameter files: {missing_params}")
    if missing_lz:
        print(f"Missing LZ files: {missing_lz}")
    if failed_parsing:
        print(f"Files failed parsing: {failed_parsing}")

    # Write DataFrame
    if output_rows:
        df = pd.DataFrame(output_rows, columns=['file_number', 'genotype_raw', 'phenotype_binary', 'complexity_entropy'])
        df = df.sort_values('file_number')
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        df.to_csv(output_file, sep='\t', index=False)
        print(f"Output written to: {output_file}")
        # summary
        print("\nSummary statistics:")
        print(f"Rows: {len(df)}")
        print(f"File number range: {df['file_number'].min()} to {df['file_number'].max()}")
        print(f"Mean complexity: {df['complexity_entropy'].mean():.3f}")
        print(f"Complexity range: {df['complexity_entropy'].min():.3f} to {df['complexity_entropy'].max():.3f}")
        print("\nSample:")
        print(df.head().to_string(index=False))
    else:
        print("No rows collected; nothing to write.")

if __name__ == "__main__":
    main()
