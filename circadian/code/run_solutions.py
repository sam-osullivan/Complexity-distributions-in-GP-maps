#!/usr/bin/env python3
"""
run_solutions_from_params.py

For every parameters*.txt in a flat directory,
read p_scaled from the file and integrate the ODE with Radau, then write
solutions to a 'solutions_out' subdirectory.

Example:
 python3 run_solutions_from_params.py --input-dir /path/to/flat/params \
     --tf 100 --n_steps 499999 --num_chunks 19 --workers 4
"""

import argparse
import os
from pathlib import Path
import re
import math
import numpy as np
from scipy.integrate import solve_ivp
from datetime import datetime
from multiprocessing import Pool, cpu_count
import functools

# -----------------------
# ODE rhs (same as your model)
# -----------------------
def rhs(u, p, t):
    f0 = p[0]*u[2] - p[2]*u[0]*u[5]
    f1 = p[1]*u[3] - p[3]*u[1]*u[5]
    f2 = p[2]*u[0]*u[5] - p[0]*u[2]
    f3 = p[3]*u[1]*u[5] - p[1]*u[3]
    f4 = p[6]*u[2] + p[5]*u[0] - p[9]*u[4]
    f5 = p[13]*u[4] + p[0]*u[2] + p[1]*u[3] - u[5]*(p[2]*u[0] + p[3]*u[1] + p[4]*u[7] + p[11])
    f6 = p[8]*u[3] + p[7]*u[1] - p[10]*u[6]
    f7 = p[14]*u[6] - p[4]*u[5]*u[7] + p[11]*u[8] - p[12]*u[7]
    f8 = p[4]*u[5]*u[7] - p[11]*u[8]
    return np.array([f0,f1,f2,f3,f4,f5,f6,f7,f8], dtype=float)

# -----------------------
# helpers to parse p_scaled from parameters file
# -----------------------
BRACKET_RE = re.compile(r'\[.*?\]', re.S)
FLOAT_RE = re.compile(r'[-+]?\d*\.\d+([eE][-+]?\d+)?|[-+]?\d+[eE][-+]?\d+|[-+]?\d+')

def extract_p_scaled(text):
    """
    Try to extract the p_scaled numeric vector from file text.
    Returns list of floats or raises ValueError.
    """
    # try explicit p_scaled = [ ... ]
    m = re.search(r'p_scaled\s*=\s*(\[[^\]]*\])', text, re.S)
    bracket = m.group(1) if m else None
    if not bracket:
        # fallback to first bracketed substring
        m2 = BRACKET_RE.search(text)
        bracket = m2.group(0) if m2 else None
    if bracket:
        tokens = [mo.group(0) for mo in FLOAT_RE.finditer(bracket)]
        if tokens and len(tokens) >= 15:
            return [float(x) for x in tokens]
    # fallback: all floats in text
    tokens = [mo.group(0) for mo in FLOAT_RE.finditer(text)]
    if tokens and len(tokens) >= 15:
        return [float(x) for x in tokens[:15]]
    raise ValueError("p_scaled vector not found or too short")

def index_from_parameters_filename(fname):
    """
    given parametersNNN.txt -> return NNN
    """
    m = re.search(r'parameters(\d+)\.txt$', fname)
    return m.group(1) if m else None

# -----------------------
# per-file processing function
# -----------------------
def process_one(params_path, solutions_dir, t0, tf, n_steps, sample_indices, atol, rtol, max_step):
    """
    params_path: Path to parametersNNN.txt
    solutions_dir: Path to output directory for solutions
    returns: tuple (success_bool, message)
    side-effect: writes solutions_dir/solutionNNN.txt
    """
    try:
        text = params_path.read_text()
        p_scaled = extract_p_scaled(text)
        if len(p_scaled) < 15:
            raise ValueError("parsed p_scaled length < 15")
        p = np.array(p_scaled[:15], dtype=float)

        # initial condition
        u0 = np.array([1.,1.,0.,0.,0.,0.,0.,0.,0.], dtype=float)

        # build t_eval
        t_eval = np.linspace(t0, tf, n_steps + 1)

        # integrate with Radau
        sol = solve_ivp(fun=lambda tt, yy: rhs(yy, p, tt),
                        t_span=(t0, tf),
                        y0=u0,
                        method='Radau',
                        t_eval=t_eval,
                        atol=atol,
                        rtol=rtol,
                        max_step=max_step)

        if not sol.success:
            # write NaNs but still return failure indicator
            u = np.full((n_steps + 1, 9), np.nan, dtype=float)
            msg = f"solver failed: {sol.message}"
        else:
            u = sol.y.T
            msg = "ok"

    except Exception as e:
        # any parse or solver-setup error: write NaNs
        u = np.full((n_steps + 1, 9), np.nan, dtype=float)
        msg = f"error: {e}"

    # write solution file to solutions_dir/solutionNNN.txt
    try:
        idx = index_from_parameters_filename(params_path.name) or "unknown"
        out_path = solutions_dir / f"solution{idx}.txt"

        # sample C = u[:,8]
        C = u[:,8]
        lines = []
        # initial point
        lines.append(f"{C[0]:.12e}")
        for idx_i in sample_indices:
            if 0 <= idx_i <= n_steps:
                val = C[idx_i]
                # format NaN appropriately
                if math.isnan(val):
                    lines.append("nan")
                else:
                    lines.append(f"{val:.12e}")
            else:
                lines.append("nan")

        out_path.write_text("\n".join(lines) + "\n")
    except Exception as e2:
        return False, f"failed to write solution: {e2} (prev: {msg})"

    return (msg == "ok"), msg

# -----------------------
# gather list of parameters files from flat directory
# -----------------------
def collect_parameter_files(input_dir):
    p = Path(input_dir)
    if not p.is_dir():
        raise FileNotFoundError(f"input directory not found: {input_dir}")
    
    files = sorted(p.glob("parameters*.txt"))
    return files

# -----------------------
# main
# -----------------------
def main():
    ap = argparse.ArgumentParser(description="Solve ODE for parameters files in a flat directory and write solutions to solutions_out/")
    ap.add_argument("--input-dir", required=True, help="directory containing parameters*.txt files")
    ap.add_argument("--tf", type=float, default=100.0, help="final time (default 100)")
    ap.add_argument("--n_steps", type=int, default=499999, help="number of steps (default 499999)")
    ap.add_argument("--num_chunks", type=int, default=19, help="number of chunks to sample (default 19)")
    ap.add_argument("--atol", type=float, default=1e-8, help="absolute tolerance for solver")
    ap.add_argument("--rtol", type=float, default=1e-6, help="relative tolerance for solver")
    ap.add_argument("--max_step", type=float, default=1.0, help="max step size for solver")
    ap.add_argument("--workers", type=int, default=1, help="number of parallel worker processes (default 1)")
    ap.add_argument("--dry-run", action="store_true", help="don't actually run solves; just report files found")
    args = ap.parse_args()

    input_dir = Path(args.input_dir).resolve()
    tf = args.tf
    n_steps = args.n_steps
    num_chunks = args.num_chunks

    # create solutions output directory
    solutions_dir = input_dir / "solutions_out"
    solutions_dir.mkdir(exist_ok=True)

    # compute sample indices same rule as your earlier script
    if num_chunks % 2 == 0:
        interval = n_steps // (num_chunks + 1)
    else:
        interval = n_steps // num_chunks
    # sample indices range: interval, 2*interval, ... up to num_chunks*interval
    sample_indices = [interval * i for i in range(1, num_chunks + 1)]
    # ensure indices are within 0..n_steps
    sample_indices = [min(max(0, int(ii)), n_steps) for ii in sample_indices]

    # collect parameters files
    files = collect_parameter_files(input_dir)
    if not files:
        print("No parameters*.txt files found in", input_dir)
        return

    print(f"Found {len(files)} parameter files in {input_dir}.")
    print(f"Using tf={tf}, n_steps={n_steps}, num_chunks={num_chunks}, interval(steps)={interval}")
    print(f"Sample indices (first 5): {sample_indices[:5]} ... last: {sample_indices[-1]}")
    print(f"Solutions will be written to: {solutions_dir}")

    if args.dry_run:
        for f in files[:10]:
            print("FOUND:", f)
        print("Dry run: exiting.")
        return

    # prepare partial worker function
    worker = functools.partial(process_one,
                               solutions_dir=solutions_dir,
                               t0=0.0, tf=tf, n_steps=n_steps,
                               sample_indices=sample_indices,
                               atol=args.atol, rtol=args.rtol, max_step=args.max_step)

    workers = max(1, min(args.workers, cpu_count()))
    print(f"Running with {workers} worker(s).")

    if workers == 1:
        # sequential
        count_ok = 0
        for i, fp in enumerate(files, start=1):
            ok, msg = worker(fp)
            if ok:
                count_ok += 1
            if i % 100 == 0 or i == 1 or i == len(files):
                print(f"[{i}/{len(files)}] {fp.name} -> {msg}")
        print(f"Completed: {count_ok}/{len(files)} successful solves.")
    else:
        # parallel via multiprocessing Pool
        count_ok = 0
        with Pool(processes=workers) as pool:
            for i, (fp, result) in enumerate(zip(files, pool.imap(worker, files)), start=1):
                ok, msg = result
                if ok:
                    count_ok += 1
                if i % 100 == 0 or i == 1 or i == len(files):
                    print(f"[{i}/{len(files)}] {fp.name} -> {msg}")
        print(f"Completed: {count_ok}/{len(files)} successful solves.")

if __name__ == "__main__":
    main()
