import subprocess
import json

def engage_nuclei_strike(target_ip, port, service_name):
    """
    Dynamic Exploit Router.
    Maps service intelligence to specific Nuclei CVE templates.
    """
    target_url = f"http://{target_ip}:{port}"
    if port in [443, 8443]:
        target_url = f"https://{target_ip}:{port}"

    print(f"[*] [WEAPONS HOT] Routing templates for {service_name} on {target_url}...")

    # Dynamic Tag Routing: Build the attack profile based on Kamui's intelligence
    attack_tags = ["cves", "default-logins", "misconfiguration", "exposure"]
    
    service_lower = service_name.lower()
    if "wordpress" in service_lower:
        attack_tags.append("wordpress")
    elif "nginx" in service_lower or "apache" in service_lower:
        attack_tags.append("web-server")
    elif "tomcat" in service_lower:
        attack_tags.append("tomcat")

    tag_string = ",".join(attack_tags)

    # Construct the headless Nuclei command
    command = [
        "nuclei",
        "-u", target_url,
        "-tags", tag_string,
        "-severity", "critical,high,medium",
        "-j",        # Output strictly in JSON
        "-silent"    # Mute the ASCII banners and progress bars
    ]

    try:
        # Fire the weapon. Timeout after 5 minutes to prevent queue blocking.
        process = subprocess.run(command, capture_output=True, text=True, timeout=300)
        
        # Parse the JSON results from Nuclei
        if process.stdout:
            for line in process.stdout.strip().split('\n'):
                try:
                    finding = json.loads(line)
                    vuln_name = finding.get('info', {}).get('name', 'Unknown')
                    severity = finding.get('info', {}).get('severity', 'Unknown').upper()
                    print(f"[!!!] [CRITICAL HIT] {severity} | {vuln_name} found on {target_url}")
                except json.JSONDecodeError:
                    continue
        else:
            print(f"[-] Strike complete. No vulnerabilities found on {target_url}.")
            
    except subprocess.TimeoutExpired:
        print(f"[-] [TIMEOUT] Nuclei strike aborted on {target_url} (exceeded 300s).")
    except Exception as e:
        print(f"[-] [ERROR] Weapon malfunction: {e}")