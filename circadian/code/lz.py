#!/usr/bin/env python3
# lz.py — KC_LZ-based (Pascal-style) Lempel–Ziv complexity for binary strings
# Usage: python3 lz.py <input_dir> <output_dir>
#
# Reads:  <input_dir>/binaryN.txt  (one line: 0/1 string)
# Writes: <output_dir>/kN.txt      (one line: KC value with 2 decimals)

import os
import sys
import numpy as np

def KC_LZ(string: str) -> int:
    """
    Lempel–Ziv parse count using the KC_LZ algorithm (as in pascal_v2.py).
    """
    n = len(string)
    s = '0' + string
    c = 1
    l = 1
    i = 0
    k = 1
    k_max = 1
    stop = 0

    while stop == 0:
        if s[i + k] != s[l + k]:
            if k > k_max:
                k_max = k
            i = i + 1
            if i == l:
                c = c + 1
                l = l + k_max
                if l + 1 > n:
                    stop = 1
                else:
                    i = 0
                    k = 1
                    k_max = 1
            else:
                k = 1
        else:
            k = k + 1
            if l + k > n:
                c = c + 1
                stop = 1
    return c

def calc_KC(s: str) -> float:
    """
    Bidirectional KC with log2(L) normalization.
    - If s is all-0s or all-1s, returns log2(L).
    - Otherwise returns log2(L) * (KC_LZ(s) + KC_LZ(s[::-1])) / 2.
    """
    L = len(s)
    if L == 0:
        return 0.0
    if s == '0' * L or s == '1' * L:
        return float(np.log2(L))
    return float(np.log2(L) * (KC_LZ(s) + KC_LZ(s[::-1])) / 2.0)

def process_binary_files(input_folder: str, output_folder: str) -> None:
    os.makedirs(output_folder, exist_ok=True)

    # Pick up files like binary123.txt in any order
    for filename in sorted(os.listdir(input_folder)):
        if not (filename.startswith("binary") and filename.endswith(".txt")):
            continue

        in_path = os.path.join(input_folder, filename)
        with open(in_path, "r") as f:
            seq = f.read().strip()

        # Basic sanity: keep only 0/1 chars
        if not seq or any(ch not in "01" for ch in seq):
            # Write a placeholder so we can detect and fix upstream issues
            kc_val = float("nan")
        else:
            kc_val = calc_KC(seq)

        # Match your existing naming: k<index>.txt
        # e.g., binary57.txt -> k57.txt
        idx = filename[len("binary"):-len(".txt")]
        out_name = f"k{idx}.txt"
        out_path = os.path.join(output_folder, out_name)

        with open(out_path, "w") as out:
            # Two decimals, like pascal_v2 output
            out.write(f"{kc_val:.2f}\n")

    print(f"Processing completed. KC_LZ values saved in '{output_folder}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 lz.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f"Error: input directory not found: {input_dir}")
        sys.exit(1)

    process_binary_files(input_dir, output_dir)
