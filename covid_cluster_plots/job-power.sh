#!/bin/bash                                                                     
#SBATCH -t 24:00:00                                                             
#SBATCH -N 1                                                                    
#SBATCH --mem=60G                                                               
#SBATCH --mail-type=END                                                         
#SBATCH --mail-user=m.b.cetin@vu.nl                                             
#SBATCH -e slurm-%j.err                                                         
#SBATCH -o slurm-%j.out                                                         

python3 /home/cmt2002/cluster_analysis/power_consumption_plot.py surfsara_power_usage
