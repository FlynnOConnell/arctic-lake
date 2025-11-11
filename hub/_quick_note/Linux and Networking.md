# Linux and Networking Reference

---

## Chmod

### User Categories
- **U** → User (usually, you)
- **G** → Group (e.g., sudo group)
- **O** → Others

### Permission Codes

| Bin | Dec | Representation |
|-----|-----|----------------|
| 000 |  0  | ---            |
| 001 |  1  | --x            |
| 010 |  2  | -w-            |
| 011 |  3  | -wx            |
| 100 |  4  | r--            |
| 101 |  5  | r-x            |
| 110 |  6  | rw-            |
| 111 |  7  | rwx            |

### Syntax Examples

```bash
chmod 777 file       # rwx rwx rwx → everyone can do everything
chmod 744 dir        # rwx r-- r-- → only user can write and execute
chmod 200 file2      # -w- --- --- → only user can write
```

```bash
chmod u=rwx,g=rx,o=r filename
```

---

## Format Strings (printf)

| Format | Description                         |
|--------|-------------------------------------|
| `%c`   | character                            |
| `%d`   | decimal (integer, base 10)           |
| `%e`   | exponential floating-point number    |
| `%f`   | floating-point number                |
| `%i`   | integer (base 10)                    |
| `%o`   | octal number (base 8)                |
| `%s`   | string                               |
| `%u`   | unsigned integer                     |
| `%x`   | hexadecimal number (base 16)         |
| `%%`   | print a percent sign                 |
| `\%`   | print a percent sign                 |

---

## Sockets (`ss`)

### General Usage

```bash
ss -a        # all sockets
ss -l        # listening sockets
ss -u        # UDP only
ss -t        # TCP only
ss -lu       # listening UDP
ss -p        # show PID
ss -4        # IPv4 only
ss -6        # IPv6 only
ss -at '( dport = :22 or sport = :22 )'  # filter by port
ss -at '( dport = :ssh or sport = :ssh )'
```

### Extended Commands

```bash
ss | less
ss -t
ss -u
ss -x
ss -at
ss -au
ss -tn
ss -ltn
ss -ltp
ss -s
ss -tn -o
ss -lt4
```

---

## Ports

| Port | Service | Protocol | Description |
|------|---------|----------|-------------|
| 7    | Echo    | TCP/UDP  | Echo service |
| 20   | FTP-data | TCP/SCTP | File Transfer Protocol data |
| 21   | FTP     | TCP/UDP/SCTP | FTP control |
| 22   | SSH     | TCP/UDP/SCTP | Secure Shell, SCP, SFTP |
| 23   | Telnet  | TCP      | Unencrypted remote login |
| 25   | SMTP    | TCP      | Mail server routing |
| 53   | DNS     | TCP/UDP  | Domain name resolution |
| 69   | TFTP    | UDP      | Trivial file transfer |
| 80   | HTTP    | TCP/UDP/SCTP | Web traffic (HTTP/1 & 2) |
| 88   | Kerberos | TCP/UDP | Network authentication |
| 110  | POP3    | TCP      | Post Office Protocol v3 |
| 143  | IMAP4   | TCP/UDP  | Email retrieval |
| 443  | HTTPS   | TCP/UDP/SCTP | Secure HTTP |
| 3306 | MySQL   | TCP      | MySQL database |
| 5432 | PostgreSQL | TCP  | PostgreSQL database |
| 5900 | VNC     | TCP/UDP  | Remote desktop (RFB protocol) |
| 8086 | Kaspersky | TCP   | Antivirus Control Center |
| 9100 | PDL     | TCP      | Network printer stream |
| 10000 | Webmin | unofficial | Web-based Unix admin tool |
| 12345 | NetBus | unofficial | Remote admin trojan |
| 27374 | Sub7   | unofficial | Remote admin trojan |
| 31337 | Back Orifice | unofficial | Remote admin trojan |

---

## SSH Options

| Option | Description |
|--------|-------------|
| `-X`   | Forward X11 |
| `-Y`   | Trusted X11 forwarding |
| `-E`   | Append debug logs to file |
| `-F`   | Use alternate config file |
| `-g`   | Allow remote hosts on forwarded ports |
| `-i`   | Identity (private key) file |
| `-J`   | Jump host |
| `-l`   | Remote login name |
| `-p`   | Remote port |
| `-q`   | Quiet mode |
| `-V`   | Show SSH version |
| `-v`   | Verbose mode |

### Example

```bash
ssh -L 8889:localhost:8889 foconnell@129.85.3.29
```

---

## Signals

- `SIGHUP`: Signal Hang Up – sent when terminal closes
