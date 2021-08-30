#!/bin/bash

### Rescale Job Definition
NAME=Fluent-PBS
NPROCS=8
INPUTS=fluent-input.zip
JOURNAL=run.jou
WTIME=2

### Scheculer Script Definition
export PBS_SCRIPT=".$NAME"\_"$NPROCS"\_"$INPUTS"\_"$WTIME".qsub
echo "#!/bin/bash" > $PBS_SCRIPT

echo "" >> $PBS_SCRIPT
echo "### Build PBS scripts" >> $PBS_SCRIPT
echo "#PBS -q rescale" >> $PBS_SCRIPT
echo "#PBS -N "$NAME"" >> $PBS_SCRIPT
echo "#PBS -l walltime="$WTIME":00:00" >> $PBS_SCRIPT
echo "#PBS -k oe" >> $PBS_SCRIPT
echo "#PBS -j oe" >> $PBS_SCRIPT
echo "cd \$PBS_O_WORKDIR" >> $PBS_SCRIPT

echo "" >> $PBS_SCRIPT
echo "### Rescale job kill when qdel sends SIGTERM" >> $PBS_SCRIPT
echo "PROGRAM=\$0" >> $PBS_SCRIPT
echo "trap 'echo "\$\{PROGRAM\} received signal SIGTERM"' SIGTERM" >> $PBS_SCRIPT

echo "" >> $PBS_SCRIPT
echo "### Rescale Job Command" >> $PBS_SCRIPT
echo "fluent_batch_job.py --name "$NAME" --nprocs "$NPROCS" --inputs "$INPUTS" --journal "$JOURNAL" --wtime "$WTIME"" >> $PBS_SCRIPT

### Submit Job to Rescale
qsub $PBS_SCRIPT

### Remove Schduler script
rm -f $PBS_SCRIPT
