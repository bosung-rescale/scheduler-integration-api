#!/bin/bash

### Rescale Job Definition
NAME=Fluent-LSF
NPROCS=8
INPUTS=fluent-input.zip
JOURNAL=run.jou
WTIME=2

### Scheculer Script Definition
export LSF_SCRIPT=".$NAME"\_"$NPROCS"\_"$INPUTS"\_"$WTIME".bsub
echo "#!/bin/bash" > $LSF_SCRIPT

echo "" >> $LSF_SCRIPT
echo "### Build LSF scripts" >> $LSF_SCRIPT
echo "#BSUB -q rescale" >> $LSF_SCRIPT
echo "#BSUB -J "$NAME"" >> $LSF_SCRIPT
echo "#BSUB -W "$WTIME":00" >> $LSF_SCRIPT
echo "#BSUB -o "$NAME".o%J" >> $LSF_SCRIPT
echo "#BSUB -e "$NAME".e%J" >> $LSF_SCRIPT

echo "" >> $LSF_SCRIPT
echo "### Rescale Job Command" >> $LSF_SCRIPT
echo "fluent_batch_job.py --name "$NAME" --nprocs "$NPROCS" --inputs "$INPUTS" --journal "$JOURNAL" --wtime "$WTIME"" >> $LSF_SCRIPT

### Submit Job to Rescale
bsub < $LSF_SCRIPT

### Remove Schduler script
rm -f $LSF_SCRIPT
