import requests

def execute_shovel_recon(domain):
    """
    Headless Shovel integration.
    Scrapes Certificate Transparency logs with enterprise timeouts and WAF evasion.
    """
    print(f"[*] [THE SHOVEL] Engaging OSINT sweep for root domain: {domain}")
    subdomains = set()
    
    # Masking the bot signature to bypass basic WAF throttling
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        # Increased timeout to 90 seconds. crt.sh is notoriously slow.
        response = requests.get(url, headers=headers, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                name_value = entry.get('name_value', '')
                clean_names = name_value.replace('*.', '').split('\n')
                for name in clean_names:
                    if name.endswith(domain):
                        subdomains.add(name.strip())
                        
        print(f"[+] [THE SHOVEL] Discovered {len(subdomains)} subdomains for {domain}")
        return list(subdomains)
        
    except Exception as e:
        print(f"[-] [THE SHOVEL] Recon failed or timed out: {e}")
        return []