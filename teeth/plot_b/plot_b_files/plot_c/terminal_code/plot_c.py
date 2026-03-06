#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def create_plot(N_values, entropies, scaled_means=None, simple_means=None,
                filename_suffix="", log_y=False, simple_mean_only=False):
    """Create a plot with entropy and optionally scaled and/or simple mean complexity.

    - N_values: list of x values (will be plotted on a log x axis)
    - entropies: list of entropy values (required)
    - scaled_means: list or None -> plotted if provided
    - simple_means: list or None -> plotted if provided
    - log_y: if True, use log scale on y-axis
    - simple_mean_only: if True, adjust title for the simple-mean-only plots
    """
    plt.figure(figsize=(12, 8))

    # Entropy (always plotted)
    plt.semilogx(N_values, entropies, 'o-', linewidth=2, markersize=8,
                 label='Entropy vs Number of Samples')

    # Scaled mean (optional)
    if scaled_means is not None:
        plt.semilogx(N_values, scaled_means, 's--', linewidth=2, markersize=8,
                     label='Scaled Average Complexity vs Number of Samples')

    # Simple mean (optional)
    if simple_means is not None:
        plt.semilogx(N_values, simple_means, '^-', linewidth=2, markersize=8,
                     label='Mean Complexity vs Number of Samples')

    # Formatting
    plt.xlabel('Number of Samples (N)', fontsize=14)

    # Titles and labels
    if log_y:
        plt.ylabel('Entropy (S) and Average Complexity (K) [Log₁₀ scale]', fontsize=14)
        plt.title('Entropy (S) and Average Complexity (K) vs Number of Samples for Teeth', fontsize=16)
        plt.yscale('log')
    elif simple_mean_only:
        plt.ylabel('Entropy (S) and Average Complexity (K)', fontsize=14)
        plt.title('Entropy (S) and Average Complexity (K) vs Number of Samples for Teeth', fontsize=16)
    else:
        plt.ylabel('Entropy (S) and Scaled Average Complexity (K)', fontsize=14)
        plt.title('Entropy (S) and Scaled Average Complexity (K) vs Number of Samples for Teeth', fontsize=16)

    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)

    # X limits and ticks
    plt.xlim(5, 200000)
    x_ticks = [10, 100, 1000, 10000, 100000]
    x_tick_labels = ['10¹', '10²', '10³', '10⁴', '10⁵']
    plt.xticks(x_ticks, x_tick_labels)

    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()

    return plt.gcf()


def main():
    base_dir = Path("/mnt/users/osullivans/tehe/plot_c")

    configs = [
        {'N': 10, 'dir': '10', 'entropy_file': base_dir / '10' / '10entropy.txt',
         'scaled_mean_file': base_dir / '10' / 'scaled_mean.txt',
         'simple_mean_file': base_dir / '10' / 'simple_mean.txt'},
        {'N': 100, 'dir': '100', 'entropy_file': base_dir / '100' / '100entropy.txt',
         'scaled_mean_file': base_dir / '100' / 'scaled_mean.txt',
         'simple_mean_file': base_dir / '100' / 'simple_mean.txt'},
        {'N': 1000, 'dir': '103', 'entropy_file': base_dir / '103' / '103entropy.txt',
         'scaled_mean_file': base_dir / '103' / 'scaled_mean.txt',
         'simple_mean_file': base_dir / '103' / 'simple_mean.txt'},
        {'N': 10000, 'dir': '104', 'entropy_file': base_dir / '104' / '104_entropy.txt',
         'scaled_mean_file': base_dir / '104' / 'scaled_mean.txt',
         'simple_mean_file': base_dir / '104' / 'simple_mean.txt'},
        {'N': 100000, 'dir': '105', 'entropy_file': base_dir / '105' / '105entropy.txt',
         'scaled_mean_file': base_dir / '105' / 'scaled_mean.txt',
         'simple_mean_file': base_dir / '105' / 'simple_mean.txt'}
    ]

    data = []

    for config in configs:
        N = config['N']
        dir_name = config['dir']
        try:
            with open(config['entropy_file'], 'r') as f:
                entropy = float(f.read().strip())
            with open(config['scaled_mean_file'], 'r') as f:
                scaled_mean = float(f.read().strip())
            simple_mean = None
            if config['simple_mean_file'].exists():
                with open(config['simple_mean_file'], 'r') as f:
                    simple_mean = float(f.read().strip())
            data.append((N, entropy, scaled_mean, simple_mean))
            print(f"Dir {dir_name} -> N={N}: entropy={entropy:.3f}, scaled_mean={scaled_mean:.3f}, simple_mean={simple_mean if simple_mean is not None else 'N/A'}")
        except (FileNotFoundError, ValueError) as e:
            print(f"Warning: Could not read data for directory {dir_name} (N={N}): {e}")

    if not data:
        print("Error: No valid data found")
        return

    # Sort by N
    data.sort(key=lambda x: x[0])

    # Extract data for plotting
    N_values = [d[0] for d in data]
    entropies = [d[1] for d in data]
    scaled_means = [d[2] for d in data]
    simple_means = [d[3] for d in data]
    has_simple_means = any(sm is not None for sm in simple_means)

    # 1) All three lines
    if has_simple_means:
        print("Creating plot with all three lines...")
        fig1 = create_plot(N_values, entropies, scaled_means=scaled_means, simple_means=simple_means)
        output_file1 = base_dir / "plot_c_complexity_vs_entropy_with_simple_mean.png"
        fig1.savefig(output_file1, dpi=300, bbox_inches='tight')
        print(f"Plot with simple mean saved to {output_file1}")
        plt.close(fig1)

    # 2) No simple mean
    print("Creating plot without simple mean...")
    fig2 = create_plot(N_values, entropies, scaled_means=scaled_means, simple_means=None)
    output_file2 = base_dir / "plot_c_complexity_vs_entropy_no_simple_mean.png"
    fig2.savefig(output_file2, dpi=300, bbox_inches='tight')
    print(f"Plot without simple mean saved to {output_file2}")
    plt.close(fig2)

    # 3) No 10¹ point + no simple mean
    print("Creating plot without 10^1 data point and no simple mean...")
    filtered = [(N, ent, sc, sm) for (N, ent, sc, sm) in zip(N_values, entropies, scaled_means, simple_means) if N != 10]
    if filtered:
        filtered_N = [d[0] for d in filtered]
        filtered_entropies = [d[1] for d in filtered]
        filtered_scaled = [d[2] for d in filtered]
        fig3 = create_plot(filtered_N, filtered_entropies, scaled_means=filtered_scaled, simple_means=None)
        output_file3 = base_dir / "plot_c_complexity_vs_entropy_no_10_no_simple_mean.png"
        fig3.savefig(output_file3, dpi=300, bbox_inches='tight')
        print(f"Plot without 10^1 data point and no simple mean saved to {output_file3}")
        plt.close(fig3)

    # 4) Simple mean only (no scaled mean)
    if has_simple_means:
        print("Creating plot: simple mean only (no scaled mean)...")
        fig4 = create_plot(N_values, entropies, scaled_means=None, simple_means=simple_means,
                           simple_mean_only=True)
        output_file4 = base_dir / "plot_c_complexity_vs_entropy_simple_mean_only.png"
        fig4.savefig(output_file4, dpi=300, bbox_inches='tight')
        print(f"Plot (simple mean only) saved to {output_file4}")
        plt.close(fig4)

        # 5) Simple mean only (log-y)
        print("Creating plot: simple mean only (no scaled mean) with log-y axis...")
        fig5 = create_plot(N_values, entropies, scaled_means=None, simple_means=simple_means,
                           log_y=True, simple_mean_only=True)
        output_file5 = base_dir / "plot_c_complexity_vs_entropy_simple_mean_only_logy.png"
        fig5.savefig(output_file5, dpi=300, bbox_inches='tight')
        print(f"Plot (simple mean only, log-y) saved to {output_file5}")
        plt.close(fig5)
    else:
        print("Skipping simple-mean-only plots because no simple_mean files were found.")

    print("Plots created successfully!")


if __name__ == "__main__":
    main()
