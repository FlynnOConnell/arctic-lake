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