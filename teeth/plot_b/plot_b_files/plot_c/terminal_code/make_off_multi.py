import os
import sys

# Check if the input directory and output directory are provided
if len(sys.argv) < 3:
    print("Usage: python generate_multirun.py <input_directory> <output_directory>")
    sys.exit(1)

# Get the input and output directories from the command line arguments
input_directory = sys.argv[1]
output_directory = sys.argv[2]

# Check if the provided input directory exists
if not os.path.isdir(input_directory):
    print(f"The input directory {input_directory} does not exist.")
    sys.exit(1)

# Check if the provided output directory exists; if not, create it
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Path to the output file
output_file = os.path.join(output_directory, 'multirun.txt')

# Create or open the multirun.txt file in the output directory
try:
    with open(output_file, 'w') as multirun_file:
        # Iterate through all files in the input directory
        for filename in sorted(os.listdir(input_directory)):
            # Construct the full path to the file
            file_path = os.path.join(input_directory, filename)
            try:
                # Check if the file is a regular file and has a .txt extension
                if os.path.isfile(file_path) and filename.endswith('.txt'):
                    # Get the filename without the extension
                    file_name_without_extension = os.path.splitext(filename)[0]
                    # Write the required line to the multirun.txt file, skip if it matches the unwanted line
                    line_to_write = f'./runt.e ./{filename} . {file_name_without_extension} 9000 1\n'
                    if line_to_write.strip() != './runt.e ./.txt . .txt 9000 1':
                        multirun_file.write(line_to_write)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue

    print(f"multirun.txt file has been created in {output_directory}.")
except Exception as e:
    print(f"Error creating multirun.txt: {e}")
