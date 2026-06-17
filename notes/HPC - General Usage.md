# HPC - General

wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --load-cookies cookies.txt https://hpc.rockefeller.edu/

## GPU/CUDA

All of the GPU nodes on the cluster have CUDA toolkit installed.

The L40 nodes in particular have been tested with different toolkit versions (cuda-11.2 to cuda-12.4).

You can use the `sinfo -p` command to see the L40 nodes:

- on the RHEL7 cluster: `sinfo -p hpcl40,hpc_l40_bigmem`
- on the Rocky 9 cluster: `sinfo -p hpc_l40s`

## SSH Tunnel

On your local machine, create the following entries in `~/.ssh/config` :

```bash

Host ruhpc_vsc
HostName login05-hpc.rockefeller.edu
User <USERNAME>

Host ruhpc_vsc_x
ProxyCommand ssh ruhpc_vsc "nc $(squeue --me --name=VSCode_tunnel --states=R -h -O NodeList,Comment)"
StrictHostKeyChecking no
User <USERNAME>
```

### MATLAB License Setup

```bash

mkdir -p ~/.matlab/R2022a_licenses
cp /ru-auth/local/home/ruitsoft/soft/matlab/current/licenses/network.lic ~/.matlab/R2022a_licenses/
```

Run commands without an interactive shell:

```bash

ssh mbo_data@dtn02-hpc.rockefeller.edu "ls -lh /lustre/fs4/mbo/scratch/mbo_data/"

ssh mbo_data@dtn02-hpc.rockefeller.edu "rm -rf /lustre/fs4/mbo/scratch/mbo_data/single_hemisphere"

ssh mbo_data@dtn02-hpc.rockefeller.edu "ls -lh /lustre/fs4/mbo/scratch/mbo_data/"
```

## HPC Storage Quotas

```bash

for d in $MBO_SCRATCH $MBO_STORE do
    [ -d "$d" ] || { echo "== $d (not found) =="; continue; }
    pid=$(lfs project -d "$d" | awk '{print $1}')
    echo "== $d (project $pid) =="
    lfs quota -h -p "$pid" /lustre/fs8
done

== /lustre/fs8/mbo/scratch (project 88040637) ==
Disk quotas for prj 88040637 (pid 88040637):

    Filesystem    used   quota   limit   grace   files   quota   limit   grace
    /lustre/fs8  134.5G      1T      1T       -  268794  1048576 1048576       -

== /lustre/fs8/mbo/store (project 78040637) ==
Disk quotas for prj 78040637 (pid 78040637):

    Filesystem    used   quota   limit   grace   files   quota   limit   grace
    /lustre/fs8     20k      4G      4G       -       5    4096    4096       -
```
