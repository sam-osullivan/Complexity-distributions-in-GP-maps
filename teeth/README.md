# tooth-evo-devo

Code steps to generate uniform random sampling of teeth using OPCR and cusp counts as the measurement for complexity (figures 3a & 4a):

0. gfortran -O2 -w new_humppa_translate2.f90 -o runt.e
1. python3 lhs.py 19000     # This will generate 19000 input .txt files using Latin Hypercube Sampling of the variable genetic and cellular parameters in ToothMaker
2. cp runt.e ./19000_input_files     #This will copy runt.e into the subdirectory with the input .txt files
3. python3 make_off_multi.py ./19000_input_files ./19000_input_files     #this makes a "multirun" code to run to generate 19000 teeth in the cluster. If you only want to generate a single tooth you can simply run "./runt.e ./1.txt . ./1 9000 1"
4. cd ./19000_input_files #navigate to directory with input files
5. sed -i '/\.\/runt\.e \.\/multirun\.txt \. multirun 9000 1/d' multirun.txt     #this deletes the last line of the multirun file, if neccessary, which may say ./runt.e ./multirun.txt . multirun 5000 1 in multirun.txt
6. addqueue -n 50 /usr/local/shared/bin/multirun ./multirun.txt     #for running calculations on a cluster, this will generate all the tooth .off files inside ./19000_input_files
7. ls -1 ./*.off | wc -l    #this will tell you how many .off files were generated
8. cp convert.off.to.ply.py ./19000_input_files     #this is a file which will convert all the .off files into .ply files
9. python3 convert.off.to.ply.py .    #this will convert all the .off files into .ply files
10. cd ./19000_input_files/outputs_ply    #navigate to directory with .ply tooth files
11. ls -1 ./*.ply | wc -l    #should be 19000!
12. mkdir opc    #this will be the directory where we save the orientation patch count rotated values for each .ply file
13.  (copy the following files to ./outputs_ply : calc_opc.py, topomesh.py, plython.py, DNE.py, implicitfair.py, normcore.py, OPC.py, RFI.py, 1opc.py, run_opc.py)
14.  python3 run_opc.py    #this will generate a .txt file called commands_opc.txt, which is a command to calculate the opc for each .ply tooth file in an efficient manner
15.  addqueue -c "5 minutes" -n 100 /usr/local/shared/bin/multirun ./commands_opc.txt    #this will calculate the OPC values for all the .ply files in the directory and save them in /opc
16.  ls *.txt -1 | wc -l    #running this inside ./opc will allow you to monitor progress, speicifically how many ./opc values have been calculated.
17.  cp extract_opc.py ./outputs_ply    #copy extract_opc.py into the correct folder for its use
18.  python3 extract_opc.py ./opc     #this will extract the OPC values from the .txt files and save them in a list: ./opc/opc_list.txt
19.  cd ./19000_input_files    #navigate to directory where .off files are stored
20.  cp count_cusp_off.py into ./19000_input_files    #ensure code to count cusps of the .off files is in the correct directory
21.  python3 count_cusp_off.py ./19000_input_files     #running this will create a new subdirectory called ./z_batch_results. In this directory, three text files will be generated: 1)z_full_batch_out.txt, which contains a full summary of each tooth .off file, including: File ID (from the filename), Angle in radians and degrees between a primary cusp (cusp A, the one closest to the origin) and its immediate neighbors (to the left and right in X), Notes (such as 'Missing B and/or C cusp' or angle issues), Number of real cusps detected, Whether it failed the inhibitory cascade test (whether other cusps are lower than cusp A in Z.). 2) angles.txt, which contains the same fields as above but is used to focus on successfully calculated angles.. 3) fails.txt, which contains records of files that had issues, such as: Missing neighboring cusps, Invalid angles, Failures in the inhibitory cascade test.
23.  (copy the following files into the same directory: combine_opc_cusp.py, opc_list.txt, z_full_batch_out.txt)
24.  python3 combine_opc_cusp.py seal_lhs_opc_list.txt z_full_batch_out.txt     #this will combine the opc and cusp data into a single data file which can be plotted and further analyzed

To filter teeth by flat-ness, run python3 check_height.py inside the directory containing .off files.

Code steps to generate mutant teeth from parent tooth using OPCR and cusp counts as the measurement for complexity (figures 3b-c & 4b-c):
1. python3 mut.py P4.txt     #Beginning with parent tooth (for example) P4.txt, this will generate 19000 mutant txt files within specific ranges (see mut.py to alter these ranges) inside ./mutants
2. python3 make_off_multi.py ./mutants/ ./mutants/      #this will generate a multirun input file to generate teeth in the cluster
3. copy ./runt.e , ./convert.off.to.ply.py , and ./count_cusp_off into ./mutants
4. (if needed) find . -type f -name 'multirun.txt' -exec sed -i '/\.\/runt\.e \.\/multirun\.txt \. multirun 5900 1/d' {} +     #this removes the last line of the multirun input file, which says ./runt.e ./multirun.txt . multirun 5000 1
5. chmod +x multirun.txt
6. addqueue -n 33 /usr/local/shared/bin/multirun ./multirun.txt      #this will submit the job to the cluster to generate all the .off files inside 16000_input_files, to monitor when each folder has 16000 .off files
7. ls -1 ./*.off | wc -l      #this will tell you how many .off files were generated
8. python3 convert.off.to.ply.py .      #this will convert all the .off files into .ply files
9. (copy the following files to ./outputs_ply : calc_opc.py, topomesh.py, plython.py, DNE.py, implicitfair.py, normcore.py, OPC.py, RFI.py, 1opc.py, run_opc.py)
10. python3 run_opc.py    #this will generate a .txt file called commands_opc.txt, which is a command to calculate the opc for each .ply tooth file in an efficient manner
####From here, continue with step #15 above####

This project builds on the original ToothMaker computational model of tooth development, developed by Salazar-Ciudad & Jernvall:

Salazar-Ciudad I, Jernvall J. A computational model of teeth and the developmental origins of morphological variation. Nature. 2010 Mar 25;464(7288):583–586. https://doi.org/10.1038/nature08838

If you use this code or model in your work, please cite the original paper.
