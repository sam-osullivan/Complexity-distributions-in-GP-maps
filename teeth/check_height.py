#This script processes all .off files in the current directory, checks the height (difference between the maximum and minimum z-coordinates) of each file, and classifies them as either "tall enough" or "too flat" based on a threshold of 0.5. The results are written to two separate output files: 18985_tall_enough.txt and 18985_too_flat.txt. If the file is not in the correct OFF or COFF format, an error is raised.

import os
import glob

# Function to check the height of the generated .off file
def check_height(off_file):
    if not os.path.isfile(off_file):
        raise ValueError(f"OFF file does not exist: {off_file}")
    
    print(f"Checking height for file: {off_file}")
    
    # Read the .off file
    with open(off_file, 'r') as file:
        lines = file.readlines()
    
    # Check if the file is in OFF or COFF format
    if lines[0].strip() not in ['OFF', 'COFF']:
        raise ValueError(f"File {off_file} is not in OFF or COFF format.")
    
    # Read the number of vertices and faces
    num_vertices, num_faces, _ = map(int, lines[1].strip().split())
    
    # Read the vertices
    z_values = [float(lines[i].strip().split()[2]) for i in range(2, 2 + num_vertices)]
    
    # Calculate the height (z-coordinate range)
    height = max(z_values) - min(z_values)
    
    if height < 0.5:
        return False, height
    else:
        return True, height

# List all .off files in the current directory
off_files = glob.glob("*.off")

# Check if there are any .off files to process
if not off_files:
    print("No .off files found in the current directory.")
    exit()

# Open the output files for writing
tall_enough_file = open("18985_tall_enough.txt", "w")
too_flat_file = open("18985_too_flat.txt", "w")

# Process each .off file
for off_file in off_files:
    try:
        # Check the height of the current .off file
        height_ok, height_value = check_height(off_file)
        
        if height_ok:
            # File is tall enough
            print(f"{off_file} is tall enough with height {height_value}")
            tall_enough_file.write(f"{off_file} {height_value}\n")
        else:
            # File is too flat
            print(f"{off_file} is too flat with height {height_value}")
            too_flat_file.write(f"{off_file} {height_value}\n")
    except Exception as e:
        print(f"Error processing {off_file}: {e}")

# Close the output files
tall_enough_file.close()
too_flat_file.close()

print("Height checking completed.")
