import os
import argparse
import pymeshlab

# Set default options
binary = False
save_vertex_color = False

# Set up argument parser
parser = argparse.ArgumentParser(description='Convert .off files to .ply files using PyMeshLab.')
parser.add_argument('input_dir', type=str, help='Path to the directory containing .off files')

# Parse arguments
args = parser.parse_args()
input_dir = args.input_dir

# Output directory name
output_dir_name = 'outputs_ply'

# Create outputs_ply directory if it doesn't exist
output_dir = os.path.join(input_dir, output_dir_name)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Initialize PyMeshLab
ms = pymeshlab.MeshSet()

# Loop through all files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.off'):
        # Construct input and output file paths
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.ply')

        # Load the mesh from the input file
        ms.load_new_mesh(input_file)

        # Perform any additional processing steps here if needed

        # Save the processed mesh to the output file
        ms.save_current_mesh(output_file, binary=binary, save_vertex_color=save_vertex_color)

        # Print a confirmation
        print("Mesh processing complete. Output saved to:", output_file)
