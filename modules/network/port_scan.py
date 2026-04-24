import nmap

def scan_target(ip_address):
    """Executes a real, fast network scan using Nmap."""
    nm = nmap.PortScanner()
    try:
        # -F performs a fast scan of the top 100 ports. -T4 speeds up execution.
        nm.scan(ip_address, arguments='-F -T4')
        
        open_ports = []
        if ip_address in nm.all_hosts():
            for proto in nm[ip_address].all_protocols():
                lport = nm[ip_address][proto].keys()
                for port in sorted(lport):
                    if nm[ip_address][proto][port]['state'] == 'open':
                        open_ports.append(port)
        return open_ports
    except nmap.PortScannerError:
        print("[-] Nmap Error: Is Nmap installed and in your system PATH?")
        return []
    except Exception as e:
        print(f"[-] Scan Execution Failed: {e}")
        return []