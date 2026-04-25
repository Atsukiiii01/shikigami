from workers.celery_app import app
from core.database import ShikigamiCore
from modules.network.port_scan import scan_target
from modules.offensive.web_fuzzer import fuzz_web_port
from modules.offensive.infra_strike import strike_ftp, strike_ssh

db_engine = ShikigamiCore("data/shikigami_state.db")

@app.task(name="tasks.execute_live_scan")
def execute_live_scan(target_ip):
    print(f"[*] [CELERY WORKER] Initiating scan on Target: {target_ip}")
    
    ports = scan_target(target_ip)
    
    if ports:
        new_ports = db_engine.update_asset_state(target_ip, ports, "static_hash")
        
        if new_ports:
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