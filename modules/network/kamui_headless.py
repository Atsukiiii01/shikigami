import nmap
import hashlib
import json

def execute_kamui_scan(target_host, scan_type="pulse"):
    """
    Headless Kamui integration.
    Repaired: Dynamic DNS resolution handling.
    """
    nm = nmap.PortScanner()
    
    if scan_type == "pulse":
        scan_args = '-Pn -p 21,22,80,443,8000,8080,8443 -T4'
        print(f"[*] [KAMUI] Executing Pulse Scan on {target_host}...")
    elif scan_type == "interrogation":
        scan_args = '-Pn -p- -sV -T4'
        print(f"[*] [KAMUI] Executing Deep Interrogation on {target_host}...")
    else:
        return None

    try:
        nm.scan(target_host, arguments=scan_args)
        
        # THE FIX: Nmap returns the resolved IP, not the hostname. 
        # We dynamically grab the actual host Nmap processed.
        hosts = nm.all_hosts()
        if not hosts:
            return None
            
        scanned_ip = hosts[0]

        open_ports = []
        services = {}
        
        for proto in nm[scanned_ip].all_protocols():
            lport = nm[scanned_ip][proto].keys()
            for port in sorted(lport):
                state = nm[scanned_ip][proto][port]['state']
                if state == 'open':
                    open_ports.append(port)
                    
                    if scan_type == "interrogation":
                        service_name = nm[scanned_ip][proto][port].get('name', 'unknown')
                        service_version = nm[scanned_ip][proto][port].get('version', '')
                        services[str(port)] = f"{service_name} {service_version}".strip()
                    else:
                        services[str(port)] = "unverified"

        hash_source = json.dumps(open_ports, sort_keys=True)
        state_hash = hashlib.md5(hash_source.encode('utf-8')).hexdigest()

        return {
            "target": target_host,  # Keep original subdomain for the memory bank
            "open_ports": open_ports,
            "services": services,
            "state_hash": state_hash
        }

    except nmap.PortScannerError as e:
        print(f"[-] [KAMUI] Nmap Execution Error: {e}")
        return None
    except Exception as e:
        print(f"[-] [KAMUI] Fatal Scan Error: {e}")
        return None