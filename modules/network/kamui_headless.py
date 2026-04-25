import nmap
import hashlib
import json

def execute_kamui_scan(ip_address, scan_type="pulse"):
    """
    Headless Kamui integration for Celery workers.
    Zero GUI. Zero interactive prompts. Pure data extraction.
    """
    nm = nmap.PortScanner()
    
    # Gear Shifting: Determine scan depth based on the engine's request
    if scan_type == "pulse":
        # Fast baseline check (Top 100 ports, fast timing)
        scan_args = '-F -T4'
        print(f"[*] [KAMUI] Executing Pulse Scan on {ip_address}...")
    elif scan_type == "interrogation":
        # Deep inspection (All ports, service versions)
        scan_args = '-p- -sV -T4'
        print(f"[*] [KAMUI] Executing Deep Interrogation on {ip_address}...")
    else:
        return None

    try:
        nm.scan(ip_address, arguments=scan_args)
        
        if ip_address not in nm.all_hosts():
            return None

        open_ports = []
        services = {}
        
        for proto in nm[ip_address].all_protocols():
            lport = nm[ip_address][proto].keys()
            for port in sorted(lport):
                state = nm[ip_address][proto][port]['state']
                if state == 'open':
                    open_ports.append(port)
                    
                    # Extract service version if available (for Interrogation mode)
                    service_name = nm[ip_address][proto][port].get('name', 'unknown')
                    service_version = nm[ip_address][proto][port].get('version', '')
                    services[str(port)] = f"{service_name} {service_version}".strip()
                    
        # Generate the state hash. If the admin upgrades a service, the ports 
        # stay the same, but the hash mutates.
        services_json = json.dumps(services, sort_keys=True)
        state_hash = hashlib.md5(services_json.encode('utf-8')).hexdigest()

        return {
            "target": ip_address,
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