from workers.celery_app import app
from core.database import ShikigamiCore
from modules.network.kamui_headless import execute_kamui_scan
from modules.offensive.web_fuzzer import fuzz_web_port
from modules.offensive.infra_strike import strike_ftp, strike_ssh

db_engine = ShikigamiCore("data/shikigami_state.db")

@app.task(name="tasks.execute_live_scan")
def execute_live_scan(target_ip):
    print(f"[*] [CELERY WORKER] Engaging Kamui Headless on Target: {target_ip}")
    
    # 1. Engage Sensory Input (Kamui Pulse Scan)
    scan_data = execute_kamui_scan(target_ip, scan_type="pulse")
    
    if scan_data and scan_data["open_ports"]:
        ports = scan_data["open_ports"]
        current_hash = scan_data["state_hash"]
        
        # 2. Feed to the Memory Bank
        new_ports = db_engine.update_asset_state(target_ip, ports, current_hash)
        
        # 3. The Attack Router
        if new_ports:
            # If new ports opened, we instantly escalate from Pulse to Interrogation
            print(f"[!] [ESCALATION] New surface detected. Triggering Deep Interrogation.")
            deep_scan = execute_kamui_scan(target_ip, scan_type="interrogation")
            
            # Fire the weapons based on the new surface
            for port in new_ports:
                if port in [80, 443, 8000, 8080, 8443]:
                    fuzz_web_port(target_ip, port)
                elif port == 21:
                    strike_ftp(target_ip, port)
                elif port == 22:
                    strike_ssh(target_ip, port)
                else:
                    print(f"[*] Port {port} opened, no offensive module mapped.")
    else:
        print(f"[-] No open ports found or host is down: {target_ip}")
        
    return f"Scan complete for {target_ip}"