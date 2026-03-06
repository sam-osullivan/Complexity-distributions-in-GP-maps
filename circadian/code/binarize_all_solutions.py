#!/usr/bin/env python3
"""
binarize_all_solutions.py

Runs bin.py on all solutions_out directories found in the plot_b structure.
Creates corresponding binaries_out directories for each solutions_out.

Usage:
    python3 binarize_all_solutions.py --base-dir /path/to/plot_b [options]
"""

import os
import subprocess
import argparse
from pathlib import Path
import time

def setup_arguments():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Binarize all solutions in parameter directories')
    
    parser.add_argument('--base-dir', type=str, required=True,
                       help='Base directory containing G1-G5 subdirectories')
    parser.add_argument('--max-generation', type=int, default=10,
                       help='Maximum generation number (default: 10)')
    parser.add_argument('--groups', nargs='+', default=['G1', 'G2', 'G3', 'G4', 'G5'],
                       help='Groups to process (default: G1 G2 G3 G4 G5)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show commands without executing them')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip directories that already have binaries_out')
    parser.add_argument('--bin-script', type=str, default='bin.py',
                       help='Path to binarization script (default: bin.py)')
    
    return parser

def run_binarization(base_dir, solutions_dir, binaries_dir, bin_script, dry_run=False):
    """Run binarization for a specific solutions directory"""
    
    # Check if solutions directory exists and has files
    if not solutions_dir.exists():
        print(f"❌ Warning: {solutions_dir} does not exist, skipping...")
        return False
    
    solution_files = list(solutions_dir.glob('solution*.txt'))
    if not solution_files:
        print(f"❌ Warning: No solution files found in {solutions_dir}, skipping...")
        return False
    
    # Build command
    cmd = [
        'python3', bin_script,
        str(solutions_dir),
        str(binaries_dir)
    ]
    
    if dry_run:
        print(f"🔍 Would run: {' '.join(cmd)}")
        print(f"   Input: {solutions_dir} ({len(solution_files)} solution files)")
        print(f"   Output: {binaries_dir}")
        return True
    
    try:
        print(f"🔄 Processing: {solutions_dir} ({len(solution_files)} solution files)")
        print(f"   → {binaries_dir}")
        start_time = time.time()
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            # Count created binary files
            binary_files = list(binaries_dir.glob('binary*.txt')) if binaries_dir.exists() else []
            print(f"✅ Completed: {solutions_dir} → {len(binary_files)} binary files in {elapsed:.1f}s")
            return True
        else:
            print(f"❌ Error in {solutions_dir}:")
            print(f"   stdout: {result.stdout[-300:]}")  # Last 300 chars
            print(f"   stderr: {result.stderr[-300:]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception running {solutions_dir}: {e}")
        return False

def main():
    # Parse arguments
    parser = setup_arguments()
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    
    print(f"Binarizing all solutions in parameter directories")
    print(f"Base directory: {base_dir}")
    print(f"Groups: {args.groups}")
    print(f"Max generation: {args.max_generation}")
    print(f"Binarization script: {args.bin_script}")
    print(f"Dry run: {args.dry_run}")
    print(f"Skip existing: {args.skip_existing}")
    
    # Validate base directory
    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}")
        return
    
    # Check if bin.py exists
    bin_script_path = base_dir / args.bin_script
    if not bin_script_path.exists() and not args.dry_run:
        print(f"Error: Binarization script not found: {bin_script_path}")
        print(f"Make sure {args.bin_script} is in {base_dir}")
        return
    
    # Collect all solutions directories
    solutions_dirs = []
    
    for group in args.groups:
        group_dir = base_dir / group
        if not group_dir.exists():
            print(f"Warning: Group directory {group} not found")
            continue
            
        # Add solutions_out for 0param through max_generation param
        for gen in range(0, args.max_generation + 1):
            param_dir = group_dir / f"{gen}param"
            solutions_dir = param_dir / "solutions_out"
            binaries_dir = param_dir / "binaries_out"
            
            if solutions_dir.exists():
                # Check if we should skip existing binaries
                if args.skip_existing and binaries_dir.exists():
                    binary_files = list(binaries_dir.glob('binary*.txt'))
                    if binary_files:
                        print(f"⏭️  Skipping {solutions_dir} (binaries_out exists with {len(binary_files)} files)")
                        continue
                
                solutions_dirs.append((group, gen, solutions_dir, binaries_dir))
    
    total_dirs = len(solutions_dirs)
    print(f"\nFound {total_dirs} solutions directories to process")
    
    if total_dirs == 0:
        print("No solutions directories found!")
        return
    
    # Process all directories
    success_count = 0
    
    for i, (group, gen, solutions_dir, binaries_dir) in enumerate(solutions_dirs, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{total_dirs}] {group}/{gen}param")
        print(f"{'='*60}")
        
        success = run_binarization(base_dir, solutions_dir, binaries_dir, 
                                 args.bin_script, args.dry_run)
        
        if success:
            success_count += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully processed: {success_count}/{total_dirs} directories")
    
    if not args.dry_run and success_count > 0:
        print(f"\nBinary files created in:")
        total_binary_files = 0
        for group in args.groups:
            group_dir = base_dir / group
            if group_dir.exists():
                binaries_dirs = []
                for gen in range(0, args.max_generation + 1):
                    binaries_dir = group_dir / f"{gen}param" / "binaries_out"
                    if binaries_dir.exists():
                        binary_count = len(list(binaries_dir.glob('binary*.txt')))
                        binaries_dirs.append(f"{gen}param/binaries_out ({binary_count} files)")
                        total_binary_files += binary_count
                if binaries_dirs:
                    print(f"  {group}: {', '.join(binaries_dirs)}")
        
        print(f"\nTotal binary files created: {total_binary_files}")

if __name__ == "__main__":
    main()
