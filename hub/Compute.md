![[Pasted image 20250710232211.png]]

# HPC

## Send File

```powershell
PS C:\Users\RBO\caiman_data\demo> scp .\demo_data.tif mbo_data@dtn02-hpc.rockefeller.edu:/lustre/fs4/mbo/scratch/mbo_data/demo_data.tif
```

## Sync Data

```bash
mbo at RBO-C2 in /mnt/c/Users/RBO
$ rsync -avz foconnell@dtn02-hpc.rockefeller.edu:/ru-auth/local/home/foconnell/scratch/foconnell/ ~/hpc/foconnell/
```

## Every Hour via `crontab`

Edit crontab:

```bash
crontab -e
0 * * * * rsync -avz foconnell@dtn02-hpc.rockefeller.edu:/ru-auth/local/home/foconnell/scratch/foconnell/batch ~/hpc/
```

Output:

```bash
mbo at RBO-C2 in /mnt/c/Users/RBO$ crontab -e
no crontab for mbo - using an empty one
crontab: installing new crontab
```

## Stage Data into tmp nvme

```bash
cp -r /path/to/source/files/* /tmp/mbo/
```

## Apptainer Instructions

### On a node, in `/tmp`

```bash
apptainer pull matlab_r2022a.sif docker://mathworks/matlab:r2022a
```

### MATLAB License Setup

```bash
mkdir -p ~/.matlab/R2022a_licenses
cp /ru-auth/local/home/ruitsoft/soft/matlab/current/licenses/network.lic ~/.matlab/R2022a_licenses/
```

### Basic Shell

```bash
apptainer shell --bind /rugpfs/fs0/vzri_lab/scratch:/vzri_scratch matlab_r2022a.sif
```

### With Writeable Overlay

```bash
apptainer overlay create --size 2048 matlab_r2022a_overlay_nofakeroot.img

apptainer shell --overlay matlab_r2022a_overlay_nofakeroot.img \
  --bind /rugpfs/fs0/vzri_lab/scratch:/vzri_scratch matlab_r2022a.sif
```

Local copy:

```bash
/rugpfs/fs0/vzri/scratch/tnobauer/matlab_r2022a.sif
```

