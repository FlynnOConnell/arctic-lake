RBO-W1 License Debugging
## Generate Report
1. In Remote Desktop Licensing Manager right-click the license server, click **Create Report**, and then click **CAL Usage**.
    
2. The report is created and a message appears to confirm that the report was successfully created. Click **OK** to close the message.

## Notes
From [ms-2019 cal not showing up](https://learn.microsoft.com/en-us/answers/questions/689967/rds-server-2019-cals-not-showing-as-installed)
- Event Viewer\Applications and Services Logs\Microsoft\Windows\TerminalServices-Licensing for clues 

Phil created:
Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\RCM\Licensing Core
- LicensingMode (REG_DWORD): 4
- LServerName (REG_SZ): RBO-W1

To refresh license issued, delete this: 
![[Pasted image 20251203105536.png]]

## Folder Permissions
- You should only be allowing users the permissions they need, not denying any permissions, and also adding the administrator group or user the ability to allow them to create folders and write.

- Server Setup (New Account)
	- Sign into Jetbrains with rockefeller.edu email ![[Pasted image 20250719113424.png]]
	- Remove browsers from start menu/desktop/shortcuts
	- File explorer -> view -> show hidden files, show file extension

File permissions, default, for C:/
![[Pasted image 20250815142221.png]]
Steps:
- Right-click `C:\` → **Properties** → **Security** → **Advanced**.
- Find the `Users` or `Authenticated Users` entry.
- Edit → uncheck `Create folders / append data`.
- Leave **Read & execute**, **List folder contents**, and **Read**.
- Apply to `This folder only`.

## Accessing client from another server 
![[Pasted image 20250910143155.png]]

Pulling data from RBO-W1 -> RBO-W2
![[Pasted image 20250910143531.png]]

# Users Forgetting to Log-Out

`FO: 2025-09-19`

Event Viewer -> Windows Logs -> Application -> Error:
```powershell
Faulting application name: LogonUI.exe, version: 10.0.20348.1, time stamp: 0x8b367c97
```

## What causis LogonUI.exe errors?
> The **LogonUI.exe exception error** typically occurs due to corrupted system files, outdated or faulty graphics drivers, or malicious software. It can also happen if third-party applications interfere with the user interface during startup, especially software that modifies login screens or applies custom themes.

[Same issue on MS forum](https://learn.microsoft.com/en-us/answers/questions/2244658/rdp-issues-for-a-single-user-faulting-application)
> This issue appears to be related to the LogonUI.exe process crashing due to a problem with the Windows.UI.Xaml.dll module during RDP connections. The error code 0xc000027b typically indicates a DLL initialization failure.

## Steps to Fix 
1. `sfc /scannow`

```
(base) PS C:\Windows\system32> sfc /scannow

Beginning system scan.  This process will take some time.

Beginning verification phase of system scan.
Verification 100% complete.

Windows Resource Protection found corrupt files but was unable to fix some of them.

For online repairs, details are included in the CBS log file located at
windir\Logs\CBS\CBS.log. For example C:\Windows\Logs\CBS\CBS.log. For offline
repairs, details are included in the log file provided by the /OFFLOGFILE flag.
```

#### Contents of CBS.log
2025-09-19 14:40:05, Info                  CSI    0000012b Hashes for file member [l:23]'tls_branding_config.xml' do not match.
 Expected: {l:32 ml:33 b:045852938e96aa28197993a6efc401407d94185aff8c13172ad3252ff711ba45}.
 Actual: {l:32 b:49c898176d9ad8669bb1761a62e4fddb9da3b98f8cc3a311db7ac374bc4d2c37}.
2025-09-19 14:40:05, Info                  CSI    0000012c [SR] Could not reproject corrupted file \??\C:\Windows\System32\\tls_branding_config.xml; source file in store is also corrupted
2025-09-19 14:40:05, Info                  CSI    0000012d Hashes for file member [l:20]'LServer_PKConfig.xml' do not match.
 Expected: {l:32 ml:33 b:d89ab0d7cf6262145ab3517febd26dbb95297bdf0adb72d551746f4e409eb089}.
 Actual: {l:32 b:cfa5c1d46b882f7980fbacca01c6cfe80aad5ec96392d3f839dbd7ef27f40321}.
2025-09-19 14:40:05, Info                  CSI    0000012e [SR] Cannot repair member file [l:20]'LServer_PKConfig.xml' of Microsoft-Windows-TerminalServices-LicenseServer-LRWIZDLL, version 10.0.20348.2849, arch amd64, nonSxS, pkt {l:8 b:31bf3856ad364e35} in the store, hash mismatch
2025-09-19 14:40:05, Info                  CSI    0000012f [SR] This component was referenced by [l:102]'Microsoft-Windows-TerminalServices-Licensing-Package~31bf3856ad364e35~amd64~~10.0.20348.3207.Licensing'
2025-09-19 14:40:05, Info                  CSI    00000130 [SR] This component was referenced by [l:108]'Microsoft-Windows-TerminalServices-Licensing-UI-Package~31bf3856ad364e35~amd64~~10.0.20348.2849.Licensing-UI'
2025-09-19 14:40:05, Info                  CSI    00000131 Hashes for file member [l:20]'LServer_PKConfig.xml' do not match.
 Expected: {l:32 ml:33 b:d89ab0d7cf6262145ab3517febd26dbb95297bdf0adb72d551746f4e409eb089}.
 Actual: {l:32 b:cfa5c1d46b882f7980fbacca01c6cfe80aad5ec96392d3f839dbd7ef27f40321}.
2025-09-19 14:40:05, Info                  CSI    00000132 Hashes for file member [l:20]'LServer_PKConfig.xml' do not match.
 Expected: {l:32 ml:33 b:d89ab0d7cf6262145ab3517febd26dbb95297bdf0adb72d551746f4e409eb089}.
 Actual: {l:32 b:cfa5c1d46b882f7980fbacca01c6cfe80aad5ec96392d3f839dbd7ef27f40321}.
2025-09-19 14:40:05, Info                  CSI    00000133 [SR] Could not reproject corrupted file \??\C:\Windows\System32\\LServer_PKConfig.xml; source file in store is also corrupted
2025-09-19 14:40:06, Info                  CSI    00000134 [SR] Verify complete

We have the same hashing errors as mentioned [here](https://learn.microsoft.com/en-us/answers/questions/2082598/the-tls-branding-config-xml-and-lserver-pkconfig-x), where this user had users forced to use temporary profiles when RDP into the server.

[This post](https://learn.microsoft.com/en-us/answers/questions/4286055/how-do-i-fix-a-logonui-exe-system-error-with-a-bla) , similar UI error, recommended soulution is "reboot, make a new account"

2. [DISM](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/what-is-dism?view=windows-11)
	1. `DISM /Online /Cleanup-Image /RestoreHealth`

```
(base) PS C:\Windows\system32> DISM /Online /Cleanup-Image /RestoreHealth                                                                                                                                                                       Deployment Image Servicing and Management tool                                                                          Version: 10.0.20348.2849                                                                                                                                                                                                                        Image Version: 10.0.20348.3328                                                                                                                                                                                                                  [==========================100.0%==========================] The restore operation completed successfully.              The operation completed successfully.  
```

3. Disable UDP and force TCP by editing the RDP file and adding "enablecredsspsupport:i:0"
- Try a different RDP client version or compatibility mode

/Restore-Health: Replaces corrupted files with those fetched by windows update

### Windows Component Store
- DISM works on [Windows Component Store](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/manage-the-component-store?view=windows-11): Functions for custom/updating of windows
	- Using Windows Update to install new component versions. This keeps systems secure and up-to-date.
	- Enabling or disabling Windows features.
	- Adding roles or features using Server Manager.
	- Moving systems between different Windows Editions.
	- System recovery from corruption or boot failures
	- Uninstalling problematic updates
	- Running programs using side-by-side assemblies


# License Server Issues
#`FO 2025-10-06`

## Problem
Kevin Barber @ Vaziri lab is being disconnected from RBO-W1 Beta due with these dialog popups. He can reconnect, but it will boot him every hour. Have you made any group-policy / license changes? I haven't so I'm not sure why this is becoming an issue now. I can log onto MBO-Beta, Admin and Delta without issue.
## Sources
-  [Your session will be disconnected in 60 minutes when you connect to RDS](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/your-session-will-be-disconnected-in-60-minutes)
- [Cannot connect to RDS because no RD Licensing servers are available](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/cannot-connect-rds-no-license-server)
- [License Remote Desktop Services with Client Access Licenses (CALs)](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-client-access-license)
- [Best practices for setting up RD licensing across Active Directory domains/forests or work groups](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/set-up-remote-desktop-licensing-across-domains-forests-workgroups)
- [Install Remote Desktop Services client access licenses](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-install-cals)

## Notes
- In Windows Server 2022, the “soft enforcement of per-device licensing” behavior (i.e. allowing a session for 60 minutes) still can occur if licensing is not resolved properly.
- There's a licensing grace period of 120 days during which no license server is required. Once the grace period ends, clients must have a valid RDS CAL issued by a license server before they can sign in a remote session.
- Per-device CALs are the only supported type of license within work-groups mode

## Cause: I'm taking 2 device licenses because I logged in from my HOME desktop
- Per-device CAL's grace period is over
- I'm not sure why kevins log-in isn't replacing my login
![[Pasted image 20251006131735.png]]

## Solution 1: Convert to per-user mode, convert the server-mode
- Why did we chose `per-device CALS` ?
- `per-user CALS` seems intuitively what we weould want
- Do we need to switch to rockefeller domain?
- Can we switch without being on the domain?

## Solution 2: Buy more licenses
- Aquire more MPSA License 
- deborah.varga@connection.com 
- mikep@mail.rockefeller.edu

### Can we use both per-device and per-user?
For both Per Device and Per User CALs issuance to work, the RD Session Host and RD licensing server in any one of the following three configurations:

- Both in the same work group
- Both in the same domain
- Both in the trusted (Two-way trust) Active Directory Domains or Forest

Here is more information on these scenarios:

- RD Session Host and RD licensing servers are in the same work group
    
    Consider the following points while configuring RDS and RD licensing servers in a work group environment:
    
    - We can use ONLY Per Device CALs in a work group environment. So, you should install only Per Device CALs on RD licensing server.
    - Per User CAL tracking and reporting is not supported in work group mode.
    - RD Session Host and RD licensing server roles can both be installed on the same server.
    - If you install RD licensing server on a different server in the work group, ensure that the RDS server is able to access RD licensing server.
	- Per User CAL tracking and reporting is not supported in work group mode.


#`FO 2025-10-06`

## Problem
Kevin Barber @ Vaziri lab is being disconnected from RBO-W1 Beta due with these dialog popups. He can reconnect, but it will boot him every hour. Have you made any group-policy / license changes? I haven't so I'm not sure why this is becoming an issue now. I can log onto MBO-Beta, Admin and Delta without issue.

## Sources
- Tobias 
-  [Your session will be disconnected in 60 minutes when you connect to RDS](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/your-session-will-be-disconnected-in-60-minutes)
- [Cannot connect to RDS because no RD Licensing servers are available](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/cannot-connect-rds-no-license-server)
- [License Remote Desktop Services with Client Access Licenses (CALs)](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-client-access-license)
- [Best practices for setting up RD licensing across Active Directory domains/forests or work groups](https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/set-up-remote-desktop-licensing-across-domains-forests-workgroups)
- [Install Remote Desktop Services client access licenses](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-install-cals)

## Notes
- In Windows Server 2022, the “soft enforcement of per-device licensing” behavior (i.e. allowing a session for 60 minutes) still can occur if licensing is not resolved properly.
- There's a licensing grace period of 120 days during which no license server is required. Once the grace period ends, clients must have a valid RDS CAL issued by a license server before they can sign in a remote session.
- Per-device CALs are the only supported type of license within work-groups mode

## Cause: 
I'm taking 2 device licenses because I logged in from my HOME desktop. Will Snyder has a license, and RBO-D1 has a license.

***Note: Can only revoke 1 licence per 90 days***

- Per-device CAL's grace period is over.
- I'm not sure why kevins log-in isn't replacing my login
![[Pasted image 20251006131735.png]]

## Solution 1: Convert to per-user mode

- Note: Can only revoke 1 licence per 90 days
- Why did we chose `per-device CALS` ? (likely workgroup-related)
- `per-user CALS` seems intuitively what we would want
- Do we need to switch to rockefeller domain for per-user CALS? YES
- Tobias uses per-user CALS

## Solution 2: Buy more licenses
- Aquire more MPSA License 
- Easier, more "plug and play"
- Users with multiple computers (laptop, lab workstation) will use a license for each of these devices
- deborah.varga@connection.com 
- mikep@mail.rockefeller.edu

### Can we use both per-device and per-user?
For both Per Device and Per User CALs issuance to work, the RD Session Host and RD licensing server in any one of the following three configurations:

- Both in the same work group
- Both in the same domain
- Both in the trusted (Two-way trust) Active Directory Domains or Forest
- RD Session Host and RD licensing servers are in the same work group
    Consider the following points while configuring RDS and RD licensing servers in a work group environment:
    - We can use ONLY Per Device CALs in a work group environment. So, you should install only Per Device CALs on RD licensing server.
    - Per User CAL tracking and reporting is not supported in work group mode.
    - RD Session Host and RD licensing server roles can both be installed on the same server.
    - If you install RD licensing server on a different server in the work group, ensure that the RDS server is able to access RD licensing server.
	- Per User CAL tracking and reporting is not supported in work group mode.

## Per-User vs Per-Device Client-Access-Licenses
**Per-User CAL**
- License one **user** to access the server from any device.
- Good when users need to connect from multiple devices (desktop, laptop, phone).
- You need as many User CALs as the headcount of distinct users accessing services.
- Doesn’t matter how many devices they use (see [Client Access Licenses and Management Licenses](https://www.microsoft.com/en-us/licensing/product-licensing/client-access-license)).
    
**Per-Device CAL**
- License one **device** (regardless of how many users use it) to access the server.
- Good when many users share the same workstation (shift work, kiosks, labs).
- You need as many Device CALs as the number of devices that connect.

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
