from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
from modules.network.port_scan import scan_target
from modules.offensive.web_fuzzer import fuzz_web_port

def execute_live_scan(engine, target_ip):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[*] [LIVE SCAN] Target: {target_ip} | Time: {now}")
    
    # 1. Engage the sensory input (Nmap)
    ports = scan_target(target_ip)
    
    if ports:
        # 2. Feed to the brain, catch the delta
        new_ports = engine.update_asset_state(target_ip, ports, "static_hash")
        
        # 3. Autonomous Execution: If a web port opened, instantly attack it
        web_ports = [80, 443, 8000, 8080, 8443]
        if new_ports:
            for port in new_ports:
                if port in web_ports:
                    fuzz_web_port(target_ip, port)
    else:
        print(f"[-] No open ports found or host is down: {target_ip}")


def start_scheduler(engine):
    print("[*] Booting Shikigami Autonomous Offensive Engine...")
    scheduler = BlockingScheduler()
    target = "127.0.0.1" 
    scheduler.add_job(execute_live_scan, 'interval', seconds=30, args=[engine, target], next_run_time=datetime.now())
    
    try:
        print(f"[*] Engine is ARMED. Monitoring {target}. Press Ctrl+C to stop.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[*] Shutting down Shikigami...")