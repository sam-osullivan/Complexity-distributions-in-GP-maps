#!/usr/bin/env python3
"""
calculate_all_lz_complexities.py

Runs lz.py on all binaries_out directories found in the plot_b structure.
Creates corresponding lz_values directories for each binaries_out.

Usage:
    python3 calculate_all_lz_complexities.py --base-dir /path/to/plot_b [options]
"""

import os
import subprocess
import argparse
from pathlib import Path
import time

def setup_arguments():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(description='Calculate LZ complexities for all binaries directories')
    
    parser.add_argument('--base-dir', type=str, required=True,
                       help='Base directory containing G1-G5 subdirectories')
    parser.add_argument('--max-generation', type=int, default=10,
                       help='Maximum generation number (default: 10)')
    parser.add_argument('--groups', nargs='+', default=['G1', 'G2', 'G3', 'G4', 'G5'],
                       help='Groups to process (default: G1 G2 G3 G4 G5)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show commands without executing them')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip directories that already have lz_values')
    parser.add_argument('--lz-script', type=str, default='lz.py',
                       help='Path to LZ complexity script (default: lz.py)')
    
    return parser

def run_lz_complexity(base_dir, binaries_dir, lz_values_dir, lz_script, dry_run=False):
    """Run LZ complexity calculation for a specific binaries directory"""
    
    # Check if binaries directory exists and has files
    if not binaries_dir.exists():
        print(f"❌ Warning: {binaries_dir} does not exist, skipping...")
        return False
    
    binary_files = list(binaries_dir.glob('binary*.txt'))
    if not binary_files:
        print(f"❌ Warning: No binary files found in {binaries_dir}, skipping...")
        return False
    
    # Build command
    cmd = [
        'python3', lz_script,
        str(binaries_dir),
        str(lz_values_dir)
    ]
    
    if dry_run:
        print(f"🔍 Would run: {' '.join(cmd)}")
        print(f"   Input: {binaries_dir} ({len(binary_files)} binary files)")
        print(f"   Output: {lz_values_dir}")
        return True
    
    try:
        print(f"🔄 Processing: {binaries_dir} ({len(binary_files)} binary files)")
        print(f"   → {lz_values_dir}")
        start_time = time.time()
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            # Count created LZ files
            lz_files = list(lz_values_dir.glob('k*.txt')) if lz_values_dir.exists() else []
            print(f"✅ Completed: {binaries_dir} → {len(lz_files)} LZ files in {elapsed:.1f}s")
            return True
        else:
            print(f"❌ Error in {binaries_dir}:")
            print(f"   stdout: {result.stdout[-300:]}")  # Last 300 chars
            print(f"   stderr: {result.stderr[-300:]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception running {binaries_dir}: {e}")
        return False

def main():
    # Parse arguments
    parser = setup_arguments()
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir)
    
    print(f"Calculating LZ complexities for all binaries directories")
    print(f"Base directory: {base_dir}")
    print(f"Groups: {args.groups}")
    print(f"Max generation: {args.max_generation}")
    print(f"LZ script: {args.lz_script}")
    print(f"Dry run: {args.dry_run}")
    print(f"Skip existing: {args.skip_existing}")
    
    # Validate base directory
    if not base_dir.exists():
        print(f"Error: Base directory not found: {base_dir}")
        return
    
    # Check if lz.py exists
    lz_script_path = base_dir / args.lz_script
    if not lz_script_path.exists() and not args.dry_run:
        print(f"Error: LZ complexity script not found: {lz_script_path}")
        print(f"Make sure {args.lz_script} is in {base_dir}")
        return
    
    # Collect all binaries directories
    binaries_dirs = []
    
    for group in args.groups:
        group_dir = base_dir / group
        if not group_dir.exists():
            print(f"Warning: Group directory {group} not found")
            continue
            
        # Add binaries_out for 0param through max_generation param
        for gen in range(0, args.max_generation + 1):
            param_dir = group_dir / f"{gen}param"
            binaries_dir = param_dir / "binaries_out"
            lz_values_dir = param_dir / "lz_values"
            
            if binaries_dir.exists():
                # Check if we should skip existing lz_values
                if args.skip_existing and lz_values_dir.exists():
                    lz_files = list(lz_values_dir.glob('k*.txt'))
                    if lz_files:
                        print(f"⏭️  Skipping {binaries_dir} (lz_values exists with {len(lz_files)} files)")
                        continue
                
                binaries_dirs.append((group, gen, binaries_dir, lz_values_dir))
    
    total_dirs = len(binaries_dirs)
    print(f"\nFound {total_dirs} binaries directories to process")
    
    if total_dirs == 0:
        print("No binaries directories found!")
        return
    
    # Process all directories
    success_count = 0
    
    for i, (group, gen, binaries_dir, lz_values_dir) in enumerate(binaries_dirs, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{total_dirs}] {group}/{gen}param")
        print(f"{'='*60}")
        
        success = run_lz_complexity(base_dir, binaries_dir, lz_values_dir, 
                                  args.lz_script, args.dry_run)
        
        if success:
            success_count += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully processed: {success_count}/{total_dirs} directories")
    
    if not args.dry_run and success_count > 0:
        print(f"\nLZ complexity files created in:")
        total_lz_files = 0
        for group in args.groups:
            group_dir = base_dir / group
            if group_dir.exists():
                lz_dirs = []
                for gen in range(0, args.max_generation + 1):
                    lz_values_dir = group_dir / f"{gen}param" / "lz_values"
                    if lz_values_dir.exists():
                        lz_count = len(list(lz_values_dir.glob('k*.txt')))
                        lz_dirs.append(f"{gen}param/lz_values ({lz_count} files)")
                        total_lz_files += lz_count
                if lz_dirs:
                    print(f"  {group}: {', '.join(lz_dirs)}")
        
        print(f"\nTotal LZ complexity files created: {total_lz_files}")

if __name__ == "__main__":
    main()
