import os
import numpy as np
import argparse

def read_parameters(input_file):
    parameters = []
    extra_lines = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split()
                try:
                    value = float(parts[0])
                    name = ' '.join(parts[1:])  # Keep the full parameter name
                    parameters.append((name, value))
                except ValueError:
                    # If line can't be converted to float, consider it as an extra line
                    extra_lines.append(line.strip())
    return parameters, extra_lines

def generate_mutants(parameters, param_ranges, steps_per_param, output_dir, extra_lines):
    param_names = [param[0] for param in parameters]
    param_values = np.array([param[1] for param in parameters])
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate mutants
    mutant_count = 0
    for i, (param_name, _) in enumerate(parameters):
        # Find corresponding full parameter name in param_ranges
        full_param_name = None
        for full_name in param_ranges:
            if param_name.lower() in full_name.lower():
                full_param_name = full_name
                break
        
        if full_param_name is None:
            continue
        
        start_value, end_value = param_ranges[full_param_name]
        step_size = (end_value - start_value) / steps_per_param
        
        for step in range(steps_per_param):
            mutant_parameters = param_values.copy()
            mutant_value = start_value + step * step_size
            mutant_parameters[i] = mutant_value
            
            # Create mutant file content
            mutant_filename = f'9_{full_param_name[:3]}_{mutant_value:.12f}.txt'
            mutant_filepath = os.path.join(output_dir, mutant_filename)
            
            with open(mutant_filepath, 'w') as f:
                for name in parameter_order:
                    if name == full_param_name:
                        f.write(f'{mutant_value:.12f}      {name}\n')
                    elif name in unchanged_parameters:
                        f.write(f'{unchanged_parameters[name]:.12f}      {name}\n')
                    else:
                        f.write(f'{param_values[param_names.index(name)]:.12f}      {name}\n')
                # Write the extra lines at the end of the file
                for extra_line in extra_lines:
                    f.write(f'{extra_line}\n')
            
            mutant_count += 1
    
    print(f"Generated {mutant_count} mutant files in '{output_dir}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate mutant files from parameter file.')
    parser.add_argument('input_file', type=str, help='Path to the input parameter file (CompSuppNine.txt)')
    parser.add_argument('--output_dir', type=str, default='mutants', help='Directory to save mutant files (default: mutants)')
    parser.add_argument('--steps_per_param', type=int, default=1000, help='Number of steps per parameter (default: 1000)')
    args = parser.parse_args()
    
    # Read parameters from input file
    parameters, extra_lines = read_parameters(args.input_file)
    
    # Define ranges for each parameter
    param_ranges = {
        'Egr_Epithelial_proliferation_rate': (0.004, 0.031),
        'Mgr_Mesenchymal_proliferation_rate': (0, 3352.557),
        'Rep_Repulsion': (0, 112.481),
        'ADH_Traction_between_neighbors': (0, 1.026),
        'ACT_BMP4_auto-activation': (0.121, 0.258),
        'INH_Inhibtion_of_SHH_over_BMP4': (1.046, 21.99),
        'Sec_FGF4_secretion_rate': (0.022, 0.107),
        'Da_BMP4_diffusion_rate': (0.001, 1.122),
        'Di_SHH_diffusion_rate': (0.001, 0.299),
        'Ds_FGF4_diffusion_rate': (0, 0.333),
        'Int_Initial(SHH)_threshold': (0, 0.195),
        'Set_secondary(FGF4)_threshold': (0.288, 0.999),
        'Boy_Boyancy_Mesenchyme_mechanic_resistance': (0, 0.201),
        'Dff_Differentiation_rate': (0.0004, 0.033),
        'Deg_Protein_degradation_rate': (0.01, 0.199),
        'Ntr_Nuclear_atraction_Mechanical_traction_from_the_borders_to_the_nucleus': (0, 1.599),
        'Bgr_Border_growth_Amount_of_Mesenchyme_in_AP': (0.125, 2.303),  # New sampling range
        'Pbi_Posterior_bias': (0, 32.88),  # New sampling range
        'Dgr_Downward_vector_of_growth': (733.901, 12500)  # New sampling range
    }
    
    # Define unchanged parameters
    unchanged_parameters = {
        'Nothing': 0.0,
        'Abi_Anterior_bias': 12.0,
        'Bbi_Buccal_bias_(invariable_in_seals)': 1.0,
        'Lbi_Lingual_bias_(invariable)': 1.0,
        'Rad_Radius_of_initial_conditions(2_for_having_7_cells)_(invariable_in_seals)': 2.0,
        'Bwi_Width_of_border': 0.8
    }
    
    # Define the order of parameters as they appear in the output format
    parameter_order = [
        'Egr_Epithelial_proliferation_rate', 'Mgr_Mesenchymal_proliferation_rate', 'Rep_Repulsion', 'Nothing',
        'ADH_Traction_between_neighbors', 'ACT_BMP4_auto-activation', 'INH_Inhibtion_of_SHH_over_BMP4', 'Nothing',
        'Sec_FGF4_secretion_rate', 'Nothing', 'Da_BMP4_diffusion_rate', 'Di_SHH_diffusion_rate', 'Ds_FGF4_diffusion_rate',
        'Nothing', 'Int_Initial(SHH)_threshold', 'Set_secondary(FGF4)_threshold', 'Boy_Boyancy_Mesenchyme_mechanic_resistance',
        'Dff_Differentiation_rate', 'Bgr_Border_growth_Amount_of_Mesenchyme_in_AP', 'Abi_Anterior_bias', 'Pbi_Posterior_bias',
        'Bbi_Buccal_bias_(invariable_in_seals)', 'Lbi_Lingual_bias_(invariable)', 'Rad_Radius_of_initial_conditions(2_for_having_7_cells)_(invariable_in_seals)',
        'Deg_Protein_degradation_rate', 'Dgr_Downward_vector_of_growth', 'Ntr_Nuclear_atraction_Mechanical_traction_from_the_borders_to_the_nucleus',
        'Bwi_Width_of_border'  # Added Bwi_Width_of_border to the end of the list
    ]
    
    # Define short names for parameters
    short_names = {
        'Egr_Epithelial_proliferation_rate': 'Egr',
        'Mgr_Mesenchymal_proliferation_rate': 'Mgr',
        'Rep_Repulsion': 'Rep',
        'ADH_Traction_between_neighbors': 'ADH',
        'ACT_BMP4_auto-activation': 'ACT',
        'INH_Inhibtion_of_SHH_over_BMP4': 'INH',
        'Sec_FGF4_secretion_rate': 'Sec',
        'Da_BMP4_diffusion_rate': 'Da',
        'Di_SHH_diffusion_rate': 'Di',
        'Ds_FGF4_diffusion_rate': 'Ds',
        'Int_Initial(SHH)_threshold': 'Int',
        'Set_secondary(FGF4)_threshold': 'Set',
        'Boy_Boyancy_Mesenchyme_mechanic_resistance': 'Boy',
        'Dff_Differentiation_rate': 'Dff',
        'Deg_Protein_degradation_rate': 'Deg',
        'Ntr_Nuclear_atraction_Mechanical_traction_from_the_borders_to_the_nucleus': 'Ntr',
        'Nothing': 'Nothing',
        'Bgr_Border_growth_Amount_of_Mesenchyme_in_AP': 'Bgr',
        'Abi_Anterior_bias': 'Abi',
        'Pbi_Posterior_bias': 'Pbi',
        'Bbi_Buccal_bias_(invariable_in_seals)': 'Bbi',
        'Lbi_Lingual_bias_(invariable)': 'Lbi',
        'Rad_Radius_of_initial_conditions(2_for_having_7_cells)_(invariable_in_seals)': 'Rad',
        'Dgr_Downward_vector_of_growth': 'Dgr',
        'Bwi_Width_of_border': 'Bwi'  # Added short name for the new unchanged parameter
    }
    
    # Generate mutants
    generate_mutants(parameters, param_ranges, args.steps_per_param, args.output_dir, extra_lines)
