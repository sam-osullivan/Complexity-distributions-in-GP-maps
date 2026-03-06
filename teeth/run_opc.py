import os

# Define the output file name
output_file = 'commands_opc.txt'

# Get a list of all .ply files in the current directory
ply_files = [f for f in os.listdir() if f.endswith('.ply')]

# Open the output file for writing
with open(output_file, 'w') as f:
    for ply_file in ply_files:
        # Generate the output file name by replacing .ply with _opc.txt
        output_txt = ply_file.replace('.ply', '_opc.txt')
        # Write the command to the output file
        f.write(f'python3 1opc.py {ply_file} ./opc/{output_txt} 3\n')

print(f"Commands written to {output_file}")
