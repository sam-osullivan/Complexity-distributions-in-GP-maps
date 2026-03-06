#!/usr/bin/env python3
"""
run_all_solutions.py

Runs run_solutions.py on all parameter directories (0param through 10param for G1-G5).
Creates solutions_out subdirectories in each param directory.

Usage:
    python3 run_all_solutions.py --base-dir /path/to/plot_b [options]
"""

import os
import subprocess
import argparse
from pathlib import Path
import time

def setup_arguments():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Run solutions for all parameter directories')
    
    parser.add_argument('--base-dir', type=str, required=True,
                       help='Base directory containing G1-G5 subdirectories')
    parser.add_argument('--tf', type=float, default=50,
                       help='Final time for simulations (default: 50)')
    parser.add_argument('--num-chunks', type=int, default=50,
                       help='Number of chunks (default: 50)')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers (default: 4)')
    parser.add_argument('--max-generation', type=int, default=10,
                       help='Maximum generation number (default: 10)')
    parser.add_argument('--groups', nargs='+', default=['G1', 'G2', 'G3', 'G4', 'G5'],
                       help='Groups to process (default: G1 G2 G3 G4 G5)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show commands without executing them')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip directories that already have solutions_out')
    
    return parser

def run_solutions(base_dir, input_dir, tf, num_chunks, workers, dry_run=False):
    """Run solutions for a specific parameter directory"""
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"❌ Warning: {input_dir} does not exist, skipping...")
        return False
    
    # Check if there are any parameter files
    param_files = list(input_dir.glob('parameters*.txt'))
    if not param_files:
        print(f"❌ Warning: No parameter files found in {input_dir}, skipping...")
        return False
    
    # Build command
    cmd = [
        'python3', 'run_solutions.py',
        '--input-dir', str(input_dir),
        '--tf', str(tf),
        '--num_chunks', str(num_chunks),
        '--workers', str(workers)
    ]
    
    if dry_run:
        print(f"�� Would run: {' '.join(cmd)}")
        print(f"   Input: {input_dir} ({len(param_files)} param files)")
        return True
    
    try:
        print(f"🔄 Processing: {input_dir} ({len(param_files)} param files)")
        start_time = time.time()
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Completed: {input_dir} in {elapsed:.1f}s")
            return True
        else:
            print(f"❌ Error in {input_dir}:")
            print(f"   stdout: {result.stdout[-500:]}")  # Last 500 chars
            print(f"   stderr: {result.stderr[-500:]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception running {input_dir}: {e}")
        return False

def main():
    # Parse arguments
    parser = setup_arguments()
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    
    print(f"Running solutions for all parameter directories")
    print(f"Base directory: {base_dir}")
    print(f"Parameters: tf={args.tf}, num_chunks={args.num_chunks}, workers={args.workers}")
    print(f"Groups: {args.groups}")
    print(f"Max generation: {args.max_generation}")
    print(f"Dry run: {args.dry_run}")
    print(f"Skip existing: {args.skip_existing}")
    
    # Validate base directory
    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}")
        return
    
    # Collect all parameter directories
    param_dirs = []
    
    for group in args.groups:
        group_dir = base_dir / group
        if not group_dir.exists():
            print(f"Warning: Group directory {group} not found")
            continue
            
        # Add 0param through max_generation param
        for gen in range(0, args.max_generation + 1):
            param_dir = group_dir / f"{gen}param"
            if param_dir.exists():
                # Check if we should skip existing solutions
                if args.skip_existing and (param_dir / "solutions_out").exists():
                    print(f"⏭️  Skipping {param_dir} (solutions_out exists)")
                    continue
                param_dirs.append((group, gen, param_dir))
            else:
                print(f"Warning: {param_dir} not found")
    
    total_dirs = len(param_dirs)
    print(f"\nFound {total_dirs} parameter directories to process")
    
    if total_dirs == 0:
        print("No parameter directories found!")
        return
    
    # Process all directories
    success_count = 0
    
    for i, (group, gen, param_dir) in enumerate(param_dirs, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{total_dirs}] {group}/{gen}param")
        print(f"{'='*60}")
        
        success = run_solutions(base_dir, param_dir, args.tf, args.num_chunks, 
                              args.workers, args.dry_run)
        
        if success:
            success_count += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully processed: {success_count}/{total_dirs} directories")
    print(f"Parameters used: tf={args.tf}, num_chunks={args.num_chunks}, workers={args.workers}")
    
    if not args.dry_run and success_count > 0:
        print(f"\nSolutions created in:")
        for group in args.groups:
            group_dir = base_dir / group
            if group_dir.exists():
                solutions_dirs = []
                for gen in range(0, args.max_generation + 1):
                    solutions_dir = group_dir / f"{gen}param" / "solutions_out"
                    if solutions_dir.exists():
                        solutions_dirs.append(f"{gen}param/solutions_out")
                if solutions_dirs:
                    print(f"  {group}: {', '.join(solutions_dirs)}")

if __name__ == "__main__":
    main()
