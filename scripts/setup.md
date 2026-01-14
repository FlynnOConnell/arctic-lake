# Setup on RBO-W2 (Windows)

## 1. Map network drive (already done)
```powershell
net use Y: \\RBO-S1\mbospace /persistent:yes
```

## 2. Clean up shared storage (remove .git from SMB share)
```powershell
Remove-Item "Y:\foconnell\docs\.git" -Recurse -Force
```

## 3. Clone repo on RBO-W2
```powershell
git clone <your-git-remote> $HOME\docs
```

## 4. Copy script
```powershell
# from laptop
scp ~/repos/docs/scripts/docs-sync.ps1 rbo:~/docs/scripts/
scp ~/repos/docs/.gitattributes rbo:~/docs/

# or on RBO-W2, create scripts dir and paste content
mkdir $HOME\docs\scripts
mkdir $HOME\.local\log
```

## 5. Create scheduled task (run as admin)
```powershell
$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-NoProfile -File $HOME\docs\scripts\docs-sync.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd
Register-ScheduledTask -TaskName "DocsSync" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest
```

## 6. Verify
```powershell
Get-ScheduledTask -TaskName "DocsSync"
Start-ScheduledTask -TaskName "DocsSync"  # manual run
Get-Content $HOME\.local\log\docs-sync.log -Tail 20
```

## Uninstall
```powershell
Unregister-ScheduledTask -TaskName "DocsSync" -Confirm:$false
```
