import numpy as np
from pyDOE import lhs
import os
import sys

# Check if the number of samples is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python3 generate_samples.py <num_samples>")
    sys.exit(1)

# Get the number of samples from the command-line argument
num_samples = int(sys.argv[1])

# Define the parameters and their ranges
parameters = {
    'Egr_Epithelial_proliferation_rate': (0.004, 0.031),
    'Mgr_Mesenchymal_proliferation_rate': (0, 3352.557),
    'Rep_Repulsion': (0,112.481),
    'ADH_Traction_between_neighbors': (0, 1.026),
    'ACT_BMP4_auto-activation': (0.121, 0.258),
    'INH_Inhibtion_of_SHH_over_BMP4': (1.046, 21.99),
    'Sec_FGF4_secretion_rate': (0.022,0.107),
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

# Generate LHS samples
lhs_samples = lhs(len(parameters), samples=num_samples)

# Rescale samples to the actual ranges of each parameter
rescaled_samples = np.zeros_like(lhs_samples)

for i, (param, (low, high)) in enumerate(parameters.items()):
    rescaled_samples[:, i] = low + lhs_samples[:, i] * (high - low)

# Convert rescaled samples into a dictionary
sampled_parameters = {param: rescaled_samples[:, i] for i, param in enumerate(parameters.keys())}

# Define the unchanged parameters
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
    'Deg_Protein_degradation_rate', 'Dgr_Downward_vector_of_growth', 'Ntr_Nuclear_atraction_Mechanical_traction_from_the_borders_to_the_nucleus', 'Bwi_Width_of_border'
]

# Create output directory
output_dir = f"{num_samples}_input_files"
os.makedirs(output_dir, exist_ok=True)

# Formatting and outputting the samples to separate files
for sample_index in range(num_samples):
    formatted_sample = []
    for param_name in parameter_order:
        if param_name in sampled_parameters:
            value = sampled_parameters[param_name][sample_index]
        else:
            value = unchanged_parameters[param_name]
        formatted_sample.append(f"{value:20.13f}      {param_name}")
    
    output_filename = os.path.join(output_dir, f"{sample_index + 1}.txt")
    with open(output_filename, 'w') as f:
        f.write("\n".join(formatted_sample))
        f.write("\n1,2,3,NA,4,5,6,NA,7,NA,8,9,10,NA,11,12,13,14,15,16,17,18,19,NA,20,21,NA\n")
        f.write("1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27\n")

