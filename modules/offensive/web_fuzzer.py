import requests

def fuzz_web_port(ip_address, port):
    """
    Surgical strike: Fires only when a new port is discovered.
    Hunts for exposed critical files on the new web service.
    """
    print(f"\n[*] [ENGAGING CLAWS] Fuzzing new web service on {ip_address}:{port}...")
    
    # Common highly-critical paths that shouldn't be exposed
    payloads = ['/.env', '/admin', '/config.json', '/server-status', '/swagger.json']
    
    base_url = f"http://{ip_address}:{port}"
    found_vulnerabilities = []

    for payload in payloads:
        target_url = f"{base_url}{payload}"
        try:
            # Short timeout. We are moving fast.
            response = requests.get(target_url, timeout=3)
            
            # If we get a 200 OK and it's not a generic redirect/error page
            if response.status_code == 200 and "404" not in response.text:
                print(f"[!!!] CRITICAL HIT: Exposed file found at {target_url}")
                found_vulnerabilities.append(target_url)
        except requests.exceptions.RequestException:
            pass # Ignore connection resets or timeouts

    if not found_vulnerabilities:
        print(f"[-] Fuzzing complete. No immediate critical files exposed on port {port}.")
        
    return found_vulnerabilities