# Dual RTX A5000 — CUDA enumeration troubleshooting

Commands used to diagnose the second A5000 (PCI bus `2A`, tried in TCC then WDDM) not
appearing to CUDA while healthy in NVML/Windows. Run nvidia-smi `-dm`, PnP, and `-r`
commands from an **elevated** PowerShell.

## CUDA visibility test

Torch is available and correctly using GPU at index 0:

```powershell
uv run python -c "import torch; print('avail:', torch.cuda.is_available(), 'count:', torch.cuda.device_count())"

True
1
```

Pin a single card by UUID — `cudaErrorNoDevice` means it's excluded at enumeration.

```powershell
$env:CUDA_VISIBLE_DEVICES = 'GPU-7a39d1e0-b42b-d9c0-1415-4ea3a96f1336'
uv run python -c "import torch; print(torch.cuda.device_count())"

0
```

Confirm the torch/CUDA build.

```powershell
uv pip show torch

Name: torch
Version: 2.12.0+cu126
```

## Environment variables

Check what's set in the session and persisted in User/Machine scope.

```powershell
Get-ChildItem Env: | Where-Object Name -match 'CUDA|MBO_GPU'
[Environment]::GetEnvironmentVariable('CUDA_VISIBLE_DEVICES','User')
[Environment]::GetEnvironmentVariable('CUDA_VISIBLE_DEVICES','Machine')
```

Clear a stale pin for the current session.

```powershell
Remove-Item Env:CUDA_VISIBLE_DEVICES -ErrorAction SilentlyContinue
```

## nvidia-smi inventory & health

List all GPUs with bus id, UUID, and driver model.

```powershell
nvidia-smi --query-gpu=index,name,uuid,pci.bus_id,driver_model.current --format=csv

0, NVIDIA RTX A5000, GPU-1e45ded4-0d19-c2f6-cbab-178292093452, 00000000:17:00.0, WDDM
1, NVIDIA RTX A5000, GPU-7a39d1e0-b42b-d9c0-1415-4ea3a96f1336, 00000000:2A:00.0, WDDM
```

Full health dump for card 1.

```powershell
nvidia-smi -q -i 1
```

Filter the state flags that would make CUDA reject a card.

```powershell
nvidia-smi -i 1 -q | Select-String -Pattern 'Compute Mode','Pending','Remapped Rows','Retired','Xid','ECC'
```

## Driver model (TCC / WDDM)

Switch card 1 between WDDM (display) and TCC (compute-only).

```powershell
nvidia-smi -i 1 -dm 0   # WDDM
nvidia-smi -i 1 -dm 1   # TCC
```

## NVLink / MIG / topology

NVLink link status and bandwidth per card.

```powershell
nvidia-smi nvlink -s
```

MIG mode — `[N/A]` on A5000 (unsupported), so not the cause.

```powershell
nvidia-smi --query-gpu=index,name,mig.mode.current --format=csv
```

## GPU reset

Attempt a card reset (usually refused under WDDM).

```powershell
nvidia-smi -i 1 -r
```

## Windows device state

PnP status of display devices (look for error/problem codes).

```powershell
Get-PnpDevice -Class Display | Format-Table -Auto Status, FriendlyName, InstanceId
```

Map each display device to its PCI location (bus/slot).

```powershell
Get-PnpDevice -Class Display | ForEach-Object { $_.FriendlyName; ($_ | Get-PnpDeviceProperty -KeyName DEVPKEY_Device_LocationInfo).Data }
```

Disable / re-enable a card without a reboot (no-reboot reset lever).

```powershell
Disable-PnpDevice -InstanceId '<InstanceId>' -Confirm:$false
Enable-PnpDevice  -InstanceId '<InstanceId>' -Confirm:$false
```

## Event log

Recent nvlddmkm events (Event 153 = TDR reset-and-recover).

```powershell
Get-WinEvent -FilterHashtable @{ LogName='System'; ProviderName='nvlddmkm' } -MaxEvents 50 | Select-Object TimeCreated, Id, LevelDisplayName
```
