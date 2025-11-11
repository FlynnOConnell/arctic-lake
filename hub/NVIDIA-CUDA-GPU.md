# NVIDIA / GPU

Resources
- https://www.leadergpu.com/articles/504-check-nvlink-in-windows
- https://techcommunity.microsoft.com/discussions/compute/nv-series---wddm-vs-tcc/143568


- **NC, NCv2, and ND** sizes are optimized for compute-intensive and network-intensive applications and algorithms, including CUDA- and OpenCL-based applications and simulations, AI, and Deep Learning.
- **NV** sizes are optimized and designed for remote visualization, streaming, gaming, encoding, and VDI scenarios utilizing frameworks such as OpenGL and DirectX.

- TCC: Tensor Compute Cluster
	- Disables windows graphics driver
- WDDM: Windows Display Driver Model
- TCC being useful for compute workloads (NC or ND size) vs WDDM being appropriate for graphics workloads (NV size). In my experience, when the GPU is in TCC mode, RDP sessions are not able to leverage the GPU. Using the nvidia-smi tool to change the mode to WDDM:

`nvidia-smi -g {_GPU_ID_} -dm 0`

- GPU changing settings is likely due to settings being stored in the EEPROM of the GPU
- Windows operates in WDDM mode **by default**
![[Pasted image 20250908104433.png]]
## WDDM to TCC

For instance, if you want to run C/C++ CUDA® applications, you need to switch the driver on each GPU to a different operating mode: TCC (Tesla® Compute Cluster):

```
>> nvidia-smi -i 0 -dm TCC

Set driver model to TCC for GPU 00000000:03:00.0.
All done.
Reboot required.
```

Here, 0 is an ID of the GPU. You can see all IDs (started from 0) in the nvidia-smi output (first column). Apply this action to each GPU and finally reboot the server.

### Back to WDDM?
`nvidia-smi -i 0 -dm WDDM`

- Some cases require a hybrid method, potentially GPU0 for WDDM GPU1 for TCC

## GPU on RDP
Samples: https://github.com/NVIDIA/cuda-samples/archive/refs/heads/master.zip
Resource: https://www.leadergpu.com/articles/513-gpu-rendering-in-rdp

Might need to enable **RemoteFX** to allow GPU rendering over RDP

CTRL + R -> gpedit.msc
```
Administrative Templates > Windows Components > Remote Desktop Services > Remote Desktop Session Host > Remote Session Environment > RemoteFX for Windows Server
```
Select the **Configure RemoteFX** option and right-click on it. Select **Edit**:
![[Pasted image 20250908105159.png]]

Do the same for the **Optimize visual experience for Remote Desktop Service Sessions** item. Select **Edit** from the context menu:

![[Pasted image 20250908105226.png]]

## NVIDIA-SMI, nvcc versioning
[StackOverflow Source](https://stackoverflow.com/questions/53422407/different-cuda-versions-shown-by-nvcc-and-nvidia-smi)
- CUDA has 2 primary APIs, the runtime and the driver API. Both have a corresponding version (e.g. 8.0, 9.0, etc.)
- If version reported by `nvidia-smi` is a numerically lower value than the version reported by `nvcc`,  probably a broken config.

This can be a problem when downloading CUDA compatibility packages.

**nvcc: 11.8**
```
PS C:\Users\RBO\repos\mbo_utilities> nvcc --version
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2022 NVIDIA Corporation
Built on Wed_Sep_21_10:41:10_Pacific_Daylight_Time_2022
Cuda compilation tools, release 11.8, V11.8.89
Build cuda_11.8.r11.8/compiler.31833905_0
```

**nvidia-smi: 12.4 (not even installed)**
```
PS C:\Users\RBO\repos\mbo_utilities> nvidia-smi
Thu Sep 18 11:10:49 2025
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 553.09                 Driver Version: 553.09         CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                     TCC/WDDM  | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA RTX A4000             WDDM  |   00000000:01:00.0  On |                  Off |
| 41%   31C    P8             11W /  140W |    6809MiB /  16376MiB |      1%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```

**Installed CUDA versions:**
```
PS C:\Users\RBO\repos\mbo_utilities> ls "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"


    Directory: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         9/16/2025  11:40 AM                v11.8
d-----         11/8/2024   3:16 PM                v12.6
d-----         8/21/2025  10:01 AM                v9.0
```
