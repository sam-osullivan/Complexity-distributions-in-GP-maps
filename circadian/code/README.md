## Plot (a)
1. To solve ODE system for set of input parameters:
python3 run_solutions.py \
    --input-dir /mnt/users/osullivans/circ/oct24/t0to50/parameters \
    --tf 50 \
    --num_chunks 50 \ ##Vary this value to adjust lengths, as in Plot (c)
    --n_steps 49999 \

2. Binarize output curves
python3 2bin.py </solutions_out> </binary_out>

3. Calculate Lempel-Ziv Complexity
python3 lz.py </binary_out> </lz_values>

4. Store results in a table
python3 make_any_table.py \
--params-dir <parameters_directory>
--binary-dir <binaries_directory>
--lz-dir <lz_values_directory>
--output <output_table.txt>

6. sample P-distribution and compile into a table:
python3 sample0mutbinaries.py
&
python3 make_0mut_table.py

7. Mutate parameters
python3 mutate_params.py --input <input_folder> --output <output_folder> -seed 42

## Plot (d)
1. Create complexity quintiles
python3 create_complexity_quintiles.py \ --input <input_table> --output-dir <output_dir> 0--samples-per-group 2000

2. Copy corresponding parameters to quintiles
python3 copy_params_to_quintiles.py --params-dir <input_parameter_directory> \ --quintiles_dir <quintiles_dir>

3. Mutate parameters, run solutions, binarize solutions, calculate LZ complexities
python3 mutate_params.py --input G1/0param --output G1/1param --seed 1001
python3 mutate_params.py --input G2/0param --output G2/1param --seed 2001
python3 mutate_params.py --input G3/0param --output G3/1param --seed 3001
python3 mutate_params.py --input G4/0param --output G4/1param --seed 4001
python3 mutate_params.py --input G5/0param --output G1/5param --seed 5001
(repeat up to 20 parameters)

    OR python3 sequential_mutations.py --base-dir . --start-generation 1 --max-generation 20

    python3 run_all_solutions.py --base-dir .

    python3 binarize_all_solutions.py --base-dir .

    python3 calculate_all_lz_complexities.py --base-dir .

    python3 generate_all_data_tables.py --base-dir <base_dir>
